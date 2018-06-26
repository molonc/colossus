"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'sample', views.SampleViewSet)
router.register(r'lane', views.LaneViewSet)
router.register(r'sequencing', views.SequencingViewSet)
router.register(r'library', views.LibraryViewSet, base_name='library')
router.register(r'sublibraries', views.SublibraryViewSet, base_name='sublibraries')
router.register(r'analysis_information', views.AnalysisInformationViewSet, base_name='analysis_information')
router.register(r'analysis_run', views.AnalysisRunViewSet, base_name='analysis_run')
router.register(r'experimental_metadata', views.ExperimentalMetadata, base_name='experimental_metadata')
app_name='api'
urlpatterns = [
    url(r'^', include(router.urls))
]
