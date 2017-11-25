"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated Nov. 30, 2017 by Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from . import views

app_name = 'core'
urlpatterns = [
    url(r'^sample/(?P<pk>\d+)$', views.SampleDetail.as_view(), name='sample_detail'),
    url(r'^sample/list$', views.SampleList.as_view(), name='sample_list'),
    url(r'^sample/create/$', views.SampleCreate.as_view(), name='sample_create'),
    url(r'^sample/update/(?P<pk>\d+)$', views.SampleUpdate.as_view(), name='sample_update'),
    url(r'^sample/delete/(?P<pk>\d+)$', views.SampleDelete.as_view(), name='sample_delete'),
    url(r'^project/list$', views.ProjectList.as_view(), name='project_list'),
    url(r'^project/update/(?P<pk>\d+)$', views.ProjectUpdate.as_view(), name='project_update'),
    url(r'^project/delete/(?P<pk>\d+)$', views.ProjectDelete.as_view(), name='project_delete')
]
