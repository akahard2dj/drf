from rest_framework import permissions
from django.contrib.auth.models import AnonymousUser

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard
from core.models.connector import UserBoardConnector
from core.models.category import *


class IsBoraApiAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        is_auth = request.user and request.user.is_authenticated()
        return is_auth


class IsBoardOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
        try:
            board_id = request.GET['board_id']
        except KeyError:
            return False

        return user_board_connector.check_bulletinboard_id(board_id)


class ArticlesPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
            try:
                board_id = int(request.GET['board_id'])
            except KeyError:
                return False
            user = DonkeyUser.objects.get(email=request.user)

            return not user.is_reported and user_board_connector.check_bulletinboard_id(board_id)

        if request.method == 'GET':
            if int(request.GET['board_id']) == 1:
                return True
            else:
                if request.user == AnonymousUser():
                    return False
                else:
                    user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
                    try:
                        board_id = request.GET['board_id']
                    except KeyError:
                        return False

                    return user_board_connector.check_bulletinboard_id(board_id)


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