import logging

import jwt
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Request

from core.auth.auth_service import AuthService
from core.exceptions.base_exceptions import (
    InvalidParamsError,
    AuthenticateError,
    InvalidTokenError,
    NoPermissionError
)
from core.settings import settings


logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    """
    Verify whether jwt token is given, validate the token and pass the request further,
    otherwise thrown the exception
    """
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            return self.verifying_creds(request, credentials.credentials)
        else:
            logger.warning('Access denied (Invalid authentication scheme)')
            raise AuthenticateError()

    @classmethod
    def verifying_creds(cls, request: Request, token: str):
        """
        The function to be overridden. Allow a coder to develop a custom user authentication
        :param request:
        :param token: jwt token
        :return: return the given token if valid, otherwise raise HTTPException.
        """
        if not AuthService.verify_user_token(token):
            logger.warning('Access denied (The token is invalid)')
            raise InvalidTokenError()
        return token


class IsUserOwner(JWTBearer):
    @classmethod
    def verifying_creds(cls, request: Request, token: str):
        """
        Verify the given token and additionally check out whether the user owns requested profile
        :param token: jwt token
        :param request: request from client
        :return: return the given token is valid and the requested user is the page's owner,
                 otherwise throw HTTPException.
        """
        if not AuthService.verify_user_token(token):
            logger.warning('Access denied (The token is invalid)')
            raise InvalidTokenError()

        try:
            user_id = int(request.get('path_params')['user_id'])
        except ValueError:
            logger.warning('Access denied (The given params are invalid')
            raise InvalidParamsError()
        else:
            user_id_from_token = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_SIGNING_METHOD]
            )['user_id']
            if user_id_from_token != user_id:
                logger.warning('Access denied (The user has no permission to view this page)')
                raise NoPermissionError()
            return token
