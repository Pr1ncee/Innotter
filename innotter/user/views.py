from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import User
from .serializers import AdminUserSerializer, ListUsersSerializer


class AdminUserViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    Allow administrators manage users.
    """
    permission_map = {'retrieve': (IsAdminUser,),
                      'update': (IsAdminUser,),
                      'list': (IsAuthenticated,),
                      'partial_update': (IsAdminUser,),
                      None: (IsAdminUser,)}
    serializer_map = {'list': ListUsersSerializer,
                      'retrieve': AdminUserSerializer,
                      'update': AdminUserSerializer,
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
        Return serializer based on request method.
        """
        return self.serializer_map.get(self.action, None)
