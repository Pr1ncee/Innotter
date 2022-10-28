from rest_framework import serializers

from user.models import User
from .models import Page, Post


class ListAllPagesSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Page model to allow any user browse existed pages.
    """
    class Meta:
        model = Page
        exclude = ['unblock_date', 'follow_requests']


class CreateListUpdatePageSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Page model to allow an owner to look through and edit his pages.
    """
    class Meta:
        model = Page
        exclude = ['owner']
        read_only_fields = ['followers', 'follow_requests', 'unblock_date']


class DestroyTagSerializer(serializers.ModelSerializer):
    """
    Serializer for destroying page's tags.
    """
    class Meta:
        model = Page
        fields = ['name', 'tags']


class CreateListUpdateDestroyPostSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Post model with all fields corresponding to the methods.
    """
    class Meta:
        model = Post
        fields = '__all__'


class ListLikedPostSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Post model with 'lovers' field.
    """
    class Meta:
        model = Post
        fields = ['lovers']


class ManagerPageSerializer(serializers.ModelSerializer):
    """
    Provide fields for moderators' and administrators' actions of Page model.
    """
    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ['name', 'uuid', 'description', 'is_private',
                            'image', 'tags', 'followers', 'follow_requests', 'owner']


class ManagerPostSerializer(serializers.ModelSerializer):
    """
    Provide fields for moderators' and administrators' actions of Post model.
    """
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['__all__']


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'is_staff', 'is_active', 'role', 'is_blocked']
        read_only_fields = ['email', 'username', 'image_path', 'liked']
