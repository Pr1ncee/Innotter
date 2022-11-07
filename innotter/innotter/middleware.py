from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from authorization.auth_service import AuthService
from user.models import User


class CustomJWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest) -> None:
        """
        Try to authenticate user.
        :param request: sent request from client.
        :return: None.
        """
        request.user = SimpleLazyObject(lambda: self.__class__.get_user_jwt(request))

    @staticmethod
    def get_user_jwt(request: WSGIRequest) -> AnonymousUser | User:
        """
        Try to get user from request, if succeeded process further to the server.
        Otherwise, get jwt and process further to the server as well
        :param request: sent request from client.
        :return: either authenticated or anonymous user.
        """
        user_jwt = get_user(request)
        if user_jwt.is_authenticated:
            return user_jwt

        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token:
            _, _, user_jwt = AuthService.verify_user_token(token)

        return user_jwt
