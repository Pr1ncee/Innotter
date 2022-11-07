from rest_framework import serializers

from .models import User


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Provide fields for setting user's permissions.
    """
    class Meta:
        model = User
        fields = ('username', 'is_staff', 'is_active', 'role', 'is_blocked')
        read_only_fields = ('email', 'username', 'image_path', 'liked')
