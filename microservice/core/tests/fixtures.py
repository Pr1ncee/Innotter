from datetime import datetime, timezone, timedelta

import jwt
from pytest import fixture

from core.settings import settings


@fixture
def create_valid_token() -> str:
    ttl = 999999
    payload = {"user_id": 1,
               "iss": "innotter",
               "exp": datetime.now(tz=timezone.utc) + timedelta(days=ttl)}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_SIGNING_METHOD)
    return token


@fixture
def create_invalid_token() -> str:
    date = datetime(2000, 12, 14, 18, 29, 4, 0, tzinfo=timezone.utc)
    payload = {"user_id": 1,
               "iss": "innotter",
               "exp": date}
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_SIGNING_METHOD)
    return token
