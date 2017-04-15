from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from mapi import views

urlpatterns = [
    # pre-check : token check
    url(r'^preCheck$', views.pre_check, name='pre-check'),
    url(r'^init$', views.InitDonkey.as_view(), name='init-donkey'),

    # email-check : email validation and getting a name of a university
    url(r'^emailCheck$', views.email_check, name='email-check'),

    # department : providing a data of department
    url(r'^departments', views.get_departments, name='department'),

    # gen-auth-key : temporally generating key in cache
    # confirm-auth-key : authenticating email code in cache
    url(r'^genAuthKey$', views.gen_auth_key, name='gen-auth-key'),
    url(r'^isExistUser', views.is_exist_user, name='is-exist-user'),
    url(r'^confirmAuthKey$', views.confirm_auth_key, name='confirm-auth-key'),

    # registration : user registration
    url(r'^registration/$', views.registration, name='registration'),


    # new url mapping
    # providing a list of articles
    url(r'^boards/(?P<board_pk>[0-9]+)$', views.ArticleList.as_view(), name='list_articles'),
    url(r'^boards/(?P<board_pk>[0-9]+)/articles/(?P<article_pk>[0-9]+)$', views.ArticleDetail.as_view(), name='detail-article'),

    # articles : listing articles
    # articles-add : adding an article
    url(r'^articles$', views.ArticleList.as_view(), name='articles'),
    #url(r'^articleDetail/(?P<article_pk>[0-9]+)/boardId/(?P<board_id>[0-9]+)$', views.ArticleDetail.as_view(), name='articles'),
    url(r'^articleDetail/(?P<article_pk>[0-9]+)$', views.ArticleDetail.as_view(), name='articles-detail'),

    # article-reply
    url(r'^articleDetail/(?P<article_pk>[0-9]+)/articleReplies/$', views.ArticleReplyList.as_view(), name='article-reply'),
    url(r'^articleDetail/(?P<article_pk>[0-9]+)/articleReplies/(?P<reply_pk>[0-9]+)/$', views.ArticleReplyDetail.as_view(), name='article-reply-detail'),

    # donkeyuser
    url(r'^donkeyuser/$', views.UserDetail.as_view(), name='user-detail'),

    # check service alive
    url(r'^hello/$', views.hello, name='hello'),

    url(r'auth-check/$', views.custom_auth_check, name='auth-check')

]

urlpatterns = format_suffix_patterns(urlpatterns)
