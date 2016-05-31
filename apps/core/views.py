"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from .models import Sample
from .forms import SampleForm


def index_view(request):
    s = Sample()
    samples = Sample.objects.all()
    # self._update_sample_num_libraries(samples)
    context = {
               'samples': samples,
               }
    return render(request, 'core/index.html', context)


def home_view(request):
    """home page of this app."""
    return HttpResponse(render(request, 'core/home.html', {}))


def sample_detail(request, pk):
    """sample detail page."""
    sample = get_object_or_404(Sample, pk=pk)

    ## the post-save doesn't work in a sense that it's always
    ## one save behind. 
    ## this is to avoid that, but there must be a better way to handle this.
    # if sample.has_celltable():
    #     nl = len(sample.celltable.cell_set.all())
    #     if sample.num_libraries != nl:
    #         sample.num_libraries = nl
    #         sample.save()

    # c = Cell()
    # fields = c.get_fields()
    context = {
    'sample': sample
    }
    return render(request, 'core/sample_detail.html', context)
            

def sample_create(request):
    """sample create page."""
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    if request.method == 'POST':
        form = SampleForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            return HttpResponseRedirect(reverse("index"))
    
    else:
        form = SampleForm()
    return render(request, "core/sample_create.html", {'form':form})


def sample_update(request, pk):
    """sample update page."""
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == 'POST':
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.save()
            return HttpResponseRedirect(reverse("index"))

    else:
        form = SampleForm(instance=sample)

    context = {
        'form': form,
        'pk': pk,
    }
    return render(request, "core/sample_update.html", context)


def sample_delete(request, pk):
    """sample delete page."""
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    sample = get_object_or_404(Sample, pk=pk)

    if request.method == 'POST':
        sample.delete()
        return HttpResponseRedirect(reverse("index"))    

    context = {
        'sample': sample,
        'pk': pk
    }
    return render(request, "core/sample_delete.html", context)




