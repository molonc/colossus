"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.shortcuts import render
from django.views.generic.base import TemplateView
from .models import Sample, CellTable, Cell


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
    
    
class SampleDetail(TemplateView):

    """
    Sample detail page.
    """
    
    template_name = 'core/sample_detail.html'
    
    def get_context_data(self):
        sample = self.get_sample()
        fields = self.get_cell_field_names()
        values = [values for values in self.get_cell_values()]
        context = {'sample': sample,
                   'cell_fields': fields,
                   'cell_values': values,
                   }
        return context
    
    def get_sample(self):
        sid = self.request.GET.get('sid')
        sample = Sample.objects.get(pk=sid)
        return sample 
    
    def get_cell_field_names(self):
        """return the fields of the Cell model."""
        c = Cell()
        names = [field.name for field in c._meta.fields]
        names.remove('id')
        names.remove('cell_table')
        return names
    
    def get_cell_values(self):
        """return the value of the given field for a Cell object."""
        sample = self.get_sample()
        cells = sample.celltable.cell_set.all()
        fields = self.get_cell_field_names()
        for c in cells:
            values = [str(c.row) + str(c.col)]
            values.extend([getattr(c, f) for f in fields])
            yield values
    
def sample_detail(request):
    sid = request.GET.get('sid')
    sample = Sample.objects.get(pk=sid)
    return render(request, 'core/sample_detail.html', context={'sample':sample})
