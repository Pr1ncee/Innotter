import json

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import dotenv

from authorization.views import token_verify


config = dotenv.dotenv_values(".env")


class CustomJWTAuthenticationMiddleware(MiddlewareMixin):
    def create_response(self, request_id, code, message):
        try:
            request = str(request_id)
            data = {'data': message, 'code': int(code), 'request_id': request}
            return data
        except Exception:
            pass

    def process_request(self, request):
        jwt_token = request.headers.get('authorization', None)

        data, status = token_verify(jwt_token)

        response = json.dumps(self.create_response("", 4001, data))
        return HttpResponse(response, status=status)
