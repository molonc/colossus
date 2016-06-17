"""
Created on June 17, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.conf.urls import url
from . import views

app_name = 'account'
urlpatterns = [
               url(r'^login$', views.login_view, name='login'),
               url(r'^logout$', views.logout_view, name='logout'),
               ]