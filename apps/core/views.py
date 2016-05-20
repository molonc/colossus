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
        samples = Sample.objects.all()
#         self._update_sample_num_libraries(samples)
        context = {
                   'samples': samples,
                   'fields': fields,
                   }
        return context
    
    # fixme: there must be a better way to set the value of 
    # num_librarires field automatically when the sample celltable is updated.
    # Currently, it's not efficient, since every time the main page is loaded, it runs 
    # through all the samples.
#     def _update_sample_num_libraries(self, samples):
#         for sample in samples:
#             if sample.has_celltable():
#                 nl = len(sample.celltable.cell_set.all())
#                 if sample.num_libraries != nl:
#                     sample.num_libraries = nl
#                     sample.save()
                
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
#         sample.set_num_libraries()
        c = Cell()
        fields = c.get_fields()
        context = {'sample': sample,
                   'celltable_fields': fields,
                   }
        return context
            
