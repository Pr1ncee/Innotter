from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework import viewsets, mixins

from .models import Page, Post
from user.models import User
from .serializers import PageSerializer, CreateListUpdatePageSerializer, \
                         DestroyTagSerializer, CreateListUpdateDestroyPostSerializer, ListLikedPostSerializer


class CreateListPageViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    Implement list and create methods of Page model.
    Overridden 'create' method validate given data
    And link 'owner' field of Page model to user, who sent the data.
    """
    serializer_class = CreateListUpdatePageSerializer
    queryset = Page.objects.all()

    def create(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.id)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['owner'] = user
        tag = serializer.validated_data.pop('tags')

        new_page = Page.objects.create(**serializer.validated_data)
        new_page.tags.set(tag)
        new_page.save()

        return Response(serializer.data, status=HTTP_201_CREATED)


class UpdatePageViewSet(mixins.UpdateModelMixin,
                        viewsets.GenericViewSet):
    """
    Implement both 'put' & 'patch' methods of Page model.
    """
    serializer_class = CreateListUpdatePageSerializer
    queryset = Page.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # List of Tag objects
        tags_list = serializer.validated_data.pop('tags')
        # Several tags can be possibly sent, that's why we loop through the give list
        for tag in tags_list:
            instance.tags.add(tag)
        serializer.save()

        return Response(serializer.data)


class DestroyTagViewSet(mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    Destroy last added tag in Page model.
    """
    serializer_class = DestroyTagSerializer
    queryset = Page.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Delete last added tag
        tag_to_delete = instance.tags.last()
        instance.tags.remove(tag_to_delete)
        instance.save()

        return Response(status=HTTP_200_OK)


class RetrieveFollowRequestsViewSet(mixins.RetrieveModelMixin,
                                    viewsets.GenericViewSet):
    """
    Retrieve page's followers and follow requests according to given page's id.
    """
    serializer_class = PageSerializer
    queryset = Page.objects.all()


class CreateListPostViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    Implement 'list' & 'create' methods of Post model.
    """
    serializer_class = CreateListUpdateDestroyPostSerializer
    queryset = Post.objects.all()


class UpdateDestroyPostViewSet(mixins.UpdateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """
    Implement both 'put' & 'patch' and 'destroy' methods of Post model.
    """
    serializer_class = CreateListUpdateDestroyPostSerializer
    queryset = Post.objects.all()


class ListLikedPostViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    List user's liked posts.
    """
    # TODO link volumes to the container
    serializer_class = ListLikedPostSerializer
    queryset = User.objects.all()

