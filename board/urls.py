from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from board import views

urlpatterns = [
    url(r'^posts/$', views.PostList.as_view()),
    url(r'^posts/(?P<pk>[0-9]+)/$', views.PostDetail.as_view()),

    url(r'users/$', views.UserDetail.as_view()),
    #url(r'users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    url(r'registration/$', views.registration),
    url(r'registration/confirmation/$', views.registration_confirmation),

    url(r'perm_test/$', views.example_view),
]

urlpatterns = format_suffix_patterns(urlpatterns)
