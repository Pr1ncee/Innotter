from pytest import fixture

from authorization import services


username, password, email = 'test', 'test', 'andrewvs0707@gmail.com'


@fixture
def signup_user(db):
    result, status_code = services.signup_user(username, password, email)
    return result, status_code


@fixture
def obtain_tokens(db):
    def _obtain_tokens(user_id: int) -> dict[str, str]:
        """
        Return both access and refresh tokens
        :param user_id: user id
        :return: dict with both tokens.
        """
        data = services.obtain_tokens(user_id)
        return data

    return _obtain_tokens
