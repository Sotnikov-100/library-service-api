from rest_framework import permissions

class IsAuthenticatedOnly(permissions.BasePermission):
    '''
    The user is authenticated.
    '''

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated
        )
