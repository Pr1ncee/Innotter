from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth import login, logout
import jwt
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from user.models import User
from .serializers import TokenRefreshSerializer, TokenVerifySerializer, \
                         LoginSerializer, RegisterSerializer, LogoutSerilaizer


JWT_SECRET_KEY = settings.JWT_SECRET_KEY
SIGNING_METHOD = settings.SIGNING_METHOD
ACCESS_TOKEN_LIFE_TIME = settings.ACCESS_TOKEN_LIFE_TIME
REFRESH_TOKEN_LIFE_TIME = settings.REFRESH_TOKEN_LIFE_TIME


class TokenRefresh(APIView):
    """
    Take refresh token. If the given deserialized token is valid, return valid access token.
    """
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        user_id = request.user.id

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data['refresh_token']
        _, status_code = token_verify(refresh_token)
        if status_code == status.HTTP_200_OK:
            access_token = get_token(user_id, ACCESS_TOKEN_LIFE_TIME)
            data = {'info': '', 'access': access_token}
            status_code = status.HTTP_200_OK
        else:
            data = {'info': 'Invalid token', 'access': ''}
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(data, status=status_code)


class TokenVerify(APIView):
    """
    Take access token. Return whether the deserialized token is valid or not.
    """
    serializer_class = TokenVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data['access_token']
        data, status_code = token_verify(refresh_token)

        return Response(data, status=status_code)


class SigninView(APIView):
    """
    Implement user signin, return status=202.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user_id = user.id
        login(request, user)

        access_token = get_token(user_id, ACCESS_TOKEN_LIFE_TIME)
        refresh_token = get_token(user_id, REFRESH_TOKEN_LIFE_TIME)

        User.objects.filter(pk=user_id).update(refresh_token=refresh_token)

        data = {'access_token': access_token, 'refresh_token': refresh_token}

        return Response(data, status=status.HTTP_202_ACCEPTED)


class SignoutView(APIView):
    """
    Implement user signout, return status=204
    """
    serializer_class = LogoutSerilaizer

    def get(self, request):
        logout(request)

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class SignupView(APIView):
    """
    Implement user signup, return status=202.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username, password, email = serializer.validated_data['username'], \
                                    serializer.validated_data['password'], serializer.validated_data['email']
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        return Response(None, status=status.HTTP_201_CREATED)


def get_token(user_id: int, ttl: int) -> str:
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


def token_verify(token: str) -> tuple[dict, int]:
    """
    Verify whether the given token is valid or not.
    :param token: either access or refresh token.
    :return: data corresponding to the token.
    """
    if token:
        try:
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[SIGNING_METHOD])

            data = {'info': 'Token is valid'}
            status_code = status.HTTP_200_OK
        except jwt.ExpiredSignatureError:
            data = {'info': 'Authentication token has expired'}
            status_code = status.HTTP_401_UNAUTHORIZED
        except (jwt.DecodeError, jwt.InvalidTokenError):
            data = {'info': 'Authentication has failed. Please send valid token'}
            status_code = status.HTTP_401_UNAUTHORIZED

    else:
        data = {'info': 'Authorization not found. Please send valid token in headers'}
        status_code = status.HTTP_400_BAD_REQUEST

    return data, status_code
