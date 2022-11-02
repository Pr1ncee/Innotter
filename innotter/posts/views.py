from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework import viewsets, mixins

from authorization.permissions import IsModerator
from .models import Page, Post
from user.models import User
from .serializers import PagesSerializer, MyPagesSerializer, PageTagsSerializer, \
                         PageFollowersSerializer, PageFollowRequestsSerializer, \
                         PostSerializer, ManagerPageSerializer, ManagerPostSerializer, \
                         AdminUserSerializer
from .services import page_create, page_update, page_follow, page_response_follow_request, \
                      page_destroy_tag, post_like, manager_view


class PagesViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    """
    Either list all valid pages or provide 'follow' page's method.
    """
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Return queryset based on request method.
        """
        if self.action == 'manager_pages_view':
            return Page.objects.all()

        pk = self.kwargs.get('pk')
        if not pk:
            return Page.pages_objects.valid_pages()

        return Page.pages_objects.get_all_valid_pages()

    def get_serializer_class(self):
        """
        Return serializer class based on request method.
        """
        if self.action == 'list':
            return PagesSerializer
        elif self.action in ('retrieve', 'update', 'partial_update'):
            return PageFollowersSerializer
        elif self.action == 'manager_pages_view':
            return ManagerPageSerializer

    def perform_update(self, serializer):
        page = self.get_object()
        info = page_follow(self.request, page)

        return Response(data=info, status=HTTP_200_OK)

    @action(methods=['get', 'put'], detail=True, url_path='admin', permission_classes=[IsAdminUser | IsModerator])
    def manager_pages_view(self, request, pk=None):
        """
        Allow admins and moderators manage pages.
        """
        serializer, status_code = manager_view(request, self.get_serializer,
                                               self.get_object(), self.args, self.kwargs)

        return Response(serializer.data, status=status_code)


class MyPagesViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    Provide CRUD methods for Page objects. Extra actions for removing tags, accepting and denying follow requests.
    """
    def get_queryset(self):
        user_id = self.request.user.id
        return Page.pages_objects.user_pages(user_id)

    def get_serializer_class(self):
        match self.action:
            case 'tags':
                return PageTagsSerializer
            case 'follow_requests':
                return PageFollowRequestsSerializer
            case _:
                return MyPagesSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        page_create(request, serializer)

        return Response(serializer.data, status=HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        page_update(serializer, instance)

        return Response(serializer.data)

    @action(methods=['get', 'delete'], detail=True, url_path='tags')
    def tags(self, request, pk=None):
        if request.method == 'DELETE':
            instance = self.get_object()

            serializer = self.get_serializer(page_destroy_tag(instance))
            return Response(serializer.data, status=HTTP_200_OK)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(methods=['get', 'put', 'delete'], detail=True, url_path='follow-requests')
    def follow_requests(self, request, pk=None):
        """
        Implement method for retrieving, accepting and denying follow requests.
        """
        page = self.get_object()
        serializer = self.get_serializer()
        status_code = HTTP_200_OK

        match request.method:
            case 'GET':
                serializer = serializer(self.get_queryset(), many=True)
            case 'PUT':
                serializer = serializer(page_response_follow_request(page, mode='accept'))
            case 'DELETE':
                serializer = serializer(page_response_follow_request(page, mode='deny'))

        return Response(serializer.data, status=status_code)


class PostsViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    """
    Either list all valid posts or provide 'like' post's method.
    """
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action == 'manager_posts_view':
            return Post.objects.all()

        return Post.posts_objects.valid_posts()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'manager_posts_view':
            return ManagerPostSerializer

        return PostSerializer

    def perform_update(self, serializer):
        post = self.get_object()
        post_like(self.request, post)

        return Response(status=HTTP_200_OK)

    @action(methods=['get', 'delete'], detail=True, url_path='admin', permission_classes=[IsAdminUser | IsModerator])
    def manager_posts_view(self, request, pk=None):
        """
        Allow admins and moderators manage posts.
        """
        serializer, status_code = manager_view(request, self.get_serializer,
                                               self.get_object(), self.args, self.kwargs)

        return Response(serializer.data, status=status_code)


class MyPostsViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    Provide CRUD methods for Post objects. Allow user to get feed and liked posts as well.
    """
    serializer_class = PostSerializer

    def get_queryset(self):
        """
        Return queryset depends on request action. By default return user's posts.
        """
        user = self.request.user
        match self.action:
            case 'liked_posts':
                return Post.posts_objects.liked_posts(user)
            case 'feed':
                return Post.posts_objects.feed_posts(user)
            case _:
                return Post.posts_objects.user_posts(user.id)

    @action(methods=['get'], detail=False, url_path='liked')
    def liked_posts(self, request):
        """
        List user's liked posts.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='feed')
    def feed(self, request):
        """
        Implement feed by filtering followed and owned posts.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class AdminUserViewSet(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    Allow administrators ban users.
    """
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()
