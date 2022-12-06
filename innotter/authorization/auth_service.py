from datetime import datetime, timedelta, timezone

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import jwt
from rest_framework import status

from user.models import User


JWT_SECRET_KEY = settings.JWT_SECRET_KEY
SIGNING_METHOD = settings.SIGNING_METHOD


class AuthService:
    @staticmethod
    def signup_user(username: str, password: str, email: str) -> None:
        """
        Validate serialized data, take user's creds from it, create a new user and save it
        :param username: given username
        :param password: given password
        :param email: given email
        :return: None.
        """
        user = User.objects.create_user(username=username, password=password, email=email)
        user.full_clean()
        user.save()

    @staticmethod
    def get_user_token(user_id: int, ttl: int) -> str:
        """
        Take user id as a component of payload and time-to-live component to specify created token
        :param user_id: integer value, represents id of user
        :param ttl: time-to-live integer value, represents token that will be created (access or refresh)
        :return: valid token.
        """
        payload = {"user_id": user_id,
                   "iss": "innotter",
                   "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=ttl)}
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=SIGNING_METHOD)

        return token

    @staticmethod
    def verify_user_token(token: str) -> tuple[dict[str], int, User | None]:
        """
        Verify whether the given token is valid or not
        :param token: either access or refresh token
        :return: data corresponding to the token.
        """
        user = None
        if token:
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[SIGNING_METHOD])
                user = User.objects.get(pk=payload['user_id'])

                data = {'msg': 'Token is valid'}
                status_code = status.HTTP_200_OK
            except jwt.ExpiredSignatureError:
                data = {'msg': 'Authentication token has expired'}
                status_code = status.HTTP_401_UNAUTHORIZED
            except (jwt.DecodeError, jwt.InvalidTokenError):
                data = {'msg': 'Authentication has failed. Please send valid token'}
                status_code = status.HTTP_401_UNAUTHORIZED
            except ObjectDoesNotExist:
                data = {'msg': 'Authentication has failed. The user does not exist'}
                status_code = status.HTTP_401_UNAUTHORIZED

        else:
            data = {'msg': 'Authorization not found. Please send valid token in headers'}
            status_code = status.HTTP_400_BAD_REQUEST

        return data, status_code, user
