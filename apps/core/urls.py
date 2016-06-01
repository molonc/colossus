"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.conf.urls import url
from . import views

app_name = 'core'
urlpatterns = [
               url(r'^$', views.home_view, name='home'),
               url(r'^sample/list$', views.sample_list, name='sample_list'),
               url(r'^sample/create/$', views.sample_create, name='sample_create'),
               url(r'^sample/(?P<pk>\d+)$', views.sample_detail, name='sample_detail'),
               url(r'^sample/update/(?P<pk>\d+)$', views.sample_update, name='sample_update'),
               url(r'^sample/delete/(?P<pk>\d+)$', views.sample_delete, name='sample_delete'),
               # url(r'^sample/detail/(?P<id>\d+)$', views.sample_detail, name='sample_detail2'),
               ]
