from fastapi import status


class BaseError(Exception):
    status_code: int
    default_detail: str

    def __init__(self, detail: str = None):
        self.detail = detail or self.default_detail


class AuthenticateError(BaseError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid authentication scheme'


class InvalidCredentialsError(AuthenticateError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid credentials were provided'


class InvalidTokenError(AuthenticateError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'The token is invalid'


class InvalidParamsError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid parameters were provided'


class NoPermissionError(BaseError):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You have no permissions to view this page'


class InvalidObjectTypeError(Exception):
    default_detail = 'The object data type is not supported by this function'

    def __init__(self, detail):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


