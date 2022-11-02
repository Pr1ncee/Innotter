from django.contrib.auth import login, logout
from django.conf import settings
from rest_framework import status
from rest_framework.request import Request

from .auth_service import AuthService
from .serializers import TokenRefreshSerializer, TokenVerifySerializer, LoginSerializer, RegisterSerializer
from user.models import User


ACCESS_TOKEN_LIFE_TIME = settings.ACCESS_TOKEN_LIFE_TIME
REFRESH_TOKEN_LIFE_TIME = settings.REFRESH_TOKEN_LIFE_TIME


def user_token_refresh(serializer: TokenRefreshSerializer, user_id: int) -> tuple[dict[str, str], int]:
    """
    Take refresh token from serialized data, verify it and return access token.
    :param serializer: provides deserialized data from client.
    :param user_id: id of user, which make request.
    :return: generated valid access token.
    """
    serializer.is_valid(raise_exception=True)

    refresh_token = serializer.validated_data['refresh_token']
    _, status_code, _ = AuthService.user_token_verify(refresh_token)
    if status_code == status.HTTP_200_OK:
        access_token = AuthService.user_get_token(user_id, ACCESS_TOKEN_LIFE_TIME)
        data = {'info': '', 'access': access_token}
        status_code = status.HTTP_200_OK
    else:
        data = {'info': 'Invalid token', 'access': ''}
        status_code = status.HTTP_400_BAD_REQUEST

    return data, status_code


def user_token_verify(serializer: TokenVerifySerializer) -> tuple[dict[str], int]:
    """
    Take access token and verify it, return result of the verification.
    :param serializer: provides deserialized data from client.
    :return: message of verification action and status code.
    """
    serializer.is_valid(raise_exception=True)

    refresh_token = serializer.validated_data['access_token']
    data, status_code, _ = AuthService.user_token_verify(refresh_token)

    return data, status_code


def user_signin(request: Request, serializer: LoginSerializer) -> dict[str, str]:
    """
    Validate serialized data, try to log user in.
    If successfully generate both access and refresh tokens and update user's 'refresh_token' field as well.
    :param request: request from client.
    :param serializer: deserialized data sent from client.
    :return: dictionary with both access and refresh tokens.
    """
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    login(request, user)

    access_token = AuthService.user_get_token(user.id, ACCESS_TOKEN_LIFE_TIME)
    refresh_token = AuthService.user_get_token(user.id, REFRESH_TOKEN_LIFE_TIME)

    User.objects.filter(pk=user.id).update(refresh_token=refresh_token)

    data = {'access_token': access_token, 'refresh_token': refresh_token}
    return data


def user_signout(request: Request) -> None:
    """
    Log user out using default django function 'logout'.
    :param request: request from client.
    :return: None.
    """
    logout(request)


def user_signup(serializer: RegisterSerializer) -> None:
    """
    Sign user up using custom AuthService.
    :param serializer: deserialized data from client.
    :return: None.
    """
    AuthService.user_signup(serializer)
