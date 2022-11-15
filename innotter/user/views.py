from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from authorization.permissions import IsProfileOwner
from .models import User
from posts.enum_objects import Directory
from posts.services import save_image
from .serializers import AdminUserSerializer, ListUsersSerializer, UpdateUserSerializer


class AdminUserViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    Allow administrators manage users.
    """
    permission_map = {'list': (IsAuthenticated,),
                      'retrieve': (IsAdminUser,),
                      'retrieve_my_profile': (IsProfileOwner,),
                      'update': (IsAdminUser,),
                      'update_my_profile': (IsProfileOwner,),
                      'partial_update': (IsAdminUser,),
                      None: (IsAdminUser,)}
    serializer_map = {'list': ListUsersSerializer,
                      'retrieve': AdminUserSerializer,
                      'retrieve_my_profile': UpdateUserSerializer,
                      'update': AdminUserSerializer,
                      'update_my_profile': UpdateUserSerializer,
                      'partial_update': AdminUserSerializer,
                      }
    queryset = User.objects.all()
    filter_backends = (OrderingFilter, SearchFilter)
    ordering_fields = ('username',)
    search_fields = ('username',)

    def get_permissions(self):
        """
        Instantiate and return the tuple of permissions that this view requires.
        """
        return [permission() for permission in self.permission_map.get(self.action, None)]

    def get_serializer_class(self):
        """
        Return a serializer based on the request method.
        """
        return self.serializer_map.get(self.action, None)

    @action(methods=('get',), detail=True, url_path='profile')
    def retrieve_my_profile(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @retrieve_my_profile.mapping.put
    def update_my_profile(self, request, pk=None, *args, **kwargs):
        """
        Update user's profile by default.
        If image passed save it at AWS S3 and return url of the remote storage.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        image = request.FILES.get('image_path')
        if image:
            file_obj = serializer.validated_data.pop('image_path', None)
            file_url = save_image(file_obj, Directory.USERS)
            serializer.validated_data['image_path'] = file_url

        self.perform_update(serializer)
        return Response(serializer.data)
