from collections import OrderedDict
from typing import BinaryIO

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APIClient
from pytest import fixture

from posts.enum_objects import Mode, Directory
from posts.models import Tag, Page, Post
from posts.services import save_image, update_page, response_page_follow_request, delete_object, like_post,\
                           create_page as posts_create_page, send_email
from user.models import User


class Fixtures:
    """
    Implement different fixtures methods
    """
    client = APIClient(enforce_csrf_checks=False)
    file_obj_type = SimpleUploadedFile | BinaryIO
    file_name = 'tests/innotter_avatar_2.jpg'
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
    def create_post(self, db):
        def _create_post(page_id: int) -> Post:
            """
            Create the post and return its instance
            :param page_id: id of page
            :return: Post instance
            """
            new_page = Post.objects.create(title='Test post', content='Test content', page_id=page_id)
            new_page.save()
            return new_page

        return _create_post

    @fixture
    def create_page(self, db, signup_user):
        user = User.objects.all()[0]

        def _create_page(tags: list | tuple = tuple(), is_private: bool = True) -> Page:
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

        return _create_page

    @fixture
    def follow_page(self, db, obtain_tokens):
        def _follow_page(page_id: int, user_id: int) -> Request:
            """
            Follow the page and return the request
            :param page_id: page to follow
            :param user_id: user id to get jwt token
            :return: result request of following.
            """
            access_token = obtain_tokens(user_id)['access_token']
            self.client.credentials(HTTP_AUTHORIZATION=access_token)
            request = self.client.put(f'/api/v1/pages/{page_id}/')
            return request

        return _follow_page

    @fixture
    def create_tags(self, db):
        [Tag.objects.create(name=tag) for tag in self.tags]
        return self.tags


class TestPage(Fixtures):
    """
    Testing actions with page object
    """
    def test_save_image(self, get_file, mocker):
        mocker.patch("posts.services.S3Client.create_presigned_url", return_value=True)

        result = save_image(get_file, Directory.PAGES)
        assert result

    def test_create_page(self, signup_user, create_tags, create_page):
        page = create_page()
        assert page

    def test_update_page(self, signup_user, create_tags, create_page):
        page = create_page()
        tag_list = [Tag.objects.all()[0]]
        update_page(tag_list, None, page, None)
        page.save()
        assert page.tags.all()

    def test_follow_page(self, signup_user, create_page, follow_page, obtain_tokens):
        user = User.objects.all()[0]
        page = create_page()
        request = follow_page(page.id, user.id)
        assert request.status_code == status.HTTP_200_OK and page.follow_requests.all()

    def test_response_follow_request(self, signup_user, create_page, follow_page, obtain_tokens):
        user = User.objects.all()[0]
        page = create_page()
        request = follow_page(page.id, user.id)
        assert request.status_code == status.HTTP_200_OK

        response_page_follow_request(page, Mode.ACCEPT)
        assert page.followers.all()

    def test_delete_page(self, signup_user, create_page):
        page = create_page()
        delete_object(page)
        assert not Page.objects.all()


class TestPost(Fixtures):
    """
    Testing actions with post object
    """
    def test_like_post(self, signup_user, create_page, create_post, obtain_tokens):
        user = User.objects.all()[0]
        access_token = obtain_tokens(user.id)['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=access_token)

        page = create_page(is_private=False)
        post = create_post(page.id)
        request = self.client.put(f'/api/v1/posts/{post.id}/')
        assert request.status_code == status.HTTP_200_OK and post.liked_by.all()

    def test_send_email(self, signup_user, create_page, follow_page, mocker):
        expected = 'The email(s) were successfully sent.'
        mocker.patch("posts.services.send_new_post_notification_email",
                     return_value='The email(s) were successfully sent.')

        user = User.objects.all()[0]
        page = create_page(is_private=False)

        request = follow_page(page.id, user.id)
        request.user = user
        request.data['page'] = page.id
        assert request.status_code == status.HTTP_200_OK

        result = send_email(request, 'Test post')
        assert result == expected
