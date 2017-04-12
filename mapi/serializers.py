from django.utils import timezone

from rest_framework import serializers

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard
from core.models.category import *

from mapi.models import Article
from mapi.models import ArticleReply


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    board = serializers.ReadOnlyField(source='board.title')
    title = serializers.SerializerMethodField('custom_board_title')
    created_at = serializers.SerializerMethodField('localtime_created_at')

    class Meta:
        model = Article
        fields = ('id', 'user', 'board', 'title', 'views', 'likes', 'created_at')

    @staticmethod
    def custom_board_title(obj):
        if obj.status == 0:
            return obj.title
        if obj.status == 1:
            return '신고된 글 입니다'
        if obj.status == 2:
            return '삭제된 글 입니다'

    @staticmethod
    def localtime_created_at(obj):
        return timezone.localtime(obj.created_at)


class ArticleAddSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=DonkeyUser.objects.all())
    board = serializers.PrimaryKeyRelatedField(queryset=BulletinBoard.objects.all())

    class Meta:
        model = Article
        fields = ('id', 'user', 'board', 'title', 'content', 'created_at', 'modified_at', 'views', 'yellow_cards', 'likes')


class ArticleDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    board = serializers.ReadOnlyField(source='board.title')

    class Meta:
        model = Article
        fields = ('id', 'user', 'board', 'title', 'content', 'created_at', 'modified_at', 'views', 'yellow_cards', 'likes')


class ArticleReplySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    content = serializers.SerializerMethodField('custom_content_name')
    created_at = serializers.SerializerMethodField('localtime_created_at')
    modified_at = serializers.SerializerMethodField('localtime_modified_at')

    class Meta:
        model = ArticleReply
        fields = ('id', 'user', 'content', 'depth', 'status', 'created_at', 'modified_at')

    @staticmethod
    def custom_content_name(obj):
        if obj.status == 0:
            return obj.content
        if obj.status == 1:
            return '신고된 댓글 입니다'
        if obj.status == 2:
            return '삭제된 댓글 입니다'

    @staticmethod
    def localtime_created_at(obj):
        return timezone.localtime(obj.created_at)

    @staticmethod
    def localtime_modified_at(obj):
        return timezone.localtime(obj.modified_at)


class DonkeyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonkeyUser
        fields = ('id', 'username', 'nickname', 'last_login')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name')


class BulletinBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulletinBoard
        fields = ('id', 'title', 'desc')
