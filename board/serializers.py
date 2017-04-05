from rest_framework import serializers

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard

from board.models import Article
from board.models import ArticleReply


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    board = serializers.ReadOnlyField(source='board.title')

    class Meta:
        model = Article
        fields = ('id', 'user', 'board', 'title', 'views', 'likes', 'created_at')


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


class DonkeyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonkeyUser
        fields = ('id', 'username')


class ArticleReplySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')

    class Meta:
        model = ArticleReply
        fields = ('id', 'user', 'content', 'depth', 'created_at', 'modified_at')
