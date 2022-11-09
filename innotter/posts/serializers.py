from rest_framework import serializers

from .models import Page, Post


class CreateUpdatePagesSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Page model to allow any user browse existed pages.
    """
    class Meta:
        model = Page
        exclude = ('unblock_date', 'follow_requests')


class ListUpdateMyPagesSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Page model to allow an owner to look through and edit his pages.
    """
    image = serializers.FileField(required=False)

    def to_representation(self, instance):
        """Insert actual image's url if it exists."""
        rep = super().to_representation(instance)
        try:
            img = instance.image
        except AttributeError:
            img = instance.get('image', None)

        rep['image'] = img
        return rep

    class Meta:
        model = Page
        fields = ('name',
                  'uuid',
                  'description',
                  'tags',
                  'followers',
                  'follow_requests',
                  'is_private',
                  'image',
                  'unblock_date',
                  'posts',
                  'id')
        read_only_fields = ('followers', 'follow_requests', 'unblock_date', 'posts', 'id')


class UpdatePageFollowRequestsSerializer(serializers.ModelSerializer):
    """
    Provide appropriate fields for managing follow requests.
    """
    class Meta:
        model = Page
        exclude = ('owner',)
        read_only_fields = ('name',
                            'uuid',
                            'description',
                            'tags',
                            'followers',
                            'is_private',
                            'unblock_date',
                            'image')


class DeletePageTagsSerializer(serializers.ModelSerializer):
    """
    Serializer for destroying page's tags.
    """
    class Meta:
        model = Page
        fields = ('name', 'tags')


class UpdatePageFollowersSerializer(serializers.ModelSerializer):
    """
    Provide appropriate fields to follow a page.
    """
    class Meta:
        model = Page
        fields = ('name', 'uuid', 'followers', 'is_private')
        read_only_fields = ('name', 'uuid', 'is_private', 'followers')


class ListRetrievePostSerializer(serializers.ModelSerializer):
    """
    (De)Serialize Post model with all fields corresponding to the methods.
    """
    class Meta:
        model = Post
        fields = ('title', 'content', 'reply_to', 'page', 'liked_by', 'id')
        read_only_fields = ('title', 'content', 'reply_to', 'page', 'liked_by', 'id')


class UpdatePostSerializer(serializers.ModelSerializer):
    """
    Allow user to edit Post object.
    """
    class Meta:
        model = Post
        fields = ('title', 'content', 'reply_to', 'page', 'liked_by', 'id')
        read_only_fields = ('liked_by', 'id')


class UpdateBlockPageSerializer(serializers.ModelSerializer):
    """
    Provide fields for moderators' and administrators' actions of Page model.
    """
    class Meta:
        model = Page
        fields = ('name',
                  'uuid',
                  'description',
                  'tags',
                  'owner',
                  'followers',
                  'follow_requests',
                  'is_private',
                  'image',
                  'unblock_date')
        read_only_fields = ('name',
                            'uuid',
                            'description',
                            'is_private',
                            'image',
                            'tags',
                            'followers',
                            'follow_requests',
                            'owner')


class RetrievePostSerializer(serializers.ModelSerializer):
    """
    Provide fields for moderators' and administrators' actions of Post model.
    """
    class Meta:
        model = Post
        fields = ('page', 'title', 'content', 'reply_to')
        read_only_fields = ('page', 'title', 'content', 'reply_to')
