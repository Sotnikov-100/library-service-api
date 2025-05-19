from rest_framework.permissions import BasePermission


class IsAdminOrOwner(BasePermission):
    """
    Allow full access to admin users.
    Non-admin can only view their own payments.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.borrowing.user == request.user

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
