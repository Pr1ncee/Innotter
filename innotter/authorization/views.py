from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .serializers import TokenRefreshSerializer, RegisterSerializer, ObtainTokensSerializer
from .services import obtain_tokens, signup_user, refresh_user_token


class UserTokenRefreshView(APIView):
    """
    Take refresh token. If given deserialized token is valid, return valid access token.
    """
    permission_classes = (AllowAny,)
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh_token']

        user_id = request.user.id
        data, status_code = refresh_user_token(refresh_token, user_id)
        return Response(data, status=status_code)


class ObtainTokensView(APIView):
    """
    Generate and send back both access and refresh tokens, return status=202.
    """
    serializer_class = ObtainTokensSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        data = obtain_tokens(user.id)
        return Response(data, status=status.HTTP_202_ACCEPTED)


class UserSignupView(APIView):
    """
    Implement user signup, return status=202.
    """
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username, password, email = \
            serializer.validated_data['username'], \
            serializer.validated_data['password'], \
            serializer.validated_data['email']

        data, status_code = signup_user(username, password, email)
        return Response(data, status=status_code)
