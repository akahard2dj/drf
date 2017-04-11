from django.http import HttpResponse
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import (api_view, permission_classes, authentication_classes)
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
from mapi.permissions import IsBoraApiAuthenticated
from mapi import permissions as bora_permissions

from core.json.response_wrapper import DonkeyJsonResponse
from core.models.donkey_user import DonkeyUser
from core.models.bulletin_board import BulletinBoard
from core.models.connector import UserBoardConnector
from core.models.category import *
from core.utils import UserCrypto
from core.authentication import BoraApiAuthentication

from core.celery_email import Mailer
from core.utils import random_number

from celery import shared_task


def is_access_to_board(func):
    class Wrapper(object):
        def __init__(self):
            self.user_id = None
            self.board_id = None

        def __call__(self, *args, **kwargs):
            func(*args)

            user_board_connector = UserBoardConnector.objects.get(donkey_user_id=self.user_id)
            return user_board_connector.check_bulletinboard_id(self.board_id)
    return Wrapper()


@is_access_to_board
def check_board(user_id, board_id):
    check_board.user_id = user_id
    check_board.board_id = board_id


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
    is_token_key = request.method == 'GET' and 'token' in request.GET
    if is_token_key:
        token = request.GET['token']

        if Token.objects.filter(key=token).exists():
            token = Token.objects.get(key=token)
            donkey_user = token.user
            donkey_user.update_last_login()
            res = {'msg': 'sucess',
                    'code': '200',
                    'data': {'result': True}}
            return Response(res, status=status.HTTP_200_OK)
        else:
            res = {'msg': 'Invalid Token',
                    'code': '200',
                    'data': {'result': False}}

            return Response(res, status=status.HTTP_200_OK)
    else:
        res = {'msg': 'failed',
                'code': '200',
                'data': {'result': False}}
        return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def email_check(request):
    is_email = request.method == 'GET' and 'email' in request.GET
    if is_email:
        email = request.GET['email']

        try:
            validators.validate_email(email)
        except validators.ValidationError:
            res = {
                'code': '200',
                'msg': 'failed',
                'detail': 'Invalid email address',
                'data': {
                    'is_valid': False,
                    'msg': '잘못된 이메일',
                    'name': ''
                }
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            domain = email.split('@')[-1]
            try:
                university = University.objects.get(domain=domain)
            except University.DoesNotExist:
                res = {
                    'code': '200',
                    'msg': 'failed',
                    'detail': 'No service University',
                    'data': {
                        'is_valid': False,
                        'msg': '현재 서비스를 하지 않는 대학교',
                        'name': ''
                    }
                }

                return Response(res, status=status.HTTP_200_OK)
            else:
                res = {
                    'code': '200',
                    'msg': 'success',
                    'detail': 'Service University',
                    'data': {
                        'is_valid': True,
                        'msg': 'Service University',
                        'name': university.name
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

    else:
        res = {
            'code': '400',
            'msg': 'failed',
            'detail': 'No email field'
        }
        return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def gen_auth_key(request):
    is_email_key = request.method == 'GET' and 'email' in request.GET

    if is_email_key:
        key_email = request.GET['email']
        try:
            validators.validate_email(key_email)
        except validators.ValidationError:
            res = {
                'msg': 'failed',
                'code': '200',
                'detail': 'Invalid Email',
                'data': {
                    'is_sent': False,
                    'msg': '잘못된 이메일',
                }
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            if cache.get(key_email):
                res = {
                    'msg': 'failed',
                    'code': '200',
                    'detail': 'Processing authentication, check the email',
                    'data': {
                        'is_sent': True,
                        'msg': '이미 인증 메일이 발송되었습니다'
                    }
                }
                return Response(res, status=status.HTTP_200_OK)
            else:
                auth_code = random_number()
                # TODO : when deply to real service, MUST BE CHANGED "test1234" to auth_code
                cache_data = {'code': "1234", 'status': 'SENT', 'user_type': ''}
                cache.set(key_email, cache_data, timeout=300)
                #m = Mailer()
                #m.send_messages('Authorization Code', auth_code, [key_email])
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'authorization email is sent',
                    'data': {
                        'is_sent': True,
                        'msg': '인증 메일이 발송되었습니다',
                    }
                }

                return Response(res, status=status.HTTP_200_OK)
    else:
        res = {'msg': 'failed',
               'code': '400',
               'detail': 'Not enough input fields'}
        return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def confirm_auth_key(request):
    crypto = UserCrypto()
    is_email_key = request.method == 'GET' and 'email' in request.GET
    is_authcode_key = request.method == 'GET' and 'auth_code' in request.GET

    if is_email_key and is_authcode_key:
        key_email = request.GET['email']
        auth_code = request.GET['auth_code']
    else:
        res = {'msg': 'failed',
               'code': '400',
               'detail': 'Not enough input fields'}
        return Response(res, status=status.HTTP_200_OK)

    value_from_cache = cache.get(key_email)

    if not value_from_cache:
        res = {
            'msg': 'failed',
            'code': '200',
            'detail': 'There is no credential information in cache',
            'data': {
                'is_confirm': False,
                'msg': '재인증이 필요합니다',
            }
        }
        return Response(res, status=status.HTTP_200_OK)

    else:
        if auth_code == value_from_cache['code']:
            encrypted_email = crypto.encode(key_email)

            if DonkeyUser.objects.filter(email=encrypted_email).exists():
                encrypted_email = crypto.encode(key_email)
                user = DonkeyUser.objects.get(email=encrypted_email)
                token = Token.objects.get(user_id=user.id)
                # deleting caching
                if cache.get(token.key):
                    cache.delete(token.key)

                token.delete()
                new_token = Token.objects.create(user=user)
                cache.delete(key_email)


                #value_from_cache['status'] = 'CONFIRM'
                #value_from_cache['user_type'] = 'exist_user'
                #cache.set(key_email, value_from_cache, timeout=600)
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'existed_user',
                    'data': {
                        'is_confirm': True,
                        'is_exist': True,
                        'msg': '기존의 유저입니다',
                        'token': new_token.key
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

            else:
                value_from_cache['status'] = 'CONFIRM'
                value_from_cache['user_type'] = 'new_user'
                cache.set(key_email, value_from_cache, timeout=600)
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'new_user',
                    'data': {
                        'is_confirm': True,
                        'is_exist': False,
                        'msg': '새로운 유저입니다'
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

        else:
            res = {
                'msg': 'failed',
                'code': '200',
                'detail': 'Invalid authorization code',
                'data': {
                    'is_confirm': False,
                    'msg': '잘못된 인증번호 입니다'
                }
            }
            return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['POST'])
def registration(request):
    crypto = UserCrypto()
    is_email_key = request.method == 'POST' and 'email' in request.data
    is_authcode_key = request.method == 'POST' and 'auth_code' in request.data

    if is_email_key and is_authcode_key:
        key_email = request.data['email']
        auth_code = request.data['auth_code']
    else:
        res = {'msg': 'failed',
               'code': '400',
               'detail': 'Not enough input fields'}
        return Response(res, status=status.HTTP_200_OK)

    value_from_cache = cache.get(key_email)

    if not value_from_cache:
        res = {
            'msg': 'failed',
            'code': '200',
            'detail': 'There is no credential information in cache',
            'data': {
                'is_register': False,
                'msg': '재인증이 필요합니다',
            }
        }
        return Response(res, status=status.HTTP_200_OK)

    else:
        if auth_code == value_from_cache['code']:
            # new user
            if value_from_cache['user_type'] == 'new_user':
                user = DonkeyUser()
                try:
                    user.user_save(key_email=key_email)
                except validators.ValidationError as e:
                    res = {
                        'msg': 'failed',
                        'code': '200',
                        'detail': 'DonkeyUser: {}'.format(e),
                        'data': {
                            'is_register': False,
                            'msg': '현재 서비스를 하지 않는 대학교',
                        }
                    }
                    return Response(res, status=status.HTTP_200_OK)

                # bulletin searching
                joined_bulletins = BulletinBoard.objects.filter(university=user.university)
                _ = UserBoardConnector.objects.create(donkey_user=user)
                connector_btw_user_board = UserBoardConnector.objects.get(donkey_user=user)

                # default board
                connector_btw_user_board.set_bulletinboard_id(1)

                for bulletin in joined_bulletins:
                    connector_btw_user_board.set_bulletinboard_id(bulletin.id)

                token = Token.objects.get(user=user)
                cache.delete(key_email)
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'correctly data is saved in db',
                    'data': {
                        'is_register': True,
                        'token': token.key,
                        'msg': '성공적으로 가입 되었습니다'
                    }
                }
                return Response(res, status=status.HTTP_200_OK)
            # existing user
            if value_from_cache['user_type'] == 'exist_user':
                encrypted_email = crypto.encode(key_email)
                user = DonkeyUser.objects.get(email=encrypted_email)
                token = Token.objects.get(user_id=user.id)
                #deleting caching
                if cache.get(token.key):
                    cache.delete(token.key)

                token.delete()
                new_token = Token.objects.create(user=user)
                cache.delete(key_email)
                res = {
                    'msg': 'success',
                    'code': '200',
                    'detail': 'correctly data is saved in db',
                    'data': {
                        'is_register': True,
                        'token': new_token.key,
                        'msg': '성공적으로 재발급 되었습니다'
                    }
                }
                return Response(res, status=status.HTTP_200_OK)

        else:
            res = {
                'msg': 'failed',
                'code': '200',
                'detail': 'Invalid authorization code',
                'data': {
                    'is_register': False,
                    'msg': '잘못된 인증번호 입니다'
                }
            }
            return Response(res, status=status.HTTP_200_OK)


class ArticleList(APIView):
    permission_classes = (
        #IsBoraApiAuthenticated,
        bora_permissions.ArticlesPermission,
    )
    authentication_classes = (
        BoraApiAuthentication,
    )

    @method_decorator(never_cache)
    def get(self, request, format=None):
        is_offset = request.method == 'GET' and 'offset' in request.GET
        is_page = request.method == 'GET' and 'page' in request.GET

        board_id = int(request.GET['board_id'])

        if is_offset:
            n_offset = int(request.GET['offset'])
        else:
            n_offset = 5

        if is_page:
            n_page = int(request.GET['page'])
        else:
            n_page = 1

        if n_page == 1:
            first_id = Article.objects.filter(board_id=board_id).first().id
        else:
            first_id = int(request.GET['last_id'])

        n_start = (n_page-1) * n_offset
        n_end = n_page * n_offset
        articles = Article.objects.filter(board_id=board_id).filter(id__lte=first_id).all()[n_start:n_end]
        
        # TODO: last page exception
        serializer = ArticleSerializer(articles, many=True)
        res = {
            'code': '200',
            'msg': 'success',
            'detail': 'articles list',
            'data': {
                'artilces': serializer.data,
                'board_id': board_id,
                'offset': n_offset,
                'page': n_page + 1,
                'first_id': first_id,
                'next_url': 'articles?board_id={}&paage={}&offset={}&last_id={}'
                    .format(board_id, n_page+1, n_offset, first_id)
            }
        }

        return Response(res, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        request_data = request.data
        is_title = 'title' in request_data
        is_content = 'content' in request_data
        is_board_id = request.method == 'POST' and 'board_id' in request.GET

        if is_title and is_content and is_board_id:
            items = request_data
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'Not enough fields',
            }
            return Response(res, status=status.HTTP_200_OK)

        items.update({'user': request.user.id})
        items.update({'board': request.GET['board_id']})

        serializer = ArticleAddSerializer(data=items)

        if serializer.is_valid():
            serializer.save()
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'article is saved'
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'serializer validation is failed'
            }
            return Response(res, status=status.HTTP_200_OK)


class ArticleDetail(APIView):
    permission_classes = (permissions.IsAuthenticated, )

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

        if check_board(request.user.id, request.data['board_id']):
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
        if check_board(request.user.id, request.data['board_id']):
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

        if check_board(request.user.id, request.data['board_id']):
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

    @method_decorator(never_cache)
    def get(self, request, article_pk, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data

        if not is_board_id:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        if check_board(request.user.id, request.data['board_id']):
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

        if check_board(request.user.id, request.data['board_id']):
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

    def post(self, request, article_pk, reply_pk, format=None):
        request_data = request.data
        is_board_id = 'board_id' in request_data
        is_content = 'content' in request_data

        if is_board_id and is_content:
            board_id = request.data['board_id']
            content = request.data['content']
        else:
            return Response({'msg': 'Not enough data'}, status=status.HTTP_400_BAD_REQUEST)

        if check_board(request.user.id, request.data['board_id']):
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

        if check_board(request.user.id, request.data['board_id']):
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

        if check_board(request.user.id, request.data['board_id']):
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
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'There is no user in db'
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            serializer = DonkeyUserSerializer(donkey_user)
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'User Information',
                'data': {
                    'user_info': serializer.data
                }
            }
            return Response(res, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        request_data = request.data
        is_nickname = 'nickname' in request_data

        if not is_nickname:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'Not enough data'
            }
            return Response(res, status=status.HTTP_200_OK)

        user_id = int(request.user.id)
        try:
            donkey_user = DonkeyUser.objects.get(pk=user_id)
        except DonkeyUser.DoesNotExist:
            res = {
                'code': '400',
                'msg': 'failed',
                'detail': 'There is no user in db'
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            donkey_user.nickname = request_data['nickname']
            donkey_user.save()
            res = {
                'code': '200',
                'msg': 'success',
                'detail': 'nickname is changed'
            }
            return Response(res, status=status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
def hello(request):
    data = {'message': 'hello'}
    return DonkeyJsonResponse('200', 'success', 'success', data, status.HTTP_200_OK)


@never_cache
@api_view(['GET'])
@authentication_classes((BoraApiAuthentication, ))
#@permission_classes((IsBoraApiAuthenticated, ))
def custom_auth_check(request):
    print(request.user)
    res = {
        'msg': 'success',
        'code': '200'
    }
    return Response(res, status=status.HTTP_200_OK)

