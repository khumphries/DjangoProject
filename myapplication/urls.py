from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('myapplication.views',
    url(r'^list/$', 'list', name='list'),
    url(r'^sign_up/$',views.sign_up, name='sign_up'),
    url(r'^sign_up_complete/$',views.sign_up_complete, name='sign_up_complete'),
    url(r'^login/$', views.login_user, name='login'),
)