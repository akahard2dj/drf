from rest_framework import permissions
from core.authentication import BoraApiAuthentication

class IsBoraApiAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        a = BoraApiAuthentication()
        try:
            _ = request.META['HTTP_X_TOKEN']
        except KeyError:
            return False
        (user, is_auth) = a.authenticate(request)
        return is_auth


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        #if request.method in permissions.SAFE_METHODS:
        #    return True
        print(obj.owner, request.user)
        return request.user == obj


class IsDeleteAndIsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_owner = request.user == obj
        is_delete = request.method == 'DELETE'

        return is_owner and is_delete


class IsPostAndIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            is_post = True
        else:
            is_post = False

        is_auth = request.user and request.user.is_authenticated()

        return is_post and is_auth
