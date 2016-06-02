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
from .models import Sample, AdditionalSampleInformation
from .models import Library, SublibraryInformation
from .models import Sequencing
from .forms import SampleForm, AdditionalInfoInlineFormset
from .forms import LibraryForm, SequencingForm

#============================
# Index page
#----------------------------
@Render("core/index.html")
def index_view(request):
    context = {}
    return context


#============================
# Home page of the app
#----------------------------
@Render("core/home.html")
def home_view(request):
    """home page of the app."""
    context = {}
    return context


#============================
# Sample handling
#----------------------------
@Render("core/sample_list.html")
def sample_list(request):
    """list of samples."""
    samples = Sample.objects.all()
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
        form = SampleForm(request.POST)
        if form.is_valid():
            print '>' * 100
            instance = form.save(commit=False)
            instance.save()
            formset = AdditionalInfoInlineFormset(
                request.POST,
                instance=instance
                )
            ## should use django messages
            print 'created sample successfully.'            
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.save()
                    ## should use django messages
                    print 'added additional sample information successfully.'
                return HttpResponseRedirect(reverse("core:sample_list"))
        else:
            formset = AdditionalInfoInlineFormset()
    
    else:
        form = SampleForm()
        formset = AdditionalInfoInlineFormset()
    
    context = {
        'form': form,
        'formset': formset
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
            instance = form.save(commit=False)
            instance.save()
            formset = AdditionalInfoInlineFormset(
                request.POST,
                instance=instance
                )
            ## should use django messages
            print 'created sample successfully.'            
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.save()
                    ## should use django messages
                    print 'added additional sample information successfully.'            
            return HttpResponseRedirect(reverse("core:sample_list"))

    else:
        form = SampleForm(instance=sample)
        formset = AdditionalInfoInlineFormset(
            instance=sample)

    context = {
        'form': form,
        'formset': formset,
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


#============================
# Library handling
#----------------------------
@Render("core/library_list.html")
def library_list(request):
    """list of libraries."""
    libraries = Library.objects.all()
    context = {'libraries': libraries}
    return context

@Render("core/library_detail.html")
def library_detail(request, pk):
    """library detail page."""
    library = get_object_or_404(Library, pk=pk)
    context = {
    'library': library
    }
    return context
            
@Render("core/library_create.html")
@permission_required("core.groups.shahuser")
def library_create(request):
    """library create page."""
    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            ## should use django messages
            print 'created library successfully.'
            return HttpResponseRedirect(reverse("core:library_list"))
    
    else:
        form = LibraryForm()

    context = {
        'form': form,
        }
    return context

@Render("core/library_update.html")
@permission_required("core.groups.shahuser")
def library_update(request, pk):
    """library update page."""
    library = get_object_or_404(Library, pk=pk)
    if request.method == 'POST':
        form = LibraryForm(request.POST, instance=library)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            ## should use django messages
            print 'updated library successfully.'
            return HttpResponseRedirect(reverse("core:library_list"))

    else:
        form = LibraryForm(instance=library)

    context = {
        'form': form,
        'pk': pk,
    }
    return context

@Render("core/library_delete.html")
@permission_required("core.groups.shahuser")
def library_delete(request, pk):
    """library delete page."""
    library = get_object_or_404(Library, pk=pk)

    if request.method == 'POST':
        library.delete()
        return HttpResponseRedirect(reverse("core:library_list"))    

    context = {
        'library': library,
        'pk': pk
    }
    return context


#============================
# Sequencing handling
#----------------------------
@Render("core/sequencing_list.html")
def sequencing_list(request):
    """list of sequencings."""
    sequencings = Sequencing.objects.all()
    context = {'sequencings': sequencings}
    return context

@Render("core/sequencing_detail.html")
def sequencing_detail(request, pk):
    """sequencing detail page."""
    sequencing = get_object_or_404(Sequencing, pk=pk)
    context = {'sequencing': sequencing}
    return context
            
@Render("core/sequencing_create.html")
@permission_required("core.groups.shahuser")
def sequencing_create(request):
    """sequencing create page."""
    if request.method == 'POST':
        form = SequencingForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            ## should use django messages
            print 'created sequencing successfully.'
            return HttpResponseRedirect(reverse("core:sequencing_list"))
    
    else:
        form = SequencingForm()

    context = {'form': form}
    return context

@Render("core/sequencing_update.html")
@permission_required("core.groups.shahuser")
def sequencing_update(request, pk):
    """sequencing update page."""
    sequencing = get_object_or_404(Sequencing, pk=pk)
    if request.method == 'POST':
        form = SequencingForm(request.POST, instance=sequencing)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            ## should use django messages
            print 'updated sequencing successfully.'
            return HttpResponseRedirect(reverse("core:sequencing_list"))

    else:
        form = SequencingForm(instance=sequencing)

    context = {
        'form': form,
        'pk': pk,
    }
    return context

@Render("core/sequencing_delete.html")
@permission_required("core.groups.shahuser")
def sequencing_delete(request, pk):
    """sequencing delete page."""
    sequencing = get_object_or_404(Sequencing, pk=pk)

    if request.method == 'POST':
        sequencing.delete()
        return HttpResponseRedirect(reverse("core:sequencing_list"))    

    context = {
        'sequencing': sequencing,
        'pk': pk
    }
    return context
