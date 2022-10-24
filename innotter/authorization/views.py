from datetime import datetime, timedelta, timezone

import dotenv
import jwt
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from user.models import User
from .serializers import TokenRefreshSerializer, TokenVerifySerializer, ObtainTokensSerializer


config = dotenv.dotenv_values(".env")
SECRET_KEY = config["JWT_SECRET_KEY"]
SIGNING_METHOD = config["SIGNING_METHOD"]
ACCESS_TOKEN_LIFE_TIME = config["ACCESS_TOKEN_LIFE_TIME"]
REFRESH_TOKEN_LIFE_TIME = config["REFRESH_TOKEN_LIFE_TIME"]


class ObtainTokens(APIView):
    """
    Take user's credentials. If the serialized creds are valid, return access and refresh tokens.
    """
    serializer_class = ObtainTokensSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user_id = request.user.id

            access_token = get_access_token(user_id)

            refresh_payload = {"user_id": user_id,
                               "iss": "innotter",
                               "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=int(REFRESH_TOKEN_LIFE_TIME))}
            refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=SIGNING_METHOD)

            User.objects.filter(pk=user_id).update(refresh_token=refresh_token)

            data = {'info': '', 'access': access_token, 'refresh': refresh_token}
            status = HTTP_200_OK
        else:
            data = {'info': 'Invalid data', 'access': '', 'refresh': ''}
            status = HTTP_400_BAD_REQUEST

        return Response(data, status=status)


class TokenRefresh(APIView):
    """
    Take refresh token. If the given serialized token is valid, return valid access token.
    """
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        user_id = request.user.id

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh_token']
            _, status = token_verify(refresh_token)
            if status == HTTP_200_OK:
                access_token = get_access_token(user_id)
                data = {'info': '', 'access': access_token}
                status = HTTP_200_OK
            else:
                data = {'info': 'Invalid token', 'access': ''}
                status = HTTP_400_BAD_REQUEST
        else:
            data = {'info': 'Invalid data', 'access': ''}
            status = HTTP_400_BAD_REQUEST

        return Response(data, status=status)


class TokenVerify(APIView):
    """
    Take access token. Return whether the serialized token is valid or not.
    """
    serializer_class = TokenVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['access_token']
            data, status = token_verify(refresh_token)

        else:
            data = {'info': 'Invalid data'}
            status = HTTP_400_BAD_REQUEST

        return Response(data, status=status)


def get_access_token(user_id):
    """
    Take user id as payload and create valid access token.
    :param user_id: integer value, represents id of user.
    :return: valid access token.
    """
    access_payload = {"user_id": user_id,
                      "iss": "innotter",
                      "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=int(ACCESS_TOKEN_LIFE_TIME))}
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=SIGNING_METHOD)

    return access_token


def token_verify(token):
    """
    Verify whether the given token is valid or not.
    :param token: either access or refresh token.
    :return: data corresponding to the token.
    """
    if token:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[SIGNING_METHOD])

            data = {'info': 'Token is valid'}
            status = HTTP_200_OK
        except jwt.ExpiredSignatureError:
            data = {'info': 'Authentication token has expired'}
            status = HTTP_401_UNAUTHORIZED
        except (jwt.DecodeError, jwt.InvalidTokenError):
            data = {'info': 'Authentication has failed. Please send valid token'}
            status = HTTP_401_UNAUTHORIZED

    else:
        data = {'info': 'Authorization not found. Please send valid token in headers'}
        status = HTTP_400_BAD_REQUEST

    return data, status
