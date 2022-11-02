from datetime import datetime, timedelta, timezone

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import jwt
from rest_framework import status

from .serializers import RegisterSerializer
from user.models import User


JWT_SECRET_KEY = settings.JWT_SECRET_KEY
SIGNING_METHOD = settings.SIGNING_METHOD


class AuthService:
    @staticmethod
    def user_signup(serializer: RegisterSerializer) -> None:
        """
        Validate serialized data, take user's creds from it, create a new user and save it.
        :param serializer: provide deserialized data from client.
        :return: None.
        """
        serializer.is_valid(raise_exception=True)
        username, password, email = serializer.validated_data['username'], \
                                    serializer.validated_data['password'], serializer.validated_data['email']

        user = User.objects.create_user(username=username, password=password, email=email)
        user.full_clean()
        user.save()

    @staticmethod
    def user_get_token(user_id: int, ttl: int) -> str:
        """
        Take user id as a component of payload and time-to-live component to specify created token.
        :param user_id: integer value, represents id of user
        :param ttl: time-to-live integer value, represents token that will be created (access or refresh).
        :return: valid token
        """
        payload = {"user_id": user_id,
                   "iss": "innotter",
                   "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=ttl)}
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=SIGNING_METHOD)

        return token

    @staticmethod
    def user_token_verify(token: str) -> tuple[dict[str], int, User | None]:
        """
        Verify whether the given token is valid or not.
        :param token: either access or refresh token.
        :return: data corresponding to the token.
        """
        user = None
        if token:
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[SIGNING_METHOD])
                user = User.objects.get(pk=payload['user_id'])

                data = {'info': 'Token is valid'}
                status_code = status.HTTP_200_OK
            except jwt.ExpiredSignatureError:
                data = {'info': 'Authentication token has expired'}
                status_code = status.HTTP_401_UNAUTHORIZED
            except (jwt.DecodeError, jwt.InvalidTokenError):
                data = {'info': 'Authentication has failed. Please send valid token'}
                status_code = status.HTTP_401_UNAUTHORIZED
            except ObjectDoesNotExist:
                data = {'info': 'Authentication has failed. The user does not exist'}
                status_code = status.HTTP_401_UNAUTHORIZED

        else:
            data = {'info': 'Authorization not found. Please send valid token in headers'}
            status_code = status.HTTP_400_BAD_REQUEST

        return data, status_code, user
