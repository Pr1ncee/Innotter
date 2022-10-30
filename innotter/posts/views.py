from datetime import date

from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework import viewsets, mixins

from authorization.permissions import IsModerator
from .models import Page, Post
from user.models import User
from .serializers import CreateListUpdatePageSerializer, ListAllPagesSerializer, \
                         DestroyPageTagSerializer, CreateListUpdateDestroyPostSerializer,\
                         ListRetrieveUpdateLikedPostSerializer, ManagerPageSerializer, ManagerPostSerializer,\
                         AdminUserSerializer, UpdatePageFollowersSerializer, RetrieveUpdatePageFollowRequestsSerializer
from .services import page_create, page_update, page_follow, page_response_follow_request, page_destroy_tag, post_like


class ListAllPagesViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    Allow any user to readonly all the pages. List only valid pages.
    """
    permission_classes = [AllowAny]
    serializer_class = ListAllPagesSerializer
    queryset = Page.objects.exclude(owner__is_blocked=True)\
                           .exclude(unblock_date__gt=date.today()).exclude(is_private=True)


class ListCreatePageViewSet(mixins.ListModelMixin,
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

        queryset = Page.objects.filter(owner=user_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        page_create(request, serializer)

        return Response(serializer.data, status=HTTP_201_CREATED)


class RetrieveUpdateDestroyPageViewSet(mixins.RetrieveModelMixin,
                                       mixins.UpdateModelMixin,
                                       mixins.DestroyModelMixin,
                                       viewsets.GenericViewSet):
    """
    Implement both 'put' & 'patch' methods and also provide 'destroy' method of Page model.
    """
    serializer_class = CreateListUpdatePageSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        queryset = Page.objects.filter(owner=user_id)
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        page_update(serializer, instance)

        return Response(serializer.data)


class RetrieveDestroyPageTagViewSet(mixins.RetrieveModelMixin,
                                    mixins.DestroyModelMixin,
                                    viewsets.GenericViewSet):
    """
    Destroy latest added tag in Page model.
    """
    serializer_class = DestroyPageTagSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        queryset = Page.objects.filter(owner=user_id)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        page_destroy_tag(instance)

        return Response(status=HTTP_200_OK)


class RetrieveUpdatePageFollowersViewSet(mixins.RetrieveModelMixin,
                                         mixins.UpdateModelMixin,
                                         viewsets.GenericViewSet):
    """
    Allow user to follow or send follow request to page. List only valid pages.
    """
    serializer_class = UpdatePageFollowersSerializer
    queryset = Page.objects.exclude(owner__is_blocked=True) \
                           .exclude(unblock_date__gt=date.today())

    def perform_update(self, serializer):
        page = self.get_object()
        info = page_follow(self.request, page)

        return Response(data=info, status=HTTP_200_OK)


class AcceptPageFollowRequestViewSet(mixins.RetrieveModelMixin,
                                     mixins.UpdateModelMixin,
                                     viewsets.GenericViewSet):
    """
    Allow page owner to accept follow requests.
    """
    serializer_class = RetrieveUpdatePageFollowRequestsSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        queryset = Page.objects.filter(owner=user_id)
        return queryset

    def perform_update(self, serializer):
        page = self.get_object()
        page_response_follow_request(page, mode='accept')

        return Response(status=HTTP_200_OK)


class DenyPageFollowRequestViewSet(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   viewsets.GenericViewSet):
    """
    Allow page owner to deny follow requests.
    """
    serializer_class = RetrieveUpdatePageFollowRequestsSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        queryset = Page.objects.filter(owner=user_id)
        return queryset

    def perform_update(self, serializer):
        page = self.get_object()
        page_response_follow_request(page, mode='deny')

        return Response(status=HTTP_200_OK)


class ListAllPostsViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    Allow any user to readonly all the posts. List only valid posts
    """
    permission_classes = [AllowAny]
    serializer_class = CreateListUpdateDestroyPostSerializer
    queryset = Post.objects.exclude(liked_by__is_blocked=True)\
                           .exclude(page__unblock_date__gt=date.today()).exclude(page__is_private=True)


class ListFollowedMyPostsViewSet(mixins.ListModelMixin,
                                 viewsets.GenericViewSet):
    serializer_class = CreateListUpdateDestroyPostSerializer

    def get_queryset(self):
        """
        Displayed posts are filtered based on user's owned posts and followed pages.
        Each post belongs to certain page. Follow page means follow post as well.

        'user': user who made a request.
        'my_posts': Queryset object which is made of user's posts.
        'followed_posts': Queryset object which is made of valid followed posts.
        'queryset': Queryset object which is a distinct union of 'my_posts' & 'followed_posts'.
        """
        user_id = self.request.user.id
        user = User.objects.get(pk=user_id)

        my_posts = Post.objects.filter(page__owner=user)
        followed_posts = Post.objects.filter(page__followers=user).exclude(page__unblock_date__gt=date.today())
        queryset = (my_posts | followed_posts).distinct()
        return queryset


class CreateListPostViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    """
    Implement 'list' & 'create' methods of Post model.
    """
    serializer_class = CreateListUpdateDestroyPostSerializer

    def get_queryset(self):
        user_id = self.request.user.id

        queryset = Post.objects.filter(page__owner_id=user_id)
        return queryset


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

        queryset = Post.objects.filter(page__owner_id=user_id)
        return queryset


class ListLikedPostViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    List user's liked posts.
    """
    serializer_class = ListRetrieveUpdateLikedPostSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Post.objects.filter(liked_by=user)
        return queryset


class RetrieveUpdatePostLikeViewSet(mixins.RetrieveModelMixin,
                                    mixins.UpdateModelMixin,
                                    viewsets.GenericViewSet):
    """
    Provide 'like' page method. List only valid liked posts.
    """
    serializer_class = ListRetrieveUpdateLikedPostSerializer
    queryset = Post.objects.exclude(liked_by__is_blocked=True) \
                           .exclude(page__unblock_date__gt=date.today()).exclude(page__is_private=True)

    def perform_update(self, serializer):
        post = self.get_object()
        post_like(self.request, post)

        return Response(status=HTTP_200_OK)


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
