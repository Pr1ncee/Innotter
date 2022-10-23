from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions


class ObtainTokensSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=100)

    def validate(self, data):
        authenticate_kwargs = {
            'username': data['username'],
            'password': data['password']
        }

        user = authenticate(**authenticate_kwargs)

        if not (user is not None and user.is_active):
            raise exceptions.AuthenticationFailed('no active account')

        return {}


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=1024)


class TokenVerifySerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=1024)
