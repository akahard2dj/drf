from rest_framework import serializers
from rest_framework import permissions

from core.models import MyUser 
from core.models import GroupCategory
from board.models import Post
from board.permissions import IsOwnerOrReadOnly


class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    category = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Post
        fields = ('id', 'user', 'category', 'title',  'created_at', 'views')


class PostDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
    category = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Post
        fields = ('id', 'user', 'category', 'title', 'content', 'created_at', 'modified_at', 'views')


class PostAddSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=MyUser.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=GroupCategory.objects.all())

    class Meta:
        model = Post
        fields = ('id', 'user', 'category', 'title', 'content', 'created_at', 'modified_at', 'views')


class UserSerializer(serializers.ModelSerializer):
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'posts')


class UserDetailSerializer(serializers.ModelSerializer):
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())

    class Meta:
        model = MyUser
        fields = ('id', 'email', 'posts')
