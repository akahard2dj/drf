from django.contrib.auth import authenticate

from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from board.models import Post
from board.permissions import IsOwnerOrReadOnly
from board.serializers import PostSerializer, PostDetailSerializer
from board.serializers import UserSerializer, UserDetailSerializer

from core.models import MyUser

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def example_view(request, format=None):
    content = {
        'status': 'request was permitted'
    }
    return Response(content, status=status.HTTP_200_OK)


@api_view(['POST'])
def registration(request):
    if request.method == 'POST':
        data = request.data
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


class PostList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    '''
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    '''


class PostAdd(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, format=None):
        item = request.data
        item.update({'owner': request.user.id})

        serializer = PostDetailSerializer(data=item)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'msg': 'failed'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        if request.user.id != post.owner_id:
            view_count = post.views
            post.views = view_count + 1
            post.save()
        serializer = PostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def put(self, request, pk):
        post = self.get_object(pk)
        item = request.data
        item.update({'owner': request.user.id})

        serializer = PostDetailSerializer(data=item)
        if serializer.is_valid():
            post.title = item['title']
            post.content = item['content']
            post.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        post = self.get_object(pk)
        post.delete()
        return Response({'msg': 'success'}, status=status.HTTP_202_ACCEPTED)


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
