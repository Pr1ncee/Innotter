from warnings import warn

from fastapi import status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from starlette.requests import Request

from core.settings import settings
from core.aws.dynamodb_client import DynamoDBClient


db = DynamoDBClient


class AuthService:
    @staticmethod
    def get_user_id_from_token(token: str):
        """
        Get user id from the given token
        :param token: some jwt token
        :return: id of a user.
        """
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.SIGNING_METHOD])['user_id']

    @staticmethod
    def verify_user_token(token: str) -> bool:
        """
        Verify whether the given token is valid or not
        :param token: either access or refresh token
        :return: whether the token is valid or not.
        """
        valid = False
        if token:
            try:
                user_id = AuthService.get_user_id_from_token(token)
                # Verify if the user exists
                if db.get_item(settings.TABLE_NAME_USERS, settings.PK, user_id):
                    valid = True
                    return valid
            except jwt.ExpiredSignatureError:
                warn('The given token is expired')
            except (jwt.DecodeError, jwt.InvalidTokenError):
                warn('The given token is invalid')
        return valid


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
            return self.verifying_creds(credentials.credentials, request)
        else:
            warn('Access denied (Invalid authorization code)')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid authorization code.')

    @classmethod
    def verifying_creds(cls, token: str, request: Request):
        """
        The function to be overridden. Allow a coder to develop a custom user authentication
        :param token: jwt token
        :param request: request from client
        :return: return the given token if valid, otherwise raise HTTPException.
        """
        if not AuthService.verify_user_token(token):
            warn('Access denied (The token is invalid)')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid or expired token.')
        return token


class IsUserOwner(JWTBearer):
    @classmethod
    def verifying_creds(cls, token: str, request: Request):
        """
        Verify the given token and additionally check out whether the user owns requested profile
        :param token: jwt token
        :param request: request from client
        :return: return the given token is valid and the requested user is the page's owner,
                 otherwise throw HTTPException.
        """
        if not AuthService.verify_user_token(token):
            warn('Access denied (The token is invalid)')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid token or expired token.')

        try:
            user_id = int(request.get('path_params')['user_id'])
        except ValueError:
            warn('Access denied (The given params are invalid')
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The given params are invalid.')
        else:
            user_id_from_token = AuthService.get_user_id_from_token(token)
            if user_id_from_token != user_id:
                warn('Access denied (The user has no permission to view this page)')
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='You have no permission to view this page')
            return token
