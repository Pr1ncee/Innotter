from typing import Any

from django.db import models
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.request import Request

from posts.serializers import CreateListUpdatePageSerializer, ManagerPageSerializer, ManagerPostSerializer
from posts.models import Page, Post
from user.models import User


def page_create(request: Request, serializer: CreateListUpdatePageSerializer) -> None:
    """
    Validate given data, create new page and save it.
    :param request: sent request from client.
    :param serializer: deserialized data.
    :return: None.
    """
    user = User.objects.get(pk=request.user.id)

    serializer.is_valid(raise_exception=True)
    serializer.validated_data['owner'] = user
    tags = serializer.validated_data.pop('tags')

    new_page = Page.objects.create(**serializer.validated_data)
    new_page.tags.set(tags)
    perform_save(new_page)


def page_update(serializer: CreateListUpdatePageSerializer, instance: Page) -> None:
    """
    Validate given data, update and save it.
    :param serializer: deserialized data.
    :param instance: page to be updated.
    :return: None.
    """
    serializer.is_valid(raise_exception=True)

    # Get list of tags and loop through the list, 'cause user is able to send several tags to add.
    tags_list = serializer.validated_data.pop('tags', False)
    if tags_list:
        [instance.tags.add(tag) for tag in tags_list]

    serializer.save()


def page_delete(instance: models.Model) -> None:
    """
    Delete a recording.
    :param instance: any Model object.
    :return: None.
    """
    instance.delete()


def page_follow(request: Request, instance: Page) -> dict[str]:
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


def page_response_follow_request(instance: Page, mode: str) -> Page:
    """
    Provide page's owner to accept or deny follow request.
    :param instance: page request was sent to.
    :param mode: implements two actions: 'accept' and 'deny'.
    :return: None.
    """
    user_to_response = instance.follow_requests.last()
    if user_to_response:
        match mode:
            case 'accept':
                # Take user from 'follow_requests' and put it into 'followers'
                instance.follow_requests.remove(user_to_response)
                instance.followers.add(user_to_response)
            case 'deny':
                # Otherwise remove from 'follow_requests'
                instance.follow_requests.remove(user_to_response)

        perform_save(instance)
        return instance


def page_destroy_tag(instance: Page) -> Page:
    """
    Take last tag in page's tags and remove it.
    :param instance: page tag to be removed.
    :return: None.
    """
    tag_to_delete = instance.tags.last()
    instance.tags.remove(tag_to_delete)

    perform_save(instance)
    return instance


def post_like(request: Request, instance: Post) -> None:
    """
    Get user from request and add post to his 'liked'.
    :param request: request send from client.
    :param instance: post to be liked.
    :return: None.
    """
    user = User.objects.get(pk=request.user.id)
    user.liked.add(instance)
    perform_save(user)


def manager_view(request: Request, given_serializer: ManagerPageSerializer | ManagerPostSerializer,
                 instance: Post | Page,
                 *args: Any, **kwargs: Any) -> tuple[ManagerPageSerializer | ManagerPostSerializer, int]:
    """
    Generalized function for moderating both pages and posts
    :param request: sent request from client
    :param given_serializer: serializer of Page or Post model
    :param instance: Page or Post object. Represents the page or the post is being manipulated.
    :param args: additional args.
    :param kwargs: dictionary, that contains type of update.
    :return: serialized data and corresponding status code.
    """
    partial = kwargs.pop('partial', False)
    status_code = None
    serializer = given_serializer(instance, data=request.data, partial=partial)
    serializer.is_valid()

    match request.method:
        case 'PUT':
            page_update(serializer, instance)
            status_code = HTTP_200_OK
        case 'DELETE':
            page_delete(instance)
            status_code = HTTP_204_NO_CONTENT

    serializer.save()
    return serializer, status_code


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
