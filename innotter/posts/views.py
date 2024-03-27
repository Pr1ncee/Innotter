from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework import viewsets, mixins

from authorization.permissions import IsModerator
from posts.models import Page, Post
from posts.enum_objects import Mode, Directory, PostMethods
from posts.serializers import (
    CreateUpdatePagesSerializer,
    ListUpdateMyPagesSerializer,
    DeletePageTagsSerializer,
    UpdatePageFollowersSerializer,
    UpdatePageFollowRequestsSerializer,
    ListRetrievePostSerializer,
    UpdatePostSerializer,
    UpdateBlockPageSerializer,
    RetrievePostSerializer
)
from posts.services import (
    create_page,
    update_page,
    follow_page,
    response_page_follow_request,
    destroy_page_tag,
    like_post,
    delete_object,
    send_email,
    save_image,
    publish_post
)


class PagesViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    All methods for managing Page objects.
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
    permission_map = {'list': (AllowAny,)}
    default_permission_classes = (IsAuthenticated,)
    filter_backends = (OrderingFilter, SearchFilter)
    ordering_fields = ('name', 'uuid')
    search_fields = ('name', 'uuid', 'tags__name')

    def get_permissions(self):
        """
        Instantiate and return the tuple of permissions that this view requires.
        """
        return [permission() for permission in
                self.permission_map.get(self.action, self.default_permission_classes)]

    def get_queryset(self):
        """
        Return a queryset based on the request method.
        """
        match self.action:
            case 'manager_pages_view':
                return Page.objects.all()
            case 'get_my_pages' | 'retrieve_my_page' | 'delete_my_page' \
                 | 'delete_my_page' | 'update_my_page' | 'tags' | 'follow_requests':
                user_id = self.request.user.id
                return Page.pages_objects.get_user_pages(user_id)

        pk = self.kwargs.get('pk')
        if not pk:
            return Page.pages_objects.get_valid_pages()

        return Page.pages_objects.get_all_valid_pages()

    def get_serializer_class(self):
        """
        Return a serializer class based on the request method.
        """
        return self.serializer_map.get(self.action, None)

    def create(self, request, *args, **kwargs):
        """
        Create a new page.
        Use specific method to update page's tags as 'tags' field has MTM relationship.
        In addition, if image sent save it at AWS S3 and update page's 'image' field with image's url at S3.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = serializer.data
        data = serializer.validated_data
        tags = data.pop('tags')
        image = request.FILES.get('image')
        file_url = None
        if image:
            file_obj = serializer.validated_data.pop('image', None)
            file_url = save_image(file_obj, Directory.PAGES)

        page_id = create_page(data, tags, file_url)
        response['id'] = page_id
        response['image'] = file_url
        return Response(response, status=HTTP_201_CREATED)

    def perform_update(self, serializer):
        """
        Follow a page.
        """
        page = self.get_object()
        follow_page(self.request, page)

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
        delete_object(instance, pk=pk)

        return Response(status=HTTP_204_NO_CONTENT)

    @retrieve_my_page.mapping.put
    def update_my_page(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data.pop('image', None)
        tags_list = serializer.validated_data.pop('tags', None)

        update_page(tags_list, file_obj, instance, Directory.PAGES, serializer)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=('get', 'delete'), detail=True, url_path='my/tags')
    def tags(self, request, pk=None):
        """
        Delete last tag in tags list of Page object.
        """
        instance = self.get_object()
        if request.method == 'DELETE':
            serializer = self.get_serializer(destroy_page_tag(instance))
            return Response(serializer.data, status=HTTP_200_OK)

        serializer = self.get_serializer(instance)
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
                serializer = serializer(response_page_follow_request(page, mode=Mode.ACCEPT))
            case 'DELETE':
                serializer = serializer(response_page_follow_request(page, mode=Mode.DENY))

        return Response(serializer.data, status=status_code)


class PostsViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    All methods for managing Post objects.
    """
    permission_map = {'list': (AllowAny,)}
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
                self.permission_map.get(self.action, self.default_permission_classes)]

    def get_queryset(self):
        """
        Return a queryset based on the request method.
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
        Return a serializer class based on the request method.
        """
        return self.serializer_map.get(self.action, self.default_serializer)

    def perform_create(self, serializer):
        """
        Create a post and send notification email to the page's followers.
        """
        send_email(self.request, serializer)

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
        Allow admins and moderators delete posts.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid()

        delete_object(instance, serializer, pk=pk, is_post=True)
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

        delete_object(instance, pk=pk, is_post=True)
        return Response(status=HTTP_204_NO_CONTENT)

    @retrieve_my_post.mapping.put
    def update_my_post(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        post = serializer.validated_data

        serializer.save()
        liked_by = len(serializer.data['liked_by'])
        publish_post(post, PostMethods.UPDATE, pk=pk, liked_by=liked_by)
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
