from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from board import views

urlpatterns = [
    # pre-check : token check
    url(r'^pre-check/$', views.pre_check, name='pre-check'),

    # gen-auth-key : temporally generating key in cache
    # confirm-auth-key : authenticating email code in cache
    url(r'^gen-auth-key/$', views.gen_auth_key, name='gen-auth-key'),
    url(r'^confirm-auth-key/$', views.confirm_auth_key, name='confirm-auth-key'),

    # registration : user registration
    url(r'^registration/$', views.registration),

    url('^hello/', views.hello)
]

urlpatterns = format_suffix_patterns(urlpatterns)
