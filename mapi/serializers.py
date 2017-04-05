from rest_framework import serializers

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard

from mapi.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    board = serializers.ReadOnlyField(source='mapi.title')

    class Meta:
        model = Article
        fields = ('id', 'user', 'mapi', 'title', 'views', 'likes', 'created_at')


class ArticleAddSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=DonkeyUser.objects.all())
    board = serializers.PrimaryKeyRelatedField(queryset=BulletinBoard.objects.all())

    class Meta:
        model = Article
        fields = ('id', 'user', 'mapi', 'title', 'content', 'created_at', 'modified_at', 'views', 'yellow_cards', 'likes')


class ArticleDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    board = serializers.ReadOnlyField(source='mapi.title')

    class Meta:
        model = Article
        fields = ('id', 'user', 'mapi', 'title', 'content', 'created_at', 'modified_at', 'views', 'yellow_cards', 'likes')
