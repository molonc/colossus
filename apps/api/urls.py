"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'sample', views.SampleViewSet)
router.register(r'sequencing', views.SequencingViewSet)
router.register(r'library', views.LibraryViewSet, base_name='library')
router.register(r'library_brief', views.LibraryBriefViewSet, base_name='library_brief')

app_name='api'
urlpatterns = [
    url(r'^', include(router.urls))
]