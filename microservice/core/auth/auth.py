from warnings import warn

import jwt
from fastapi import status, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.settings import settings
from core.aws.dynamodb_client import DynamoDBClient


db = DynamoDBClient


class AuthService:
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
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.SIGNING_METHOD])
                # Verify if the user exists
                if db.get_item(settings.TABLE_NAME_USERS, settings.PK, payload['user_id']):
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
            if not AuthService.verify_user_token(credentials.credentials):
                warn('Access denied (The token is invalid)')
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            warn('Access denied (Invalid authorization code)')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")
