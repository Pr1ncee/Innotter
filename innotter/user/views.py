from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .models import User
from .serializers import AdminUserSerializer


class AdminUserViewSet(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    Allow administrators manage users.
    """
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()
