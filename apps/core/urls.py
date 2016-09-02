"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.conf.urls import url
from . import views

app_name = 'core'
urlpatterns = [
url(r'^$', views.home_view, name='home'),
url(r'^sample/(?P<pk>\d+)$', views.sample_detail, name='sample_detail'),
url(r'^sample/list$', views.sample_list, name='sample_list'),
url(r'^sample/create/$', views.sample_create, name='sample_create'),
url(r'^sample/update/(?P<pk>\d+)$', views.sample_update, name='sample_update'),
url(r'^sample/delete/(?P<pk>\d+)$', views.sample_delete, name='sample_delete'),
url(r'^library/(?P<pk>\d+)$', views.library_detail, name='library_detail'),
url(r'^library/list$', views.library_list, name='library_list'),
url(r'^library/create/$', views.LibraryCreate.as_view(), name='library_create'),
url(r'^library/create/(?P<from_sample>\d+)$', views.LibraryCreate.as_view(), name='library_create_from_sample'),
url(r'^library/update/(?P<pk>\d+)$', views.LibraryUpdate.as_view(), name='library_update'),
url(r'^library/delete/(?P<pk>\d+)$', views.library_delete, name='library_delete'),
url(r'^sequensing/(?P<pk>\d+)$', views.sequencing_detail, name='sequencing_detail'),
url(r'^sequensing/list$', views.sequencing_list, name='sequencing_list'),
url(r'^sequensing/create/$', views.sequencing_create, name='sequencing_create'),
url(r'^sequensing/create/(?P<from_library>\d+)$', views.sequencing_create_from_library, name='sequencing_create_from_library'),
url(r'^sequensing/update/(?P<pk>\d+)$', views.sequencing_update, name='sequencing_update'),
url(r'^sequensing/delete/(?P<pk>\d+)$', views.sequencing_delete, name='sequencing_delete'),
url(r'^sequensing/get_samplesheet/(?P<pk>\d+)$', views.sequencing_get_samplesheet, name='sequencing_get_samplesheet'),
url(r'^project/list$', views.project_list, name='project_list'),
url(r'^project/update/(?P<pk>\d+)$', views.project_update, name='project_update'),
url(r'^project/delete/(?P<pk>\d+)$', views.project_delete, name='project_delete'),
]

