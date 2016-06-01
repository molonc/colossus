"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from .decorators import Render
from .models import Sample
from .forms import SampleForm, AdditionalSampleInformationForm


@Render("core/index.html")
def index_view(request):
    context = {}
    return context


@Render("core/home.html")
def home_view(request):
    """home page of the app."""
    context = {}
    return context


@Render("core/sample_list.html")
def sample_list(request):
    """list of samples."""
    s = Sample()
    samples = Sample.objects.all()
    # self._update_sample_num_libraries(samples)
    context = {'samples': samples}
    return context


@Render("core/sample_detail.html")
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

    context = {
    'sample': sample
    }
    return context
            

@Render("core/sample_create.html")
@permission_required("core.groups.shahuser")
def sample_create(request):
    """sample create page."""
    if request.method == 'POST':
        form_sample = SampleForm(request.POST)
        form_sample_info = AdditionalSampleInformationForm(request.POST)
        if form_sample.is_valid():
            instance = form_sample.save(commit=False)
            instance.save()
            sample_id = instance.pk
            ## should use django messages
            print 'form_sample saved successfully.'
    
            if form_sample_info.is_valid():
                instance = form_sample_info.save(commit=False)
                instance.sample_id = sample_id
                instance.save()
                ## should use django messages
                print 'form_sample_info saved successfully.'

        return HttpResponseRedirect(reverse("core:sample_list"))
    
    else:
        form_sample = SampleForm()
        form_sample_info = AdditionalSampleInformationForm()

    context = {
        'form_sample': form_sample,
        'form_additional_sample_information': form_sample_info
        }
    return context


@Render("core/sample_update.html")
@permission_required("core.groups.shahuser")
def sample_update(request, pk):
    """sample update page."""
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == 'POST':
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.save()
            return HttpResponseRedirect(reverse("core:sample_list"))

    else:
        form = SampleForm(instance=sample)

    context = {
        'form': form,
        'pk': pk,
    }
    return context


@Render("core/sample_delete.html")
@permission_required("core.groups.shahuser")
def sample_delete(request, pk):
    """sample delete page."""
    sample = get_object_or_404(Sample, pk=pk)

    if request.method == 'POST':
        sample.delete()
        return HttpResponseRedirect(reverse("core:sample_list"))    

    context = {
        'sample': sample,
        'pk': pk
    }
    return context




