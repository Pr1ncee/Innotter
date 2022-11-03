from collections import OrderedDict
from typing import Any

from django.db.models import Model
from rest_framework.request import Request

from posts.models import Page, Post
from user.models import User


def create_page(data: OrderedDict, tags: list) -> None:
    """
    Validate given data, create new page and save it.
    :param data: dictionary with data to create.
    :param tags: tags to add to the page.
    :return: None.
    """
    new_page = Page.objects.create(**data)
    new_page.tags.set(tags)
    perform_save(new_page)


def update_page(tags_list: list, instance: Page) -> None:
    """
    Validate given data, update and save it.
    Get list of tags and loop through the list, 'cause user is able to send several tags to add.
    :param tags_list: list of tags to update.
    :param instance: page to be updated.
    :return: None.
    """
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


def response_page_follow_request(instance: Page, mode: str) -> Page:
    """
    Provide page's owner to accept or deny follow request.
    :param instance: page request was sent to.
    :param mode: represents two actions: 'accept' and 'deny'.
    :return: None.
    """
    user_to_response = instance.follow_requests.last()
    if user_to_response:
        match mode:
            case 'accept':
                # Take user from 'follow_requests' and put it into 'followers'.
                instance.follow_requests.remove(user_to_response)
                instance.followers.add(user_to_response)
            case 'deny':
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
    :param request: request send from client.
    :param instance: post to be liked.
    :return: None.
    """
    user = User.objects.get(pk=request.user.id)
    user.liked.add(instance)
    perform_save(user)


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
