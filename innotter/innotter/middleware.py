from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from authorization.auth_service import AuthService
from user.models import User


class CustomJWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request: WSGIRequest) -> None:
        request.user = SimpleLazyObject(lambda: self.__class__.get_user_jwt(request))

    @staticmethod
    def get_user_jwt(request: WSGIRequest) -> AnonymousUser | User:
        user_jwt = get_user(request)
        if user_jwt.is_authenticated:
            return user_jwt

        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token:
            data, status, user_jwt = AuthService.user_token_verify(token)

        return user_jwt
