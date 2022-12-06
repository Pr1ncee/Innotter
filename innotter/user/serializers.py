from rest_framework import serializers

from user.models import User


class ListUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'role')
        read_only_fields = ('username', 'role')


class UpdateUserSerializer(serializers.ModelSerializer):
    image_path = serializers.FileField(required=False)

    def to_representation(self, instance):
        """Insert actual image's url if it exists."""
        rep = super().to_representation(instance)
        rep['image_path'] = instance.image_path
        return rep

    class Meta:
        model = User
        fields = ('username', 'email', 'image_path', 'role', 'is_blocked', 'liked')
        read_only_fields = ('role', 'is_blocked', 'liked')


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Provide fields for managing users.
    """
    class Meta:
        model = User
        fields = ('username', 'is_staff', 'is_active', 'role', 'is_blocked')
        read_only_fields = ('email', 'username', 'image_path', 'liked')
