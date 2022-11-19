from rest_framework import status

from tests.fixtures import Fixtures
from posts.enum_objects import Mode, Directory
from posts.models import Tag, Page
from posts.services import save_image, update_page, response_page_follow_request, delete_object, like_post,\
                                send_email
from user.models import User


class TestPage(Fixtures):
    """
    Testing actions with page object
    """
    def test_save_image(self, get_file, mocker):
        mocker.patch("posts.services.S3Client.create_presigned_url", return_value=True)

        result = save_image(get_file, Directory.PAGES)
        assert result

    def test_create_page(self, signup_user, create_page_factory):
        page = create_page_factory()
        assert page

    def test_update_page(self, signup_user, create_tags, create_page_factory):
        page = create_page_factory()
        tag_list = create_tags
        update_page(tag_list, None, page, None)
        page.save()
        assert page.tags.all()

    def test_follow_page(self, signup_user, create_page_factory, follow_page_factory, tokens_factory):
        user = User.objects.all()[0]
        page = create_page_factory()
        request = follow_page_factory(page.id, user.id)
        assert request.status_code == status.HTTP_200_OK and page.follow_requests.all()

    def test_response_follow_request(self, signup_user, create_page_factory, follow_page_factory, tokens_factory):
        user = User.objects.all()[0]
        page = create_page_factory()
        request = follow_page_factory(page.id, user.id)
        assert request.status_code == status.HTTP_200_OK

        response_page_follow_request(page, Mode.ACCEPT)
        assert page.followers.all()

    def test_delete_page(self, signup_user, create_page_factory):
        page = create_page_factory()
        delete_object(page)
        assert not Page.objects.all()


class TestPost(Fixtures):
    """
    Testing actions with post object
    """
    def test_like_post(self, signup_user, create_page_factory, post_factory, tokens_factory):
        user = User.objects.all()[0]
        access_token = tokens_factory(user.id)['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=access_token)

        page = create_page_factory(is_private=False)
        post = post_factory(page.id)
        request = self.client.put(f'/api/v1/posts/{post.id}/')
        assert request.status_code == status.HTTP_200_OK and post.liked_by.all()

    def test_send_email(self, signup_user, create_page_factory, follow_page_factory, mocker):
        expected = 'The email(s) were successfully sent.'
        mocker.patch("posts.services.send_new_post_notification_email",
                     return_value='The email(s) were successfully sent.')

        user = User.objects.all()[0]
        page = create_page_factory(is_private=False)

        request = follow_page_factory(page.id, user.id)
        request.user = user
        request.data['page'] = page.id
        assert request.status_code == status.HTTP_200_OK

        result = send_email(request, 'Test post')
        assert result == expected
