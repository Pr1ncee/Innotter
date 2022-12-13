import sys
sys.path.append('/app/microservice/')

from fastapi import status
from fastapi.testclient import TestClient

from core.auth.auth_service import AuthService
from core.main import app


client = TestClient(app)


class TestAuthService:
    _invalid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJpc3MiOiJpbm5vdH' \
                     'RlciIsImV4cCI6MTY3MDg4MzM1M30.G71aEzCS32bkVZswMK_czZlxh5xAV2GHIP7WWfy9Ovg'
    _valid_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJpc3MiOiJpbm5vdH' \
                   'RlciIsImV4cCI6ODgwNzA3OTczMDR9.h4Aq9b9qUAaGuJfV-BvQjPIlLfvVs8XNoNDOC3PXUYA'
    _url = '/api/v1/stats/1/'

    def test_auth_service_invalid_token(self):
        response = AuthService.verify_user_token(self._invalid_token)
        assert not response

    def test_auth_service_valid_token(self):
        response = AuthService.verify_user_token(self._valid_token)
        assert response

    def test_auth_service_403_response(self):
        headers = {'Authorization': f'Bearer {self._invalid_token}'}
        response = client.get(self._url, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_auth_service_200_response(self):
        headers = {'Authorization': f'Bearer {self._valid_token}'}
        response = client.get(self._url, headers=headers)
        assert response.status_code == status.HTTP_200_OK
