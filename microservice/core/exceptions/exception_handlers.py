from fastapi.responses import JSONResponse
from fastapi import Request

from core.exceptions.base_exceptions import (
    AuthenticateError,
    InvalidCredentialsError,
    InvalidTokenError,
    InvalidParamsError,
    NoPermissionError
)


async def authentication_exception_handler(request: Request, exc: AuthenticateError):
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
    )


async def invalid_credentials_exception_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
    )


async def invalid_token_exception_handler(request: Request, exc: InvalidTokenError):
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
    )


async def invalid_params_exception_handler(request: Request, exc: InvalidParamsError):
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
    )


async def no_permission_exception_handler(request: Request, exc: NoPermissionError):
    return JSONResponse(
        status_code=exc.status_code, content={'detail': exc.detail}
    )
