from django.http import HttpResponse
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.core import validators

from mapi.models import Article
from mapi.models import ArticleReply
from mapi.serializers import ArticleSerializer
from mapi.serializers import ArticleAddSerializer
from mapi.serializers import ArticleDetailSerializer
from mapi.serializers import ArticleReplySerializer
from mapi.serializers import DonkeyUserSerializer

from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard
from core.models.connector import UserBoardConnector

from core.celery_email import Mailer
from core.utils import random_digit_and_number

from celery import shared_task


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
                user.user_save(key_email=key_email)
            except validators.ValidationError as e:
                return Response({'msg': 'Not service {}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)

            # bulletin searching
            joined_bulletins = BulletinBoard.objects.filter(university=user.university)
            _ = UserBoardConnector.objects.create(donkey_user=user)
            connector_btw_user_board = UserBoardConnector.objects.get(donkey_user=user)

            for bulletin in joined_bulletins:
                connector_btw_user_board.set_bulletinboard_id(bulletin.id)

            cache.delete(key_email)
            token = Token.objects.get(user=user)
            return Response({'msg': 'success', 'token': token.key}, status=status.HTTP_201_CREATED)
        else:
            return Response({'msg': 'invalid code'}, status=status.HTTP_401_UNAUTHORIZED)


class ArticleList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def check_bulletinboard(self, request):
        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
        return user_board_connector.check_bulletinboard_id(request.data['board_id'])

    @method_decorator(never_cache)
    def get(self, request, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data

        if is_board_id:
            board_id = request.data['board_id']
        else:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)

        if is_access:
            #articles = Article.objects.filter(board_id=board_id).exclude(status=2)
            articles = Article.objects.filter(board_id=board_id).all()
            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def post(self, request, format=None):
        request_data = request.data
        is_title = 'title' in request_data
        is_content = 'content' in request_data
        is_board_id = 'board_id' in request_data

        if is_title and is_content and is_board_id:
            items = request_data
        else:
            return Response({'msg': 'Not enough fields'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)

        if is_access:
            items.update({'user': request.user.id})
            items.update({'board': request_data['board_id']})

            serializer = ArticleAddSerializer(data=items)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ArticleAdd(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def check_bulletinboard(self, request):
        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
        return user_board_connector.check_bulletinboard_id(request.data['board_id'])

    def post(self, request, format=None):
        request_data = request.data
        is_title = 'title' in request_data
        is_content = 'content' in request_data
        is_board_id = 'board_id' in request_data

        if is_title and is_content and is_board_id:
            items = request_data
        else:
            return Response({'msg': 'Not enough fields'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)

        if is_access:
            items.update({'user': request.user.id})
            items.update({'board': request_data['board_id']})

            serializer = ArticleAddSerializer(data=items)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ArticleDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def check_bulletinboard(self, request):
        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
        return user_board_connector.check_bulletinboard_id(request.data['board_id'])

    def get_object(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({'msg': 'not found'}, status=status.HTTP_404_NOT_FOUND)

    @method_decorator(never_cache)
    def get(self, request, pk, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data

        if is_board_id:
            board_id = request.data['board_id']
        else:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)
        if is_access:
            article = self.get_object(pk)
            # status checking
            if article.status == 0:
                if int(board_id) != article.board_id:
                    return Response({'msg': 'abnormat request'}, status=status.HTTP_406_NOT_ACCEPTABLE)

                if request.user.id != article.user_id:
                    article.increase_view_count()
                serializer = ArticleDetailSerializer(article)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'invalid access'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request, pk):
        is_access = self.check_bulletinboard(request)
        if is_access:
            article = self.get_object(pk)
            if article.user == request.user:
                if article.status == 2:
                    return Response({'msg': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    article.status = 2
                    article.save()

                return Response({'msg': 'ok'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def put(self, request, pk):
        request_data = request.data
        is_title = 'title' in request_data
        is_content = 'content' in request_data
        is_board_id = 'board_id' in request_data

        if is_title and is_content and is_board_id:
            items = request_data
        else:
            return Response({'msg': 'Not enough fields'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)
        if is_access:
            article = self.get_object(pk)
            if article.user == request.user:
                items.update({'user': request.user.id})
                items.update({'board': request_data['board_id']})
                serializer = ArticleAddSerializer(data=items)
                if serializer.is_valid():
                    article.title = items['title']
                    article.content = items['content']
                    article.save()
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'msg': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ArticleReplyList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def check_bulletinboard(self, request):
        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
        return user_board_connector.check_bulletinboard_id(request.data['board_id'])

    @method_decorator(never_cache)
    def get(self, request, article_pk, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data

        if not is_board_id:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)
        if is_access:
            replies = ArticleReply.objects.filter(article_id=article_pk).all()

            serializer = ArticleReplySerializer(replies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def post(self, request, article_pk, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data
        is_content = 'content' in request_data

        if is_board_id and is_content:
            content = request.data['content']
        else:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)
        if is_access:
            reply = ArticleReply.add_root(
                content=content,
                article=Article.objects.get(pk=article_pk),
                user=DonkeyUser.objects.get(pk=request.user.id)
            )
            return Response({'msg': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ArticleReplyDetail(APIView):
    #TODO : need to be implemented of reply depth(initial condition : depth =3 --> reply(1) - reply(11) - reply(111)
    permission_classes = (permissions.IsAuthenticated, )

    def check_bulletinboard(self, request):
        user_board_connector = UserBoardConnector.objects.get(donkey_user_id=request.user.id)
        return user_board_connector.check_bulletinboard_id(request.data['board_id'])

    def post(self, request, article_pk, reply_pk, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data
        is_content = 'content' in request_data

        if is_board_id and is_content:
            board_id = request.data['board_id']
            content = request.data['content']
        else:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)
        if is_access:
            get_reply = lambda node_id: ArticleReply.objects.filter(article_id=article_pk).get(pk=node_id)
            sub_reply = get_reply(reply_pk).add_child(
                content=content,
                article_id=article_pk,
                user_id=request.user.id
            )
            return Response({'msg': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def put(self, request, article_pk, reply_pk, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data
        is_content = 'content' in request_data

        if is_board_id and is_content:
            content = request.data['content']
        else:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)
        if is_access:
            article_reply = ArticleReply.objects.get(pk=reply_pk)
            if request.user == article_reply.user:
                article_reply.content = content
                article_reply.save()
            else:
                return Response({'msg': 'Unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'msg': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request, article_pk, reply_pk, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data

        if not is_board_id:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        is_access = self.check_bulletinboard(request)
        if is_access:
            article_reply = ArticleReply.objects.get(pk=reply_pk)
            if request.user == article_reply.user:
                #TODO status naming
                article_reply.status = 2
                article_reply.save()
            else:
                return Response({'msg': 'Unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'msg': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid board id'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class UserDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @method_decorator(never_cache)
    def get(self, request, format=None):
        user_id = int(request.user.id)
        try:
            donkey_user = DonkeyUser.objects.get(pk=user_id)
        except DonkeyUser.DoesNotExist:
            return Response({'msg': 'invalid user id'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = DonkeyUserSerializer(donkey_user)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        request_data = request.data
        is_nickname = 'nickname' in request_data

        if not is_nickname:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = int(request.user.id)
        try:
            donkey_user = DonkeyUser.objects.get(pk=user_id)
        except DonkeyUser.DoesNotExist:
            return Response({'msg': 'invalid user id'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            donkey_user.nickname = request_data['nickname']
            donkey_user.save()
            return Response({'msg': 'success'}, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def hello(request):
    return HttpResponse('hello')
