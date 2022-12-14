import sys
sys.path.append('/app/microservice/')

from fastapi import status
from fastapi.testclient import TestClient

from core.auth.auth_service import AuthService
from core.main import app


client = TestClient(app)


class TestAuthService:
    _url = '/api/v1/stats/1/'

    def test_auth_service_invalid_token(self, create_invalid_token):
        response = AuthService.verify_user_token(create_invalid_token)
        assert not response

    def test_auth_service_valid_token(self, create_valid_token):
        response = AuthService.verify_user_token(create_valid_token)
        assert response

    def test_auth_service_403_response(self, create_invalid_token):
        headers = {'Authorization': f'Bearer {create_invalid_token}'}
        response = client.get(self._url, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_auth_service_200_response(self, create_valid_token):
        headers = {'Authorization': f'Bearer {create_valid_token}'}
        response = client.get(self._url, headers=headers)
        assert response.status_code == status.HTTP_200_OK
