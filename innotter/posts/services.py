from collections import OrderedDict
from typing import Any

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Model
from rest_framework.request import Request

from .custom_storage import MediaStorage
from .mods import Mode
from posts.models import Page, Post
from .tasks import send_new_post_notification_email
from user.models import User


def save_image(file_obj: InMemoryUploadedFile) -> str:
    """
    If given file_object
    :param file_obj:
    :return:
    """
    if file_obj:
        file_obj_type = file_obj.content_type.split('/')[0]
        if file_obj_type == 'image':
            remote_storage = MediaStorage()
            remote_storage.save(file_obj.name, file_obj)
            file_url = remote_storage.url(file_obj.name)
            return file_url


def create_page(data: OrderedDict, tags: list, file_obj: InMemoryUploadedFile) -> None:
    """
    Validate given data, create new page and save it.
    :param data: dictionary with data to create.
    :param tags: tags to add to the page.
    :param file_obj: file object of image type to be saved at AWS S3.
    :return: None.
    """
    file_url = save_image(file_obj)
    data['image'] = file_url

    new_page = Page.objects.create(**data)
    new_page.tags.set(tags)

    perform_save(new_page)


def update_page(tags_list: list, file_obj: InMemoryUploadedFile, instance: Page) -> None:
    """
    Validate given data, update and save it.
    Get list of tags and loop through the list, 'cause user is able to send several tags to add.
    :param tags_list: list of tags to update.
    :param file_obj: file object of image type to be saved at AWS S3.
    :param instance: page to be updated.
    :return: None.
    """
    file_url = save_image(file_obj)
    if file_url:
        instance.image = file_url
    if tags_list:
        [instance.tags.add(tag) for tag in tags_list]


def delete_object(instance: Model) -> None:
    """
    Delete a recording.
    :param instance: any Model object.
    :return: None.
    """
    instance.delete()


def follow_page(request: Request, instance: Page) -> dict[str]:
    """
    Follow page or send follow request based on page's and user's current state.
    :param request: send request from client.
    :param instance: page to be followed.
    :return: dictionary with the one value, which represents result of the following action.
    :return: None.
    """
    # If page is private and user doesn't follow it yet.
    if instance.is_private and (request.user not in instance.followers.all()):
        instance.follow_requests.add(request.user)
        msg = 'Follow request sent!'
    else:
        instance.followers.add(request.user)
        msg = 'You are following the page now!'
    perform_save(instance)

    return {'info': msg}


def response_page_follow_request(instance: Page, mode: Mode) -> Page:
    """
    Provide page's owner to accept or deny follow request.
    :param instance: page request was sent to.
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
            case Mode.DENY:
                # Otherwise remove from 'follow_requests'.
                instance.follow_requests.remove(user_to_response)

        perform_save(instance)
        return instance


def destroy_page_tag(instance: Page) -> Page:
    """
    Take last tag in page's tags and remove it.
    :param instance: page tag to be removed.
    :return: None.
    """
    tag_to_delete = instance.tags.last()
    instance.tags.remove(tag_to_delete)

    perform_save(instance)
    return instance


def like_post(request: Request, instance: Post) -> None:
    """
    Get user from request and add post to his 'liked'.
    :param request: request sent from client.
    :param instance: post to be liked.
    :return: None.
    """
    user = User.objects.get(pk=request.user.id)
    user.liked.add(instance)
    perform_save(user)


def send_email(request: Request, post: str) -> str:
    """
    Get necessary data from request, send notification email and return result information.
    :param request: request sent from client.
    :param post: created post name.
    :return: result information of sending email.
    """
    user = request.user
    page_id = request.data['page']
    page = Page.objects.get(pk=page_id)
    recipient_list = [email for email in page.followers.values_list('email', flat=True)]
    subject = f"Have a look at a new post from {user}!"
    message = f"{user} just have created '{post}' post at {page} page! Let's check in!"

    result = send_new_post_notification_email(subject, message, recipient_list)
    return result


def perform_save(obj: Any) -> None:
    """
    Take object and call both 'full_clean' and 'save' methods.
    Full clean method validates data to be saved.
    Save method saves data
    :param obj: any object, that has both 'full_clean' and 'save' methods.
    :return: None.
    """
    obj.full_clean()
    obj.save()
