from collections import OrderedDict
from typing import BinaryIO

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.request import Request
from rest_framework.test import APIClient
from pytest import fixture

from posts.models import Post, Page, Tag
from posts.services import create_page as posts_create_page
from user.models import User


class Fixtures:
    """
    Implement different fixtures methods
    """
    client = APIClient(enforce_csrf_checks=False)
    file_obj_type = SimpleUploadedFile | BinaryIO
    file_name = 'tests/images/innotter_avatar_2.jpg'
    tags = ['Tag 1']

    @fixture
    def get_file(self):
        """
        Open given file and using file uploader 'SimpleUploadedFile' to make file object
        :return: file object.
        """
        with open(self.file_name, 'rb') as image_obj:
            file_obj = SimpleUploadedFile(self.file_name, image_obj.read())
        return file_obj

    @fixture
    def post_factory(self, db):
        def create_post(page_id: int) -> Post:
            """
            Create the post and return its instance
            :param page_id: id of page
            :return: Post instance
            """
            new_page = Post.objects.create(title='Test post', content='Test content', page_id=page_id)
            new_page.save()
            return new_page

        return create_post

    @fixture
    def create_page_factory(self, db, signup_user):
        user = User.objects.all()[0]

        def create_page(tags: list | tuple = tuple(), is_private: bool = True) -> Page:
            """
            Create the page and return it
            :param tags: list of page's tags
            :param is_private: whether the page will be private or not
            :return: created object
            """
            data = OrderedDict([('name', 'Test page'),
                                ('uuid', 'testuuid'),
                                ('description', 'Test description'),
                                ('is_private', is_private),
                                ('owner', user)])
            pk = posts_create_page(data, tags)
            return Page.objects.get(pk=pk)

        return create_page

    @fixture
    def follow_page_factory(self, db, tokens_factory):
        def follow_page(page_id: int, user_id: int) -> Request:
            """
            Follow the page and return the request
            :param page_id: page to follow
            :param user_id: user id to get jwt token
            :return: result request of following.
            """
            access_token = tokens_factory(user_id)['access_token']
            self.client.credentials(HTTP_AUTHORIZATION=access_token)
            request = self.client.put(f'/api/v1/pages/{page_id}/')
            return request

        return follow_page

    @fixture
    def create_tags(self, db):
        [Tag.objects.create(name=tag) for tag in self.tags]
        return Tag.objects.all()
