"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.shortcuts import render
from django.views.generic.base import TemplateView
from .models import Sample, Cell


class MainView(TemplateView):
    
    """
    Home page of the project.
    """
    
    template_name = "core/main.html"
    
    def get_context_data(self):
        s = Sample()
        fields = s.get_fields()
        context = {
                   'samples': Sample.objects.all(),
                   'fields': fields,
                   }
        return context
    
    
class HomeView(TemplateView):
    
    """
    Home page of this app.
    """
    
    template_name = 'core/home.html'
    
    
class SampleDetail(TemplateView):

    """
    Sample detail page.
    """
    
    template_name = 'core/sample_detail.html'
    
    def get_context_data(self):
        sid = self.request.GET.get('sid')
        sample = Sample.objects.get(pk=sid)
        c = Cell()
        fields = c.get_fields()
        context = {'sample': sample,
                   'celltable_fields': fields,
                   }
        return context
            
