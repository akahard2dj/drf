from django.contrib.auth import authenticate

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDictKeyError
from django.core.cache import cache

from board.models import Post
from board.permissions import IsOwnerOrReadOnly
from board.serializers import PostSerializer, PostDetailSerializer, PostAddSerializer
from board.serializers import UserSerializer, UserDetailSerializer

from core.models import MyUser
from core.models import GroupCategory
from core.celery_email import Mailer
from core.utils import random_digit_and_number

from celery import shared_task, task
from celery.result import ResultBase

@shared_task()
def add(x, y):
    return x+y

@api_view(['POST'])
def celery_test(request):
    #add.delay(10, 10)
    #data = {'code':'af32fjl', 'status':'SENT'}
    #cache.set('abc@abc.com', data)
    #value = cache.get('abc@abc.com')
    #if value:
    #    print(value)
    #value['status'] = 'CONFIRM'
    #cache.set('abc@abc.com', value)
    add.apply_async((10,10),)

    return Response({'msg': 'success'})

@api_view(['POST'])
def pre_check(request):
    data = request.data

    try:
        token = data['token']
    except MultiValueDictKeyError:
        return Response({'msg': 'No Token'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        token_user = Token.objects.get(key=token)
    except Token.DoesNotExist:
        return Response({'msg': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({'msg': 'success'}, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def gen_auth_key(request):
    data = request.data
    key = data['email']
    temp_value = random_digit_and_number(length_of_value=6)
    print(temp_value)
    if cache.get(key):
        return Response({'msg': 'processing Authorization, check the own email'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    else:
        cache_data = {'code': temp_value, 'status': 'SENT'}
        cache.set(key, cache_data, timeout=300)
        #m = Mailer()
        #m.send_messages('Authorization Code', temp_value, [key])

        return Response({'msg': 'success'}, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def confirm_auth_key(request):
    data = request.data
    auth_key = data['auth_key']
    key = data['email']
    value_from_cache = cache.get(key)
    if not value_from_cache:
        return Response({'msg': 'There is no credential information in cache'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        if auth_key == value_from_cache['code']:
            try:
                user_from_db = MyUser.objects.get(email=key)
            except MyUser.DoesNotExist:
                value_from_cache['status'] = 'CONFIRM'
                cache.set(key, value_from_cache, timeout=600)
                return Response({'msg': 'new user'}, status=status.HTTP_202_ACCEPTED)
            else:
                cache.delete(key)
                return Response({'msg': 'existed user'}, status=status.HTTP_202_ACCEPTED)

        else:
            return Response({'msg': 'failed'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def example_view(request, format=None):
    content = {
        'status': 'request was permitted'
    }
    return Response(content, status=status.HTTP_200_OK)


@api_view(['POST'])
def registration(request):
    data = request.data
    key = data['email']
    auth_key = data['auth_key']
    value_from_cache = cache.get(key)

    if not value_from_cache:
        return Response({'msg':'There is no credential information in cache'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        if auth_key == value_from_cache['code']:
            user = MyUser()
            user.nickname = random_digit_and_number()
            user.email = key
            user.save()
            cache.delete(key)
            return Response({'msg': 'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'msg': 'invalid code'}, status=status.HTTP_401_UNAUTHORIZED)


'''


    if request.method == 'POST':
        email = data['email']

        try:
            _ = MyUser.objects.get(email=email)

            return Response({'msg': 'failed'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        except MyUser.DoesNotExist:
            user = MyUser()
            user.email = email
            user.set_password('test1234')
            user.save()
            return Response({'msg': 'success'}, status=status.HTTP_200_OK)
'''
'''
@api_view(['POST'])
def registration_confirmation(request):
    if request.method == 'POST':
        data = request.data
        email = data['email']
        code = data['code']

        authenticated_user = authenticate(username=email, password=code)

        if authenticated_user:
            if authenticated_user.is_confirm is False:
                authenticated_user.is_confirm = True
                authenticated_user.save()
                token = Token.objects.get(user=authenticated_user)
                result = {'msg': 'success', 'token': token.key}

                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'token has already issued'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'msg': 'failed'}, status=status.HTTP_401_UNAUTHORIZED)
'''

class PostList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def check_category(self, request):
        current_user = MyUser.objects.get(pk=request.user.id)
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
class UserDetail(generics.RetrieveAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserDetailSerializer
    permissions_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly,)
'''
