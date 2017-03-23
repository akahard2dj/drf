from rest_framework import serializers
from rest_framework import permissions

#from django.contrib.auth.models import User
from core.models import MyUser
from board.models import Post
from board.permissions import IsOwnerOrReadOnly


class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = Post
        fields = ('id', 'owner', 'title',  'created_at', 'views')


class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'created_at', 'modified_at', 'views')


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
