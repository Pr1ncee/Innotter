from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework import viewsets, mixins

from authorization.permissions import IsModerator
from .models import Page, Post
from user.models import User
from .serializers import CreateUpdatePagesSerializer, ListUpdateMyPagesSerializer, DeletePageTagsSerializer, \
                         UpdatePageFollowersSerializer, UpdatePageFollowRequestsSerializer, ListRetrievePostSerializer,\
                         UpdatePostSerializer, UpdateBlockPageSerializer, RetrievePostSerializer
from .services import create_page, update_page, follow_page, response_page_follow_request, \
                      destroy_page_tag, like_post, delete_object, send_email


class PagesViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    All methods for manipulating Page objects.
    """
    serializer_map = {
                      'list': CreateUpdatePagesSerializer,
                      'retrieve': UpdatePageFollowersSerializer,
                      'create': ListUpdateMyPagesSerializer,
                      'update': UpdatePageFollowersSerializer,
                      'partial_update': UpdatePageFollowersSerializer,
                      'block_page': UpdateBlockPageSerializer,
                      'get_my_pages': ListUpdateMyPagesSerializer,
                      'retrieve_my_page': ListUpdateMyPagesSerializer,
                      'update_my_page': ListUpdateMyPagesSerializer,
                      'tags': DeletePageTagsSerializer,
                      'follow_requests': UpdatePageFollowRequestsSerializer,
                      }
    permission_classes_map = {'list': (AllowAny,)}
    default_permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        """
        Instantiate and return the tuple of permissions that this view requires.
        """
        return [permission() for permission in
                self.permission_classes_map.get(self.action, self.default_permission_classes)]

    def get_queryset(self):
        """
        Return queryset based on request method.
        """
        match self.action:
            case 'manager_pages_view':
                return Page.objects.all()
            case 'get_my_pages' | 'retrieve_my_page' | 'delete_my_page'\
                 | 'delete_my_page' | 'update_my_page' | 'tags' | 'follow_requests':
                user_id = self.request.user.id
                return Page.pages_objects.get_user_pages(user_id)

        pk = self.kwargs.get('pk')
        if not pk:
            return Page.pages_objects.get_valid_pages()

        return Page.pages_objects.get_all_valid_pages()

    def get_serializer_class(self):
        """
        Return serializer class based on request method.
        """
        return self.serializer_map.get(self.action, None)

    def create(self, request, *args, **kwargs):
        """
        Create a new page.
        """
        user = User.objects.get(pk=request.user.id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['owner'] = user
        data = serializer.validated_data
        tags = data.pop('tags')

        create_page(data, tags)

        return Response(serializer.data, status=HTTP_201_CREATED)

    def perform_update(self, serializer):
        """
        Follow a page.
        """
        page = self.get_object()
        info = follow_page(self.request, page)

        return Response(data=info, status=HTTP_200_OK)

    @action(methods=('get', 'put'), detail=True, url_path='admin', permission_classes=(IsAdminUser | IsModerator))
    def block_page(self, request, pk=None):
        """
        Allow admins and moderators block pages.
        """
        instance = self.get_object()
        partial = self.kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=('get',), detail=False, url_path='my')
    def get_my_pages(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=('get',), detail=True, url_path='my')
    def retrieve_my_page(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_200_OK)

    @retrieve_my_page.mapping.delete
    def delete_my_page(self, request, pk=None):
        instance = self.get_object()
        delete_object(instance)

        return Response(status=HTTP_204_NO_CONTENT)

    @retrieve_my_page.mapping.put
    def update_my_page(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tags_list = serializer.validated_data.pop('tags', False)

        update_page(tags_list, instance)
        serializer.save()

        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=('get', 'delete'), detail=True, url_path='my/tags')
    def tags(self, request, pk=None):
        """
        Delete last tag in tags list of Page object.
        """
        if request.method == 'DELETE':
            instance = self.get_object()

            serializer = self.get_serializer(destroy_page_tag(instance))
            return Response(serializer.data, status=HTTP_200_OK)

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(methods=('get', 'put', 'delete'), detail=True, url_path='my/follow-requests')
    def follow_requests(self, request, pk=None):
        """
        Implement method for retrieving, accepting and denying follow requests.
        """
        page = self.get_object()
        serializer = self.get_serializer
        status_code = HTTP_200_OK

        match request.method:
            case 'GET':
                serializer = serializer(page)
            case 'PUT':
                serializer = serializer(response_page_follow_request(page, mode='accept'))
            case 'DELETE':
                serializer = serializer(response_page_follow_request(page, mode='deny'))

        return Response(serializer.data, status=status_code)


class PostsViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    All methods for manipulating Post objects.
    """
    permission_classes_map = {'list': (AllowAny,)}
    default_permission_classes = (IsAuthenticated,)
    serializer_map = {
                      'delete_post': RetrievePostSerializer,
                      'update_my_post': UpdatePostSerializer,
                      'create': UpdatePostSerializer,
                      }
    default_serializer = ListRetrievePostSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        return [permission() for permission in
                self.permission_classes_map.get(self.action, self.default_permission_classes)]

    def get_queryset(self):
        """
        Return queryset based on request method.
        """
        user = self.request.user
        match self.action:
            case 'manager_posts_view':
                return Post.objects.all()
            case 'get_my_posts' | 'update_my_post' | 'delete_my_post' | 'retrieve_my_post':
                return Post.posts_objects.get_user_posts(user.id)
            case 'liked_posts':
                return Post.posts_objects.get_liked_posts(user)
            case 'feed':
                return Post.posts_objects.get_feed_posts(user)

        return Post.posts_objects.get_valid_posts()

    def get_serializer_class(self, *args, **kwargs):
        """
        Return serializer class based on request method.
        """
        return self.serializer_map.get(self.action, self.default_serializer)

    def create(self, request, *args, **kwargs):
        """
        Create post and send notification email to the page's followers.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.validated_data['title']
        serializer.save()

        result_info = send_email(request, post)
        data = {'data': serializer.data, 'info': result_info}
        return Response(data, status=HTTP_201_CREATED)

    def perform_update(self, serializer):
        """
        Like a post.
        """
        post = self.get_object()
        like_post(self.request, post)

        return Response(status=HTTP_200_OK)

    @action(methods=('get', 'delete'), detail=True, url_path='admin', permission_classes=(IsAdminUser | IsModerator))
    def delete_post(self, request, pk=None):
        """
        Allow admins and moderators manage posts.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid()
        delete_object(instance)
        serializer.save()
        return Response(serializer.data, status=HTTP_204_NO_CONTENT)

    @action(methods=('get',), detail=False, url_path='my')
    def get_my_posts(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=('get',), detail=True, url_path='my')
    def retrieve_my_post(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=HTTP_200_OK)

    @retrieve_my_post.mapping.delete
    def delete_my_post(self, request, pk=None):
        instance = self.get_object()
        delete_object(instance)

        return Response(status=HTTP_204_NO_CONTENT)

    @retrieve_my_post.mapping.put
    def update_my_post(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=('get',), detail=False, url_path='my/liked')
    def liked_posts(self, request):
        """
        List user's liked posts.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=('get',), detail=False, url_path='my/feed')
    def feed(self, request):
        """
        Implement feed by filtering followed and owned posts.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
