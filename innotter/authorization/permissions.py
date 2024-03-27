from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Check out if given user is Moderator or not (True/False).
    """
    def has_permission(self, request, view):
        moderator = request.user.Roles.MODERATOR
        return request.user and request.user.role == moderator


class IsProfileOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Whether the user is authenticated
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Whether the profile page is owned by the user who made the request.
        """
        return obj.id == request.user.id
