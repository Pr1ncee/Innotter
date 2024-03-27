from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions


class CredentialsSerializer(serializers.Serializer):
    """
    (De)Serialize user's credentials and validate them.
    """
    username = serializers.CharField(max_length=50, write_only=True)
    password = serializers.CharField(max_length=100, style={'input_type': 'password'},
                                     write_only=True, trim_whitespace=True)

    def validate(self, data):
        try:
            authenticate_kwargs = {
                'username': data['username'],
                'password': data['password']
            }
        except KeyError:
            msg = 'Both "username" and "password" are required'
            raise serializers.ValidationError(msg, code='authorization')

        user = authenticate(**authenticate_kwargs)

        if not (user and user.is_active):
            raise exceptions.AuthenticationFailed('Access denied: no active account')

        data['user'] = user
        return data


class RegisterSerializer(serializers.Serializer):
    """
    Deserialize given credentials and validate them.
    """
    username = serializers.CharField(max_length=50, write_only=True)
    password = serializers.CharField(max_length=100, style={'input_type': 'password'},
                                     write_only=True, trim_whitespace=True)
    email = serializers.EmailField(allow_blank=False)

    def validate(self, data):
        try:
            authenticate_kwargs = {
                'username': data['username'],
                'password': data['password'],
                'email': data['email']
            }
        except KeyError:
            msg = 'All the fields are required.'
            raise serializers.ValidationError(msg, code='authorization')

        return authenticate_kwargs


class TokenRefreshSerializer(serializers.Serializer):
    """
    (De)Serialize given refresh token.
    """
    refresh_token = serializers.CharField(max_length=1024)


class ObtainTokensSerializer(CredentialsSerializer):
    """
    Use CredentialsSerializer to (de)serialize and validate the given credentials.
    """
    pass
