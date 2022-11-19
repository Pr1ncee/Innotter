from django.db import IntegrityError
from django.conf import settings
from rest_framework import status

from .auth_service import AuthService
from user.models import User


ACCESS_TOKEN_LIFE_TIME = settings.ACCESS_TOKEN_LIFE_TIME
REFRESH_TOKEN_LIFE_TIME = settings.REFRESH_TOKEN_LIFE_TIME


def refresh_user_token(refresh_token: str, user_id: int) -> tuple[dict[str, str], int]:
    """
    Take refresh token from serialized data, verify it and return access token
    :param refresh_token: refresh token sent from client
    :param user_id: id of user, which make request
    :return: generated valid access token.
    """
    _, status_code, _ = AuthService.verify_user_token(refresh_token)
    if status_code == status.HTTP_200_OK:
        access_token = AuthService.get_user_token(user_id, ACCESS_TOKEN_LIFE_TIME)
        data = {'msg': '', 'access_token': access_token, 'refresh_token': refresh_token}
        status_code = status.HTTP_200_OK
    else:
        data = {'msg': 'Invalid token', 'access_token': '', 'refresh_token': ''}
        status_code = status.HTTP_400_BAD_REQUEST

    return data, status_code


def obtain_tokens(user_id: int) -> dict[str, str]:
    """
    Validate serialized data.
    If successfully generate both access and refresh tokens and update user's 'refresh_token' field as well
    :param user_id: id of user that sent request
    :return: dictionary with both access and refresh tokens.
    """
    access_token = AuthService.get_user_token(user_id, ACCESS_TOKEN_LIFE_TIME)
    refresh_token = AuthService.get_user_token(user_id, REFRESH_TOKEN_LIFE_TIME)

    User.objects.filter(pk=user_id).update(refresh_token=refresh_token)

    data = {'access_token': access_token, 'refresh_token': refresh_token}
    return data


def signup_user(username: str, password: str, email: str) -> tuple[dict[str], int]:
    """
    Sign user up using custom AuthService
    :param username: user's username
    :param password: user's password
    :param email: user's email
    :return: information of creating the user.
    """
    try:
        AuthService.signup_user(username, password, email)
        msg = {'msg': 'The user was successfully created'}
        status_code = status.HTTP_201_CREATED
    except IntegrityError:
        msg = {'msg': 'The username has been already taken'}
        status_code = status.HTTP_400_BAD_REQUEST
    return msg, status_code
