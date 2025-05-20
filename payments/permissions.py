from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrOwner(BasePermission):
    """
    Allow full access to admin users.
    Non-admin can only view their own payments.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.borrowing.user == request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_staff
