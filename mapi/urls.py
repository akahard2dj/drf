from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from mapi import views

urlpatterns = [
    # pre-check : token check
    url(r'^preCheck$', views.pre_check, name='pre-check'),

    # email-check : email validation and getting a name of a university
    url(r'^emailCheck$', views.email_check, name='email-check'),

    # gen-auth-key : temporally generating key in cache
    # confirm-auth-key : authenticating email code in cache
    url(r'^genAuthKey$', views.gen_auth_key, name='gen-auth-key'),
    url(r'^confirmAuthKey$', views.confirm_auth_key, name='confirm-auth-key'),

    # registration : user registration
    url(r'^registration$', views.registration, name='registration'),

    # articles : listing articles
    # articles-add : adding an article
    url(r'^articles/$', views.ArticleList.as_view(), name='articles'),
    url(r'^articleDetail/(?P<pk>[0-9]+)/$', views.ArticleDetail.as_view(), name='articles-detail'),

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
