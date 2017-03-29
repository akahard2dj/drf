from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from board import views

urlpatterns = [
    # precheck - token check
    url(r'pre-check/$', views.pre_check, name='pre-check'),


    # gen-auth-key - temporally generating key
    url(r'gen-auth-key/$', views.gen_auth_key, name='gen-auth-key'),
    url(r'confirm-auth-key/$', views.confirm_auth_key, name='confirm-auth-key'),

    
    url(r'^posts/$', views.PostList.as_view()),
    url(r'^posts/(?P<pk>[0-9]+)/$', views.PostDetail.as_view()),
    url(r'^posts/add/$', views.PostAdd.as_view()),
    url(r'users/$', views.UserDetail.as_view()),
    #url(r'users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'registration/$', views.registration),
    #url(r'registration/confirmation/$', views.registration_confirmation),

    url(r'perm_test/$', views.example_view),
]

urlpatterns = format_suffix_patterns(urlpatterns)
