from rest_framework import serializers

from user.models import User
from .models import Page, Post


class CreateListUpdatePageSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Page model with specified fields corresponding to the methods.
    """
    class Meta:
        model = Page
        fields = ['name', 'uuid', 'description', 'tags', 'is_private', 'image']


class PageSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Page model with fields 'followers' & 'follow_requests'.
    """
    class Meta:
        model = Page
        fields = ['name', 'description', 'tags', 'followers', 'follow_requests', 'is_private']


class DestroyTagSerializer(serializers.ModelSerializer):
    """
    Destroy Page's tag(s).
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
        model = User
        fields = ['liked']
