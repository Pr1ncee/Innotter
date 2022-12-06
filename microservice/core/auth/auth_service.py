import logging

import jwt

from core.settings import settings
from core.aws.dynamodb_client import DynamoDBClient


logger = logging.getLogger(__name__)
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
                user_id = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_SIGNING_METHOD]
                )['user_id']
                # Verify if the user exists
                if db.get_item(settings.USERS_NAME_TABLE, settings.PK, user_id):
                    valid = True
                    return valid
            except jwt.ExpiredSignatureError:
                logger.warning('The given token is expired')
            except (jwt.DecodeError, jwt.InvalidTokenError):
                logger.warning('The given token is invalid')
        return valid
