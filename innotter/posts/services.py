from collections import OrderedDict
from typing import Any

from botocore.exceptions import ClientError
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Model
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer

from .aws.s3_client import S3Client
from .enum_objects import (
    Mode,
    Directory,
    PostMethods,
    PageMethods
)
from innotter.posts.pika.producer import PikaClient
from posts.models import Page, Post
from .tasks import send_new_post_notification_email
from user.models import User


bucket_name = settings.AWS_STORAGE_BUCKET_NAME
routing_key_stats = settings.RABBITMQ_STATS_ROUTING_KEY
pika = PikaClient
s3 = S3Client


def save_image(file_obj: InMemoryUploadedFile, upload_dir: Directory) -> str | None:
    """
    Validate given file object, if it's image, save it at AWS S3
    :param file_obj: given file from client
    :param upload_dir: specified directory that stores file objects
    :return: if succeeded return url to image at the remote storage.
    """
    try:
        upload_path = s3.upload_path(file_obj.name, [str(upload_dir.value)])
        s3.upload_fileobj(file_obj, bucket_name, upload_path)
        presigned_url = s3.create_presigned_url(bucket_name, upload_path)
        return presigned_url
    except ClientError:
        pass


def publish_page(page: Page, method: PageMethods, pk: int | None = None) -> None:
    """
    Prepare data sent from client and send it to the RabbitMQ exchange according to the given routing key
    :param page: page object, a raw data
    :param method: method type
    :param pk: page id
    :return: None
    """
    data = {}
    # If method DELETE no need for extra data processing
    if method == PageMethods.DELETE:
        data['id'] = page.id if page.id else pk
    else:
        data.update({
            'id': page.id,
            'owner_id': page.owner.id,
            'name': page.name,
            'uuid': page.uuid,
            'followers': page.followers.all().count(),
            'posts': page.posts.all().count(),
            'unblock_date': page.unblock_date}
        )
    pika.routing_key(routing_key_stats)
    pika.publish(method, data)


def publish_post(post: OrderedDict | Post, method: PostMethods,
                 pk: int = None, liked_by: int = 0) -> None:
    """
    Prepare data sent from client end send it to the RabbitMQ exchange according to the given routing key
    :param post: post model or dict, in other words just a raw data
    :param method: method type
    :param pk: post id
    :param liked_by: number of likes
    :return: None.
    """
    # if method is DELETE, the data argument is pk, therefore no need extra data processing
    match method:
        case PostMethods.DELETE | PostMethods.LIKE:
            data = post
        case _:
            try:
                data = {
                    'id': getattr(post, 'id'),
                    'page': getattr(post, 'page_id').id,
                    'title': getattr(post, 'title'),
                    'content': getattr(post, 'content'),
                    'reply_to': reply.id if (reply := getattr(post, 'reply_to')) else reply,
                    'liked_by': getattr(post, 'liked_by').count()
                }
            except AttributeError:
                data = {
                    'id': pk,
                    'page': post.get('page').id,
                    'title': post.get('title', ' '),
                    'content': post.get('content', ' '),
                    'reply_to': reply.id if (reply := post.get('reply_to', None)) else reply,
                    'liked_by': liked_by
                }
    pika.routing_key(routing_key_stats)
    pika.publish(method, data)


def create_page(data: OrderedDict, tags: list, file_url: str | None = None) -> int:
    """
    Validate given data, create new page and save it
    :param data: dictionary with data to create
    :param tags: tags to add to the page
    :param file_url: path to saved image.
    :return: id of created page.
    """
    data['image'] = file_url
    new_page = Page.objects.create(**data)
    new_page.tags.set(tags)

    perform_save(new_page)
    publish_page(new_page, PageMethods.CREATE)
    return new_page.id


def update_page(tags_list: list,
                file_obj: InMemoryUploadedFile,
                instance: Page,
                upload_dir: Directory,
                serializer: ModelSerializer = None) -> None:
    """
    Validate given data, update and save it.
    Get list of tags and loop through the list, 'cause user is able to send several tags to add
    :param tags_list: list of tags to update
    :param file_obj: file object of any type(should be an image) to be saved at AWS S3
    :param instance: page to be updated
    :param upload_dir: specified directory that stores file objects
    :param serializer: serializer to be saved
    :return: None.
    """
    if file_obj:
        file_url = save_image(file_obj, upload_dir)
        if file_url:
            instance.image = file_url
    if tags_list:
        [instance.tags.add(tag) for tag in tags_list]
    perform_save(serializer, fc=False)
    publish_page(instance, PageMethods.UPDATE)


def delete_object(instance: Model,
                  serializer: ModelSerializer | None = None,
                  pk: int | None = None, is_post: bool | None = None) -> None:
    """
    Delete a recording
    :param instance: any Model object
    :param serializer: any serializer to save
    :param pk: object id to be deleted
    :param is_post: pass
    :return: None.
    """
    instance.delete()
    if serializer:
        perform_save(serializer, fc=False)

    data = {'id': pk}
    publish_post(data, PostMethods.DELETE) if is_post else publish_page(instance, PageMethods.DELETE, pk=pk)


def follow_page(request: Request, instance: Page) -> dict[str]:
    """
    Follow page or send follow request based on page's and user's current statereturn_value
    :param request: send request from client
    :param instance: page to be followed.
    :return: dictionary with the one value, that represents result of the following action.
    """
    # If page is private and user doesn't follow it yet.
    if instance.is_private and (request.user not in instance.followers.all()):
        instance.follow_requests.add(request.user)
        msg = 'Follow request sent!'
    else:
        instance.followers.add(request.user)
        publish_page(instance, PageMethods.UPDATE)
        msg = 'You are following the page now!'
    perform_save(instance)

    return {'msg': msg}


def response_page_follow_request(instance: Page, mode: Mode) -> Page:
    """
    Provide page's owner to accept or deny follow request
    :param instance: page request was sent to
    :param mode: represents two actions: 'accept' and 'deny'.
    :return: None.
    """
    user_to_response = instance.follow_requests.last()
    if user_to_response:
        match mode:
            case Mode.ACCEPT:
                # Take user from 'follow_requests' and put it into 'followers'.
                instance.follow_requests.remove(user_to_response)
                instance.followers.add(user_to_response)
                publish_page(instance, PageMethods.UPDATE)
            case Mode.DENY:
                # Otherwise remove from 'follow_requests'.
                instance.follow_requests.remove(user_to_response)

        perform_save(instance)
        return instance


def destroy_page_tag(instance: Page) -> Page:
    """
    Take last tag in page's tags and remove it
    :param instance: page tag to be removed.
    :return: None.
    """
    tag_to_delete = instance.tags.last()
    instance.tags.remove(tag_to_delete)

    perform_save(instance)
    return instance


def like_post(request: Request, instance: Post) -> None:
    """
    Get user from request and add post to his 'liked'
    :param request: request sent from client
    :param instance: post to be liked.
    :return: None.
    """
    user = User.objects.get(pk=request.user.id)
    user.liked.add(instance)
    perform_save(user)
    data = {'id': instance.id, 'liked_by': user.id}
    publish_post(data, PostMethods.LIKE)


def send_email(request: Request, serializer: ModelSerializer) -> str:
    """
    Get necessary data from request, send notification email and return result information.
    :param request: request sent from client
    :param serializer: object of a Post model
    :return: result information of sending email.
    """
    perform_save(serializer, fc=False)
    post = serializer.validated_data
    post_title = post.get('title', ' ')
    page_id = request.data['page']
    page = Page.objects.get(pk=page_id)
    post_id = page.posts.order_by('-id')[0].id
    user = request.user
    recipient_list = [email for email in page.followers.values_list('email', flat=True)]

    subject = f"Have a look at a new post from {user}!"
    body = f"{user} just have created '{post_title}' post at {page} page! Let's check in!"

    result = send_new_post_notification_email(subject, body, recipient_list)
    publish_post(post, PostMethods.CREATE, pk=post_id, liked_by=0)
    return result


def perform_save(obj: Any, fc: bool = True) -> None:
    """
    Take object and call both 'full_clean' and 'save' methods.
    Full clean method validates data to be saved.
    Save method saves data
    :param obj: any object, that has 'save' method
    :param fc: bool flag whether to do full clean or not
    :return: None.
    """
    if fc:
        obj.full_clean()
    obj.save()
