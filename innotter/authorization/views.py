from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

<<<<<<< HEAD
from .serializers import TokenRefreshSerializer, RegisterSerializer, ObtainTokensSerializer
from .services import obtain_tokens, signup_user, refresh_user_token
=======
from .serializers import TokenRefreshSerializer, TokenVerifySerializer, RegisterSerializer, ObtainTokensSerializer
from .services import obtain_tokens, signup_user, verify_user_token, refresh_user_token
>>>>>>> ded63ef5c5337092a4cb3d01aba73b6a9d0f21fd


class UserTokenRefreshView(APIView):
    """
    Take refresh token. If the given deserialized token is valid, return valid access token.
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


<<<<<<< HEAD
class ObtainTokensView(APIView):
=======
class UserTokenVerifyView(APIView):
>>>>>>> ded63ef5c5337092a4cb3d01aba73b6a9d0f21fd
    """
    Generate and send back both access and refresh tokens, return status=202.
    """
    serializer_class = ObtainTokensSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
<<<<<<< HEAD
        user = serializer.validated_data['user']

=======
        refresh_token = serializer.validated_data['access_token']

        data, status_code = verify_user_token(refresh_token)
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

>>>>>>> ded63ef5c5337092a4cb3d01aba73b6a9d0f21fd
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
        username, password, email = serializer.validated_data['username'], \
<<<<<<< HEAD
                                    serializer.validated_data['password'], \
                                    serializer.validated_data['email']
=======
                                    serializer.validated_data['password'], serializer.validated_data['email']
>>>>>>> ded63ef5c5337092a4cb3d01aba73b6a9d0f21fd

        signup_user(username, password, email)
        return Response(None, status=status.HTTP_201_CREATED)
