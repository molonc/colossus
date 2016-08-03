"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

#============================
# Django imports
#----------------------------
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required #, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

#============================
# App imports
#----------------------------
from .decorators import Render
from .models import (
    Sample,
    Library,
    Sequencing,
    SublibraryInformation
    )
from .forms import (
    SampleForm, 
    AdditionalSampleInfoInlineFormset,
    LibraryForm,
    LibrarySampleDetailInlineFormset,
    LibraryConstructionInfoInlineFormset,
    LibraryQuantificationAndStorageInlineFormset,
    SublibraryForm,
    SequencingForm,
    SequencingDetailInlineFormset,
    ProjectForm
    )
from .utils import bulk_create_sublibrary

#============================
# 3rd-party app imports
#----------------------------
from taggit.models import Tag


#============================
# Helpers
#----------------------------
def get_libraries(self):
    return Library.objects.filter(projects__name=self.name)
## add a method to get the list of libraries for each project name
Tag.get_libraries = get_libraries


#============================
# Index page
#----------------------------
@Render("core/index.html")
def index_view(request):
    context = {
    'sample_size': len(Sample.objects.all()),
    'library_size': len(Library.objects.all()),
    'sequencing_size': len(Sequencing.objects.all())
    }
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
    samples = Sample.objects.all().order_by('sample_id')
    context = {'samples': samples}
    return context

@Render("core/sample_detail.html")
def sample_detail(request, pk):
    """sample detail page."""
    sample = get_object_or_404(Sample, pk=pk)
    context = {
    'sample': sample
    }
    return context
            

@Render("core/sample_create.html")
@login_required()
def sample_create(request):
    """sample create page."""
    if request.method == 'POST':
        form = SampleForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            additional_info_formset = AdditionalSampleInfoInlineFormset(
                request.POST,
                instance=instance
                )
            if additional_info_formset.is_valid():
                additional_info_formset.save()

            msg = "Successfully created the Sample."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to create the sample. Please fix the errors below."
            messages.error(request, msg)
            formset = AdditionalSampleInfoInlineFormset()
    
    else:
        form = SampleForm()
        formset = AdditionalSampleInfoInlineFormset()
    
    context = {
        'form': form,
        'formset': formset
        }
    return context


@Render("core/sample_update.html")
@login_required()
def sample_update(request, pk):
    """sample update page."""
    sample = get_object_or_404(Sample, pk=pk)
    if request.method == 'POST':
        form = SampleForm(request.POST, instance=sample)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            additional_info_formset = AdditionalSampleInfoInlineFormset(
                request.POST,
                instance=instance
                )
            if additional_info_formset.is_valid():
                additional_info_formset.save()

            msg = "Successfully updated the Sample."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to update the sample. Please fix the errors below."
            messages.error(request, msg)
            formset = AdditionalSampleInfoInlineFormset(instance=sample)

    else:
        form = SampleForm(instance=sample)
        formset = AdditionalSampleInfoInlineFormset(instance=sample)

    context = {
        'form': form,
        'formset': formset,
        'pk': pk,
    }
    return context

@Render("core/sample_delete.html")
@login_required()
def sample_delete(request, pk):
    """sample delete page."""
    sample = get_object_or_404(Sample, pk=pk)

    if request.method == 'POST':
        sample.delete()
        msg = "Successfully deleted the Sample."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('core:sample_list'))

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
    libraries = Library.objects.all().order_by('pool_id')
    context = {'libraries': libraries}
    return context

@Render("core/library_detail.html")
def library_detail(request, pk):
    """library detail page."""
    library = get_object_or_404(Library, pk=pk)
    sublibinfo = SublibraryInformation()
    context = {
    'library': library,
    'sublibinfo_fields': sublibinfo.get_fields()
    }
    return context
            
# class LibrarCreate(TemplateView):

#     """
#     Library create page.
#     """

#     template_name = "core/library_create.html"

#     def _save_formset(self, formset):
#         pass

#     def _uploaded_file_handler(self):
#         pass

#     def get_context_data(self):
#         pass

@Render("core/library_create.html")
@login_required()
def library_create(request):
    """library create page."""
    if request.method == 'POST':
        ## this is becaues of this django feature:
        ## https://code.djangoproject.com/ticket/1130
        request.POST['projects'] = ','.join(request.POST.getlist('projects'))

        form = LibraryForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            ## save instace with its ManyToMany relation.
            instance.save()
            form.save_m2m()

            sublib_form = SublibraryForm(
                request.POST,
                request.FILES,
                )
            libdetail_formset = LibrarySampleDetailInlineFormset(
                request.POST,
                instance=instance
                )
            libcons_formset = LibraryConstructionInfoInlineFormset(
                request.POST,
                instance=instance
                )
            libqs_formset = LibraryQuantificationAndStorageInlineFormset(
                request.POST,
                instance=instance
                )
            if sublib_form.is_valid():
                num_sublibraries = bulk_create_sublibrary(
                    instance,
                    request.FILES['smartchipapp_file']
                    )
                instance.num_sublibraries = num_sublibraries
                instance.save()
            if libdetail_formset.is_valid():
                libdetail_formset.save()
            if libcons_formset.is_valid():
                libcons_formset.save()
            if libqs_formset.is_valid():
                libqs_formset.save()

            msg = "Successfully created the Library."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to create the library. Please fix the errors below."
            messages.error(request, msg)
            sublib_form = SublibraryForm()
            libdetail_formset = LibrarySampleDetailInlineFormset()
            libcons_formset = LibraryConstructionInfoInlineFormset()
            libqs_formset = LibraryQuantificationAndStorageInlineFormset()
    
    else:
        form = LibraryForm()
        sublib_form = SublibraryForm()        
        libdetail_formset = LibrarySampleDetailInlineFormset()
        libcons_formset = LibraryConstructionInfoInlineFormset()
        libqs_formset = LibraryQuantificationAndStorageInlineFormset()

    projects = [t.name for t in Tag.objects.all()]
    context = {
        'form': form,
        'sublib_form': sublib_form,
        'libdetail_formset': libdetail_formset,
        'libcons_formset': libcons_formset,
        'libqs_formset': libqs_formset,
        'projects': projects,
        }
    return context

@Render("core/library_create_from_sample.html")
@login_required()
def library_create_from_sample(request, from_sample):
    """library create page."""
    sample = get_object_or_404(Sample, pk=from_sample)
    if request.method == 'POST':
        ## this is becaues of this django feature:
        ## https://code.djangoproject.com/ticket/1130
        request.POST['projects'] = ','.join(request.POST.getlist('projects'))

        form = LibraryForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            ## save instace with its ManyToMany relation.
            instance.save()
            form.save_m2m()

            sublib_form = SublibraryForm(
                request.POST,
                request.FILES,
                )
            libdetail_formset = LibrarySampleDetailInlineFormset(
                request.POST,
                instance=instance
                )
            libcons_formset = LibraryConstructionInfoInlineFormset(
                request.POST,
                instance=instance
                )
            libqs_formset = LibraryQuantificationAndStorageInlineFormset(
                request.POST,
                instance=instance
                )
            if sublib_form.is_valid():
                num_sublibraries = bulk_create_sublibrary(
                    instance,
                    request.FILES['smartchipapp_file']
                    )
                instance.num_sublibraries = num_sublibraries
                instance.save()
            if libdetail_formset.is_valid():
                libdetail_formset.save()
            if libcons_formset.is_valid():
                libcons_formset.save()
            if libqs_formset.is_valid():
                libqs_formset.save()

            msg = "Successfully created the Library."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to create the library. Please fix the errors below."
            messages.error(request, msg)
            sublib_form = SublibraryForm()
            libdetail_formset = LibrarySampleDetailInlineFormset()
            libcons_formset = LibraryConstructionInfoInlineFormset()
            libqs_formset = LibraryQuantificationAndStorageInlineFormset()
    
    else:
        form = LibraryForm()
        sublib_form = SublibraryForm()        
        libdetail_formset = LibrarySampleDetailInlineFormset()
        libcons_formset = LibraryConstructionInfoInlineFormset()
        libqs_formset = LibraryQuantificationAndStorageInlineFormset()

    projects = [t.name for t in Tag.objects.all()]
    context = {
        'form': form,
        'sublib_form': sublib_form,
        'libdetail_formset': libdetail_formset,
        'libcons_formset': libcons_formset,
        'libqs_formset': libqs_formset,
        'projects': projects,
        'sample': str(sample),
        'sample_id': from_sample,
        }
    return context

@Render("core/library_update.html")
@login_required()
def library_update(request, pk):
    """library update page."""
    library = get_object_or_404(Library, pk=pk)
    if request.method == 'POST':
        ## this is becaues of this django feature:
        ## https://code.djangoproject.com/ticket/1130
        request.POST['projects'] = ','.join(request.POST.getlist('projects'))

        form = LibraryForm(request.POST, instance=library)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            
            # save project tags
            form.save_m2m()

            sublib_form = SublibraryForm(
                request.POST,
                request.FILES,
                )
            libdetail_formset = LibrarySampleDetailInlineFormset(
                request.POST,
                instance=instance
                )
            libcons_formset = LibraryConstructionInfoInlineFormset(
                request.POST,
                instance=instance
                )
            libqs_formset = LibraryQuantificationAndStorageInlineFormset(
                request.POST,
                instance=instance
                )
            if sublib_form.is_valid():
                num_sublibraries = bulk_create_sublibrary(
                    instance,
                    request.FILES['smartchipapp_file']
                    )
                instance.num_sublibraries = num_sublibraries
                instance.save()
            if libdetail_formset.is_valid():
                libdetail_formset.save()
            if libcons_formset.is_valid():
                libcons_formset.save()
            if libqs_formset.is_valid():
                libqs_formset.save()

            msg = "Successfully updated the Library."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())

        else:
            msg = "Failed to update the library. Please fix the errors below."
            messages.error(request, msg)
            sublib_form = SublibraryForm()
            libdetail_formset = LibrarySampleDetailInlineFormset(
                instance=library
                )
            libcons_formset = LibraryConstructionInfoInlineFormset(
                instance=library
                )
            libqs_formset = LibraryQuantificationAndStorageInlineFormset(
                instance=library
                )
    
    else:
        form = LibraryForm(instance=library)
        sublib_form = SublibraryForm()
        libdetail_formset = LibrarySampleDetailInlineFormset(
            instance=library
            )
        libcons_formset = LibraryConstructionInfoInlineFormset(
            instance=library
            )
        libqs_formset = LibraryQuantificationAndStorageInlineFormset(
            instance=library
            )

    selected_projects = library.projects.names()
    projects = [t.name for t in Tag.objects.all()]
    context = {
        'pk': pk,
        'form': form,
        'sublib_form': sublib_form,
        'libdetail_formset': libdetail_formset,
        'libcons_formset': libcons_formset,
        'libqs_formset': libqs_formset,
        'projects': projects,
        'selected_projects': selected_projects,
        }
    return context

@Render("core/library_delete.html")
@login_required()
def library_delete(request, pk):
    """library delete page."""
    library = get_object_or_404(Library, pk=pk)

    if request.method == 'POST':
        library.delete()
        msg = "Successfully deleted the Library."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('core:library_list'))

    context = {
        'library': library,
        'pk': pk
    }
    return context


#============================
# Project views
#----------------------------
@Render("core/project_list.html")
def project_list(request):
    """projects detail page."""
    projects = Tag.objects.all().order_by('name')
    context = {'projects': projects}
    return context

@Render("core/project_delete.html")
@login_required()
def project_delete(request, pk):
    """project delete page."""
    project = get_object_or_404(Tag, pk=pk)

    if request.method == 'POST':
        project.delete()
        msg = "Successfully deleted the Project."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('core:project_list'))

    context = {
        'project': project,
        'pk': pk
    }
    return context

@Render("core/project_update.html")
@login_required()
def project_update(request, pk):
    project = get_object_or_404(Tag, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            msg = "Successfully updated the Project."
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('core:project_list'))
    
    else:
        form = ProjectForm(instance=project)

    context = {
        'pk': pk,
        'form': form
        }
    return context


#============================
# Sequencing views
#----------------------------
@Render("core/sequencing_list.html")
def sequencing_list(request):
    """list of sequencings."""
    sequencings = Sequencing.objects.all().order_by('library')
    context = {'sequencings': sequencings}
    return context

@Render("core/sequencing_detail.html")
def sequencing_detail(request, pk):
    """sequencing detail page."""
    sequencing = get_object_or_404(Sequencing, pk=pk)
    context = {'sequencing': sequencing}
    return context
            
@Render("core/sequencing_create.html")
@login_required()
def sequencing_create(request):
    """sequencing create page."""
    if request.method == 'POST':
        form = SequencingForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            seqdetail_formset = SequencingDetailInlineFormset(
                request.POST,
                instance=instance
                )
            if seqdetail_formset.is_valid():
                seqdetail_formset.save()

            msg = "Successfully created the Sequencing."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to create the sequencing. Please fix the errors below."
            messages.error(request, msg)
            seqdetail_formset = SequencingDetailInlineFormset()
    
    else:
        form = SequencingForm()
        seqdetail_formset = SequencingDetailInlineFormset()

    context = {
        'form': form,
        'seqdetail_formset': seqdetail_formset,
        }
    return context

@Render("core/sequencing_create_from_library.html")
@login_required()
def sequencing_create_from_library(request, from_library):
    """sequencing create page."""
    library = get_object_or_404(Library, pk=from_library)
    if request.method == 'POST':
        form = SequencingForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            seqdetail_formset = SequencingDetailInlineFormset(
                request.POST,
                instance=instance
                )
            if seqdetail_formset.is_valid():
                seqdetail_formset.save()

            msg = "Successfully created the Sequencing."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to create the sequencing. Please fix the errors below."
            messages.error(request, msg)
            seqdetail_formset = SequencingDetailInlineFormset()
    
    else:
        form = SequencingForm()
        seqdetail_formset = SequencingDetailInlineFormset()

    context = {
        'form': form,
        'seqdetail_formset': seqdetail_formset,
        'library': str(library),
        'library_id': from_library,
        }
    return context

@Render("core/sequencing_update.html")
@login_required()
def sequencing_update(request, pk):
    """sequencing update page."""
    sequencing = get_object_or_404(Sequencing, pk=pk)
    if request.method == 'POST':
        form = SequencingForm(request.POST, instance=sequencing)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            seqdetail_formset = SequencingDetailInlineFormset(
                request.POST,
                instance=instance
                )                        
            if seqdetail_formset.is_valid():
                seqdetail_formset.save()

            msg = "Successfully updated the Sequencing."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            msg = "Failed to update the sequencing. Please fix the errors below."
            messages.error(request, msg)
            seqdetail_formset = SequencingDetailInlineFormset(
                instance=sequencing
                )
    
    else:
        form = SequencingForm(
            instance=sequencing
            )
        seqdetail_formset = SequencingDetailInlineFormset(
            instance=sequencing
            )

    context = {
        'pk': pk,
        'form': form,
        'seqdetail_formset': seqdetail_formset,
        }
    return context

@Render("core/sequencing_delete.html")
@login_required()
def sequencing_delete(request, pk):
    """sequencing delete page."""
    sequencing = get_object_or_404(Sequencing, pk=pk)

    if request.method == 'POST':
        sequencing.delete()
        msg = "Successfully deleted the Sequencing."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('core:sequencing_list'))

    context = {
        'sequencing': sequencing,
        'pk': pk
    }
    return context


#============================
# Search view
#----------------------------
def search_view(request):
    query_str = request.GET.get('query_str')
    instance = None

    ## search for samples
    qs = Sample.objects.filter(sample_id=query_str)
    if qs:
        instance = qs[0]

    ## search for libraries
    else:
        qs = Library.objects.filter(pool_id=query_str)
        if qs:
            instance = qs[0]

    if instance:
        return HttpResponseRedirect(instance.get_absolute_url())
    else:
        msg = "Sorry, no match found."
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('index'))
