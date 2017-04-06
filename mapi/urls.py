from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from mapi import views

urlpatterns = [
    # pre-check : token check
    url(r'^pre-check/$', views.pre_check, name='pre-check'),

    # gen-auth-key : temporally generating key in cache
    # confirm-auth-key : authenticating email code in cache
    url(r'^gen-auth-key/$', views.gen_auth_key, name='gen-auth-key'),
    url(r'^confirm-auth-key/$', views.confirm_auth_key, name='confirm-auth-key'),

    # registration : user registration
    url(r'^registration/$', views.registration, name='registration'),

    # articles : listing articles
    # articles-add : adding an article
    url(r'^articles/$', views.ArticleList.as_view(), name='articles'),
    url(r'^article-detail/(?P<pk>[0-9]+)/$', views.ArticleDetail.as_view(), name='articles-detail'),

    # article-reply
    url(r'^article-detail/(?P<article_pk>[0-9]+)/article_replies/$', views.ArticleReplyList.as_view(), name='article-reply'),
    url(r'^article-detail/(?P<article_pk>[0-9]+)/article_replies/(?P<reply_pk>[0-9]+)/$', views.ArticleReplyDetail.as_view(), name='article-reply-detail'),

    # donkeyuser
    url(r'^donkeyuser/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),

    # check service alive
    url(r'^hello/$', views.hello, name='hello'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
