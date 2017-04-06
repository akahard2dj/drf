from rest_framework import serializers

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard

from mapi.models import Article
from mapi.models import ArticleReply


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    board = serializers.ReadOnlyField(source='board.title')
    title = serializers.SerializerMethodField('custom_board_title')

    class Meta:
        model = Article
        fields = ('id', 'user', 'board', 'title', 'views', 'likes', 'created_at')

    def custom_board_title(self, obj):
        if obj.status == 0:
            return (obj.title)
        if obj.status == 1:
            return ('신고된 글 입니다')
        if obj.status == 2:
            return ('삭제된 글 입니다')


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

    class Meta:
        model = ArticleReply
        fields = ('id', 'user', 'content', 'depth', 'status', 'created_at', 'modified_at')

    def custom_content_name(self, obj):
        if obj.status == 0:
            return (obj.content)
        if obj.status == 1:
            return ('신고된 댓글 입니다')
        if obj.status == 2:
            return ('삭제된 댓글 입니다')

class DonkeyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonkeyUser
        fields = ('id', 'username', 'nickname', 'last_login')

    def get_information(self, obj):
        return (obj.nickname)