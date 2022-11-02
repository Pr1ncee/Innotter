from rest_framework import serializers

from user.models import User
from .models import Page, Post


class PagesSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Page model to allow any user browse existed pages.
    """
    class Meta:
        model = Page
        exclude = ('unblock_date', 'follow_requests')


class MyPagesSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Page model to allow an owner to look through and edit his pages.
    """
    class Meta:
        model = Page
        fields = ('name', 'uuid', 'description', 'tags', 'followers',
                  'follow_requests', 'is_private', 'image', 'unblock_date', 'posts')
        read_only_fields = ('followers', 'follow_requests', 'unblock_date', 'posts')


class PageFollowRequestsSerializer(serializers.ModelSerializer):
    """
    Provide appropriate data for follow methods.
    """
    class Meta:
        model = Page
        exclude = ('owner',)
        read_only_fields = ('name', 'uuid', 'description', 'tags',
                            'followers', 'is_private', 'unblock_date', 'image')


class PageTagsSerializer(serializers.ModelSerializer):
    """
    Serializer for destroying page's tags.
    """
    class Meta:
        model = Page
        fields = ('name', 'tags')


class PageFollowersSerializer(serializers.ModelSerializer):
    """
    Provide appropriate data to follow a page.
    """
    class Meta:
        model = Page
        fields = ('name', 'uuid', 'followers', 'is_private')
        read_only_fields = ('name', 'uuid', 'is_private', 'followers')


class PostSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Post model with all fields corresponding to the methods.
    """
    class Meta:
        model = Post
        fields = ('title', 'content', 'reply_to', 'page', 'liked_by')
        read_only_fields = ('liked_by',)


class ManagerPageSerializer(serializers.ModelSerializer):
    """
    Provide fields for moderators' and administrators' actions of Page model.
    """
    class Meta:
        model = Page
        fields = ('name', 'uuid', 'description', 'tags', 'owner',
                  'followers', 'follow_requests', 'is_private', 'image', 'unblock_date')
        read_only_fields = ('name', 'uuid', 'description', 'is_private',
                            'image', 'tags', 'followers', 'follow_requests', 'owner')


class ManagerPostSerializer(serializers.ModelSerializer):
    """
    Provide fields for moderators' and administrators' actions of Post model.
    """
    class Meta:
        model = Post
        fields = ('page', 'title', 'content', 'reply_to')
        read_only_fields = ('page', 'title', 'content', 'reply_to')


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Provide fields for setting user's permissions
    """
    class Meta:
        model = User
        fields = ('username', 'is_staff', 'is_active', 'role', 'is_blocked')
        read_only_fields = ('email', 'username', 'image_path', 'liked')
