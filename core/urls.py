"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from . import views

app_name = 'core'
urlpatterns = [
    url(r'^sample/list$', views.SampleList.as_view(), name='sample_list'),
    url(r'^sample/create/$', views.SampleCreate.as_view(), name='sample_create'),
    url(r'^sample/update/(?P<pk>\d+)$', views.SampleUpdate.as_view(), name='sample_update'),
    url(r'^sample/delete/(?P<pk>\d+)$', views.SampleDelete.as_view(), name='sample_delete'),
    url(r'^sample/(?P<pk>\d+)$', views.sample_name_to_id_redirect, name='sample_detail'),
    url(r'^sample/(?P<sample_id>([A-Z]+)\w+)$', views.sample_name_to_id_redirect),
    url(r'^project/list$', views.ProjectList.as_view(), name='project_list'),
    url(r'^project/create$', views.ProjectCreate.as_view(), name='project_create'),
    url(r'^project/update/(?P<pk>\d+)$', views.ProjectUpdate.as_view(), name='project_update'),
    url(r'^project/delete/(?P<pk>\d+)$', views.ProjectDelete.as_view(), name='project_delete'),
    url(r'^project/detail/(?P<pk>\d+)$', views.ProjectDetail.as_view(), name='project_detail'),
    url(r'^gsc$', views.gsc_submission_form, name='gsc_submission_form'),
    url(r'^gsc_data$', views.gsc_info_post, name='gsc_retreive_data'),
    url(r'^download_sublibrary$', views.download_sublibrary_info, name='download_sublibrary_info'),

]