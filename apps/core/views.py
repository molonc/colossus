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
from .models import Sample, Library, Sequencing
from .forms import SampleForm, AdditionalInfoInlineFormset
from .forms import LibraryForm, SublibraryInlineFormset, LibrarySampleDetailInlineFormset, LibraryConstructionInlineFormset, LibraryQSInlineFormset
from .forms import SequencingForm, SequencingDetailFormset

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
# Sample views
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
            formset = AdditionalInfoInlineFormset(instance=sample)

    else:
        form = SampleForm(instance=sample)
        formset = AdditionalInfoInlineFormset(instance=sample)

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
# Library views
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
            sublib_formset = SublibraryInlineFormset(
                request.POST,
                instance=instance
                )
            libdetail_formset = LibrarySampleDetailInlineFormset(
                request.POST,
                instance=instance
                )
            libcons_formset = LibraryConstructionInlineFormset(
                request.POST,
                instance=instance
                )
            libqs_formset = LibraryQSInlineFormset(
                request.POST,
                instance=instance
                )
            print 'created library successfully.'
            if sublib_formset.is_valid():
                sublib_formset.save()
            if libdetail_formset.is_valid():
                libdetail_formset.save()
            if libcons_formset.is_valid():
                libcons_formset.save()
            if libqs_formset.is_valid():
                libqs_formset.save()
            return HttpResponseRedirect(reverse("core:library_list"))
        else:
            sublib_formset = SublibraryInlineFormset()
            libdetail_formset = LibrarySampleDetailInlineFormset()
            libcons_formset = LibraryConstructionInlineFormset()
            libqs_formset = LibraryQSInlineFormset()
    
    else:
        form = LibraryForm()
        sublib_formset = SublibraryInlineFormset()
        libdetail_formset = LibrarySampleDetailInlineFormset()
        libcons_formset = LibraryConstructionInlineFormset()
        libqs_formset = LibraryQSInlineFormset()

    context = {
        'form': form,
        'sublib_formset': sublib_formset,
        'libdetail_formset': libdetail_formset,
        'libcons_formset': libcons_formset,
        'libqs_formset': libqs_formset
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
            sublib_formset = SublibraryInlineFormset(
                request.POST,
                instance=instance
                )
            libdetail_formset = LibrarySampleDetailInlineFormset(
                request.POST,
                instance=instance
                )
            libcons_formset = LibraryConstructionInlineFormset(
                request.POST,
                instance=instance
                )
            libqs_formset = LibraryQSInlineFormset(
                request.POST,
                instance=instance
                )
            ## should use django messages
            print 'updated library successfully.'
            if sublib_formset.is_valid():
                sublib_formset.save()
            if libdetail_formset.is_valid():
                libdetail_formset.save()
            if libcons_formset.is_valid():
                libcons_formset.save()
            if libqs_formset.is_valid():
                libqs_formset.save()
            return HttpResponseRedirect(reverse("core:library_list"))

        else:
            sublib_formset = SublibraryInlineFormset(
                instance=library
                )
            libdetail_formset = LibrarySampleDetailInlineFormset(
                instance=library
                )
            libcons_formset = LibraryConstructionInlineFormset(
                instance=library
                )
            libqs_formset = LibraryQSInlineFormset(
                instance=library
                )
    
    else:
        form = LibraryForm(instance=library)
        sublib_formset = SublibraryInlineFormset(instance=library)
        libdetail_formset = LibrarySampleDetailInlineFormset(instance=library)
        libcons_formset = LibraryConstructionInlineFormset(instance=library)
        libqs_formset = LibraryQSInlineFormset(instance=library)

    context = {
        'pk': pk,
        'form': form,
        'sublib_formset': sublib_formset,
        'libdetail_formset': libdetail_formset,
        'libcons_formset': libcons_formset,
        'libqs_formset': libqs_formset
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
# Sequencing views
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
            seqdetail_formset = SequencingDetailFormset(
                request.POST,
                instance=instance
                )
            ## should use django messages
            print 'created sequencing successfully.'
            if seqdetail_formset.is_valid():
                instances = seqdetail_formset.save(commit=False)
                for instance in instances:
                    instance.save()
                    ## should use django messages
                    print 'added sample details successfully.'                    
            return HttpResponseRedirect(reverse("core:sequencing_list"))
        else:
            seqdetail_formset = SequencingDetailFormset()
    
    else:
        form = SequencingForm()
        seqdetail_formset = SequencingDetailFormset()

    context = {
        'form': form,
        'seqdetail_formset': seqdetail_formset,
        }
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
            seqdetail_formset = SequencingDetailFormset(
                request.POST,
                instance=instance
                )                        
            print 'updated sequencing successfully.'
            if seqdetail_formset.is_valid():
                instances = seqdetail_formset.save(commit=False)
                for instance in instances:
                    instance.save()
            return HttpResponseRedirect(reverse("core:sequencing_list"))
        else:
            seqdetail_formset = SequencingDetailFormset(instance=sequencing)
    
    else:
        form = SequencingForm(instance=sequencing)
        seqdetail_formset = SequencingDetailFormset(instance=sequencing)

    context = {
        'pk': pk,
        'form': form,
        'seqdetail_formset': seqdetail_formset,
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
