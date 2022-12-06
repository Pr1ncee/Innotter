from fastapi import FastAPI

from api.router import base_router
from core.exceptions.exception_handlers import *


app = FastAPI()

app.add_exception_handler(AuthenticateError, authentication_exception_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_exception_handler)
app.add_exception_handler(InvalidTokenError, invalid_token_exception_handler)
app.add_exception_handler(InvalidParamsError, invalid_params_exception_handler)
app.add_exception_handler(NoPermissionError, no_permission_exception_handler)

app.include_router(base_router)
