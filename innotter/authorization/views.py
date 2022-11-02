from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .serializers import TokenRefreshSerializer, TokenVerifySerializer, \
                         LoginSerializer, RegisterSerializer, LogoutSerilaizer
from .services import user_signin, user_signout, user_signup, user_token_verify, user_token_refresh


class UserTokenRefreshApi(APIView):
    """
    Take refresh token. If the given deserialized token is valid, return valid access token.
    """
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        user_id = request.user.id
        serializer = self.serializer_class(data=request.data)

        data, status_code = user_token_refresh(serializer, user_id)
        return Response(data, status=status_code)


class UserTokenVerifyApi(APIView):
    """
    Take access token. Return whether the deserialized token is valid or not.
    """
    serializer_class = TokenVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        data, status_code = user_token_verify(serializer)
        return Response(data, status=status_code)


class UserSigninApi(APIView):
    """
    Implement user signin, return status=202.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        data = user_signin(request, serializer)
        return Response(data, status=status.HTTP_202_ACCEPTED)


class UserSignoutApi(APIView):
    """
    Implement user signout, return status=204
    """
    serializer_class = LogoutSerilaizer

    def get(self, request):
        user_signout(request)

        return Response(None, status=status.HTTP_204_NO_CONTENT)


class UserSignupApi(APIView):
    """
    Implement user signup, return status=202.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        user_signup(serializer)
        return Response(None, status=status.HTTP_201_CREATED)
