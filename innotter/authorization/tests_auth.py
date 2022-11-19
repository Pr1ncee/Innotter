from rest_framework import status

from authorization.services import refresh_user_token
from user.models import User


class TestAuthentication:
    def test_signing_user_up(self, signup_user):
        result, status_code = signup_user
        created_result = 'The user was successfully created'
        assert result['msg'] == created_result and status_code == status.HTTP_201_CREATED

    def test_obtaining_tokens(self, tokens_factory, signup_user):
        user = User.objects.all()[0]
        tokens = tokens_factory(user.id)
        assert tokens['access_token'] and tokens['refresh_token']

    def test_refresh_token(self, tokens_factory, signup_user):
        user = User.objects.all()[0]
        refresh_token = tokens_factory(user.id)['refresh_token']
        result, status_code = refresh_user_token(refresh_token, user.id)
        assert result['access_token'] and result['refresh_token'] and status_code == status.HTTP_200_OK
