import json

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.status import HTTP_200_OK

from authorization.views import token_verify


class CustomJWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            jwt_token = request.headers.get('authorization', None)

            data, status = token_verify(jwt_token)
            if status != HTTP_200_OK:
                response = {'data': data, 'status': status, 'code': 4001}
                json_response = json.dumps(response)
                return HttpResponse(json_response, status=status)

        else:
            pass
