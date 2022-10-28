from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Check out if the user is Moderator returns True, otherwise - False.
    """
    def has_permission(self, request, view):
        moderator = request.user.Roles.MODERATOR
        return bool(request.user and request.user.role == moderator)
