"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.shortcuts import render
from django.views.generic.base import TemplateView
from .models import Sample


class MainView(TemplateView):
    
    """
    Home page of the project.
    """
    
    template_name = "core/main.html"
    
    def get_context_data(self):
        return {'samples': Sample.objects.all()}
    
    
class HomeView(TemplateView):
    
    """
    Home page of this app.
    """
    
    template_name = 'core/home.html'
    
    
def sample_detail(request):
    sid = request.GET.get('sid')
    sample = Sample.objects.get(pk=sid)
    return render(request, 'core/sample_detail.html', context={'sample':sample})