from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
from django.views.decorators.cache import (cache_page, never_cache)
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from django.core.cache import cache
from django.core import validators

#from board.models import Post
#from board.serializers import PostSerializer, PostDetailSerializer, PostAddSerializer
#from board.serializers import UserSerializer, UserDetailSerializer

from core.models.donkey_user import DonkeyUser
from core.models.category import (University, Department)
from core.models.name_tag import NameTag
from core.models.bulletin_board import BulletinBoard
from core.models.connector import Connector
from core.celery_email import Mailer
from core.utils import random_digit_and_number

from celery import shared_task

from django.utils import timezone


@shared_task()
def add(x, y):
    return x+y


@api_view(['POST'])
def celery_test(request):
    add.apply_async((10, 10),)

    return Response({'msg': 'success'})


@never_cache
@api_view(['GET'])
def pre_check(request):
    request_data = request.data

    is_token_key = 'token' in request_data
    if is_token_key:
        token = request_data['token']

        if Token.objects.filter(key=token).exists():
            token = Token.objects.get(key=token)
            donkey_user = token.user
            donkey_user.update_last_login()

            return Response({'msg': 'success'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'msg': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'msg': 'No Token'}, status=status.HTTP_401_UNAUTHORIZED)


@never_cache
@api_view(['GET'])
def gen_auth_key(request):
    request_data = request.data

    is_email_key = 'email' in request_data
    if is_email_key:
        key_email = request_data['email']
        try:
            validators.validate_email(key_email)
        except validators.ValidationError:
            return Response({'msg': 'Invalid Email'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if cache.get(key_email):
                return Response({'msg': 'processing Authorization, check the own email'},
                                status=status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                auth_code = random_digit_and_number(length_of_value=6)
                print(auth_code)
                cache_data = {'code': auth_code, 'status': 'SENT'}
                cache.set(key_email, cache_data, timeout=300)
                # m = Mailer()
                # m.send_messages('Authorization Code', temp_value, [key])

                return Response({'msg': 'success'}, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({'msg': 'No Email'}, status=status.HTTP_406_NOT_ACCEPTABLE)


@never_cache
@api_view(['GET'])
def confirm_auth_key(request):
    request_data = request.data

    is_email_key = 'email' in request_data
    is_authcode_key = 'auth_code' in request_data

    if is_email_key and is_authcode_key:
        key_email = request_data['email']
        auth_code = request_data['auth_code']
    else:
        return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

    value_from_cache = cache.get(key_email)

    if not value_from_cache:
        return Response({'msg': 'There is no credential information in cache'}, status=status.HTTP_401_UNAUTHORIZED)

    else:
        if auth_code == value_from_cache['code']:
            if DonkeyUser.objects.filter(email=key_email).exists():
                cache.delete(key_email)
                return Response({'msg': 'existed user'}, status=status.HTTP_202_ACCEPTED)
            else:
                value_from_cache['status'] = 'CONFIRM'
                cache.set(key_email, value_from_cache, timeout=600)
                return Response({'msg': 'new user'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'msg': 'failed'}, status=status.HTTP_401_UNAUTHORIZED)


@never_cache
@api_view(['GET'])
def registration(request):
    request_data = request.data

    is_email_key = 'email' in request_data
    is_authcode_key = 'auth_code' in request_data

    if is_email_key and is_authcode_key:
        key_email = request_data['email']
        auth_code = request_data['auth_code']
    else:
        return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

    value_from_cache = cache.get(key_email)

    if not value_from_cache:
        return Response({'msg': 'There is no credential information in cache'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        if auth_code == value_from_cache['code']:
            user = DonkeyUser()
            try:
                user.save(key_email=key_email)
            except validators.ValidationError as e:
                return Response({'msg': 'Not service {}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)

            # bulletin searching
            joined_bulletins = BulletinBoard.objects.filter(university=user.university)
            _ = Connector.objects.create(donkey_user=user)
            connector_btw_user_board = Connector.objects.get(donkey_user=user)

            for bulletin in joined_bulletins:
                connector_btw_user_board.set_bulletinboard_id(bulletin.id)

            cache.delete(key_email)
            token = Token.objects.get(user=user)
            return Response({'msg': 'success', 'token': token.key}, status=status.HTTP_201_CREATED)
        else:
            return Response({'msg': 'invalid code'}, status=status.HTTP_401_UNAUTHORIZED)




    '''
class PostList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def check_category(self, request):
        current_user = DonkeyUser.objects.get(pk=request.user.id)
        try:
            _ = current_user.category.get(id=request.data['category_code'])
        except GroupCategory.DoesNotExist:
            return False

        return True

    @method_decorator(never_cache)
    def get(self, request, format=None):
        is_access = self.check_category(request)

        if is_access:
            posts = Post.objects.filter(category=request.data['category_code'])
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid category code'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class PostAdd(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, format=None):
        item = request.data
        current_user = MyUser.objects.get(pk=request.user.id)
        try:
            _ = current_user.category.get(id=request.data['category_code'])
        except GroupCategory.DoesNotExist:
            return Response({'msg': 'Invalid category code'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        item.update({'user': request.user.id})
        item.update({'category': request.data['category_code']})
        serializer = PostAddSerializer(data=item)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def check_category(self, request):
        current_user = MyUser.objects.get(pk=request.user.id)
        try:
            _ = current_user.category.get(id=request.data['category_code'])
        except GroupCategory.DoesNotExist:
            return False

        return True

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'msg': 'failed'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, format=None):
        is_access = self.check_category(request)

        if is_access:
            post = self.get_object(pk)
            if request.user.id != post.user_id:
                view_count = post.views
                post.views = view_count + 1
                post.save()
            serializer = PostDetailSerializer(post)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'msg': 'Invalid category code'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def put(self, request, pk):
        is_access = self.check_category(request)

        if is_access:
            post = self.get_object(pk)
            item = request.data
            item.update({'user': request.user.id})

            serializer = PostDetailSerializer(data=item)
            if serializer.is_valid():
                post.title = item['title']
                post.content = item['content']
                post.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'Invalid category code'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request, pk):
        is_access = self.check_category(request)

        if is_access:
            post = self.get_object(pk)
            post.delete()
            return Response({'msg': 'success'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'msg': 'Invalid category code'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):
        user = MyUser.objects.get(email=request.user)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    '''
