"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.shortcuts import render
from django.views.generic.base import TemplateView

class MainView(TemplateView):
    
    """
    Home page of the project.
    """
    
    template_name = "core/main.html"
    
class HomeView(TemplateView):
    
    """
    Home page of this app.
    """
    
    template_name = 'core/home.html'
     
