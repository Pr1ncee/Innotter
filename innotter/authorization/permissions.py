from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Check out if given user is Moderator or not (True/False).
    """
    def has_permission(self, request, view):
        moderator = request.user.Roles.MODERATOR
        return request.user and request.user.role == moderator
