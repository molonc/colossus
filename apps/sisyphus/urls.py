"""
Created on July 7, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from django.conf.urls import url
from . import views

app_name='sisyphus'
urlpatterns = [
    url(r'^$', views.home_view, name='home'),
    url(r'^information/$', views.analysisinformation_list, name='analysisinformation_list'),
    url(r'^information/(?P<pk>\d+)$', views.AnalysisInformationDetailView.as_view(), name='analysisinformation_detail'),
    url(r'^information/create/$', views.analysisinformation_create_choose_library, name='analysisinformation_create_choose_library'),
    url(r'^information/create/(?P<from_library>\d+)$', views.AnalysisInformationCreate.as_view(), name='analysisinformation_create_from_library'),
    url(r'^information/update/(?P<library_pk>\d+)/(?P<analysis_pk>\d+)$', views.AnalysisInformationUpdate.as_view(), name='analysisinformation_update'),
    url(r'^information/delete/(?P<pk>\d+)$', views.analysis_delete, name='analysis_delete'),

]