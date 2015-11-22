from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('myapplication.views',
    url(r'^list/$', 'list', name='list'),
    url(r'^create_report/$', 'create_report', name='create_report'),
    url(r'^sign_up/$',views.sign_up, name='sign_up'),
    url(r'^sign_up_complete/$',views.sign_up_complete, name='sign_up_complete'),
    url(r'^login/$', views.login_user, name='login'),
    url(r'^home/$', views.home_page, name='home'),
    url(r'^logout/$', views.logout_user, name='logout'),
    url(r'^messages/$', views.messages, name='messages'),
    url(r'^inbox/$', views.inbox, name='inbox'),
    url(r'^outbox/$', views.outbox, name='outbox'),
    url(r'^groups_creator/$', views.groups_creator, name='groups_creator'),
    url(r'^groups/$', views.groups_list, name='groups'),
)