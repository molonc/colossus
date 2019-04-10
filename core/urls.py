"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from . import views

app_name = 'core'
urlpatterns = [
    url(r'^inventory$', views.Inventory.as_view(), name='inventory'),
    url(r'^sample/(?P<pk>\d+)$', views.SampleDetail.as_view(), name='sample_detail'),
    url(r'^sample/list$', views.SampleList.as_view(), name='sample_list'),
    url(r'^sample/create/$', views.SampleCreate.as_view(), name='sample_create'),
    url(r'^sample/update/(?P<pk>\d+)$', views.SampleUpdate.as_view(), name='sample_update'),
    url(r'^sample/delete/(?P<pk>\d+)$', views.SampleDelete.as_view(), name='sample_delete'),
    url(r'^project/list$', views.ProjectList.as_view(), name='project_list'),
    url(r'^project/create$', views.ProjectCreate.as_view(), name='project_create'),
    url(r'^project/update/(?P<pk>\d+)$', views.ProjectUpdate.as_view(), name='project_update'),
    url(r'^project/delete/(?P<pk>\d+)$', views.ProjectDelete.as_view(), name='project_delete'),
    url(r'^project/detail/(?P<pk>\d+)$', views.ProjectDetail.as_view(), name='project_detail'),
    url(r'^analysis/list$', views.analys_list, name='analysis_list'),
    url(r'^analysis/detail/(?P<pk>\d+)$', views.analysis_detail, name='analysis_detail'),

]
