from datetime import date

from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework import viewsets, mixins

from authorization.permissions import IsModerator
from .models import Page, Post
from user.models import User
from .serializers import CreateListUpdatePageSerializer, ListAllPagesSerializer, \
                         DestroyTagSerializer, CreateListUpdateDestroyPostSerializer,\
                         ListLikedPostSerializer, ManagerPageSerializer, ManagerPostSerializer, AdminUserSerializer


class ListAllPagesViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    Allow any user to readonly all the pages.
    """
    permission_classes = [AllowAny]
    serializer_class = ListAllPagesSerializer
    queryset = Page.objects.exclude(owner__is_blocked=True)\
                           .exclude(unblock_date__gt=date.today()).exclude(is_private=True)


class CreateListPageViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    Implement 'list' and 'create' methods of Page model.
    Overridden 'create' method validate given data
    And link 'owner' field of Page model to user, who sent the data.
    """
    serializer_class = CreateListUpdatePageSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        return Page.objects.filter(owner=user_id)

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


class UpdatePageViewSet(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    Implement both 'put' & 'patch' methods and also provide 'destroy' method of Page model.
    """
    serializer_class = CreateListUpdatePageSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        return Page.objects.filter(owner=user_id)

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


class DestroyTagViewSet(mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    Destroy latest added tag in Page model.
    """
    serializer_class = DestroyTagSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        return Page.objects.filter(owner=user_id)

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
    serializer_class = CreateListUpdatePageSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        return Page.objects.filter(owner=user_id)


class ListAllPostsViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    Allow any user to readonly all the posts.
    """
    permission_classes = [AllowAny]
    serializer_class = CreateListUpdateDestroyPostSerializer
    queryset = Post.objects.exclude(lovers__is_blocked=True)\
                           .exclude(page__unblock_date__gt=date.today()).exclude(page__is_private=True)


class CreateListPostViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    Implement 'list' & 'create' methods of Post model.
    """
    serializer_class = CreateListUpdateDestroyPostSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        return Post.objects.filter(page__owner_id=user_id)


class UpdateDestroyPostViewSet(mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """
    Implement both 'put' & 'patch' and 'destroy' methods of Post model.
    """
    serializer_class = CreateListUpdateDestroyPostSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        return Post.objects.filter(page__owner_id=user_id)


class ListLikedPostViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    List user's liked posts.
    """
    serializer_class = ListLikedPostSerializer

    def get_queryset(self):
        user = self.request.user

        return Post.objects.filter(lovers=user)


class ManagerPageViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """
    Allow moderators and administrators to manipulate with users' pages.
    """
    permission_classes = [IsAdminUser | IsModerator]
    serializer_class = ManagerPageSerializer
    queryset = Page.objects.all()


class ManagerPostViewSet(mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    Allow moderators and administrators to manipulate with user's posts.
    """
    permission_classes = [IsAdminUser | IsModerator]
    serializer_class = ManagerPostSerializer
    queryset = Post.objects.all()


class AdminUserViewSet(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    Allow administrators ban users.
    """
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()
