"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated Nov. 8, 2017 by Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from . import views

app_name = 'core'
urlpatterns = [
    url(r'^sample/(?P<pk>\d+)$', views.sample_detail, name='sample_detail'),
    url(r'^sample/list$', views.sample_list, name='sample_list'),
    url(r'^sample/create/$', views.SampleCreate.as_view(), name='sample_create'),
    url(r'^sample/update/(?P<pk>\d+)$', views.SampleUpdate.as_view(), name='sample_update'),
    url(r'^sample/delete/(?P<pk>\d+)$', views.sample_delete, name='sample_delete'),
    url(r'^project/list$', views.project_list, name='project_list'),
    url(r'^project/update/(?P<pk>\d+)$', views.project_update, name='project_update'),
    url(r'^project/delete/(?P<pk>\d+)$', views.project_delete, name='project_delete')
]

