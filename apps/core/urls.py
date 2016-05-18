"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.conf.urls import url
from .views import HomeView, sample_detail

app_name = 'core'
urlpatterns = [
               url(r'^$', HomeView.as_view(), name='home_view'),
               url(r'^/sample', sample_detail, name='sample_detail')
               ]
