"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os
#============================
# Django imports
#----------------------------
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required #, permission_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import TemplateView

#============================
# App imports
#----------------------------
from .helpers import Render
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
from .utils import bulk_create_sublibrary, generate_samplesheet

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
    'sample_size': Sample.objects.count(),
    'library_size': Library.objects.count(),
    'sequencing_size': Sequencing.objects.count()
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
            
@method_decorator(login_required, name='dispatch')
class LibraryCreate(TemplateView):

    """
    Library create page.
    """

    template_name = "core/library_create.html"

    def get_context_data(self, from_sample=None):
        if from_sample:
            sample = get_object_or_404(Sample, pk=from_sample)
        else:
            sample = None
        context = {
        'lib_form': LibraryForm(),
        'sublib_form': SublibraryForm(),
        'libdetail_formset': LibrarySampleDetailInlineFormset(),
        'libcons_formset': LibraryConstructionInfoInlineFormset(),
        'libqs_formset': LibraryQuantificationAndStorageInlineFormset(),
        'projects': [t.name for t in Tag.objects.all()],
        'sample': str(sample),
        'sample_id': from_sample,
        'related_libs': Library.objects.all()
        }
        return context

    def get(self, request, from_sample=None, *args, **kwargs):
        context = self.get_context_data(from_sample)
        return render(request, self.template_name, context)

    def post(self, request, from_sample=None, *args, **kwargs):
        context = self.get_context_data(from_sample)
        ## this is becaues of this django feature:
        ## https://code.djangoproject.com/ticket/1130
        request.POST['projects'] = ','.join(request.POST.getlist('projects'))

        lib_form = LibraryForm(request.POST)
        sublib_form = SublibraryForm(request.POST, request.FILES or None)
        context['lib_form'] = lib_form
        context['sublib_form'] = sublib_form
        if lib_form.is_valid() and sublib_form.is_valid():
            # if 'commit=True' when saving lib_form, then it strangely
            # raises the following error when trying to save the
            # ManyToMany 'Projects' field:
            # 'LibraryForm' object has no attribute 'save_m2m'.
            instance = lib_form.save(commit=False)
            all_valid, formsets = self._validate_formsets(request, instance)
            context.update(formsets)
            if all_valid:
                instance.save()
                # save the ManyToMany field.
                lib_form.save_m2m()
                # Populate the SmartChipApp result file in SublibraryForm.
                df = sublib_form.cleaned_data.get('smartchipapp_df')
                if df is not None and not df.empty:
                    num_sublibraries = bulk_create_sublibrary(
                        instance,
                        df
                        )
                    instance.num_sublibraries = num_sublibraries
                    instance.save()
                # save the formsets.
                [formset.save() for formset in formsets.values()]
                msg = "Successfully created the Library."
                messages.success(request, msg)
                return HttpResponseRedirect(instance.get_absolute_url())

        msg = "Failed to create the library. Please fix the errors below."
        messages.error(request, msg)
        return render(request, self.template_name, context)

    def _validate_formsets(self, request, instance):
        all_valid = True
        formsets = {
        'libdetail_formset': LibrarySampleDetailInlineFormset(
            request.POST,
            instance=instance
            ),
        'libcons_formset': LibraryConstructionInfoInlineFormset(
            request.POST,
            instance=instance
            ),
        'libqs_formset': LibraryQuantificationAndStorageInlineFormset(
            request.POST,
            request.FILES or None,
            instance=instance
            )
        }
        for k, formset in formsets.items():
            if not formset.is_valid():
                all_valid = False
            formsets[k] = formset
        return all_valid, formsets


class LibraryUpdate(LibraryCreate):

    """
    Library update page.
    """

    template_name = "core/library_update.html"

    def get_context_data(self, pk):
        library = get_object_or_404(Library, pk=pk)
        selected_projects = library.projects.names()
        selected_related_libs = library.relates_to.only()
        context = {
        'pk': pk,
        'lib_form': LibraryForm(instance=library),
        'sublib_form': SublibraryForm(),
        'libdetail_formset': LibrarySampleDetailInlineFormset(
            instance=library
            ),
        'libcons_formset': LibraryConstructionInfoInlineFormset(
            instance=library
            ),
        'libqs_formset': LibraryQuantificationAndStorageInlineFormset(
            instance=library
            ),
        'projects': [t.name for t in Tag.objects.all()],
        'selected_projects': selected_projects,
        'related_libs': Library.objects.all(),
        'selected_related_libs': selected_related_libs
        }
        return context

    def get(self, request, pk, *args, **kwargs):
        context = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        context = self.get_context_data(pk)
        ## this is becaues of this django feature:
        ## https://code.djangoproject.com/ticket/1130
        request.POST['projects'] = ','.join(request.POST.getlist('projects'))

        library = get_object_or_404(Library, pk=pk)
        lib_form = LibraryForm(request.POST, instance=library)
        sublib_form = SublibraryForm(request.POST, request.FILES or None)
        context['lib_form'] = lib_form
        context['sublib_form'] = sublib_form
        if lib_form.is_valid() and sublib_form.is_valid():
            # if 'commit=True' when saving lib_form, then it strangely
            # raises the following error when trying to save the
            # ManyToMany 'Projects' field:
            # 'LibraryForm' object has no attribute 'save_m2m'.
            instance = lib_form.save(commit=False)
            all_valid, formsets = self._validate_formsets(request, instance)
            context.update(formsets)
            if all_valid:
                instance.save()
                # save the ManyToMany field.
                lib_form.save_m2m()
                # Populate the SmartChipApp result file in SublibraryForm.
                df = sublib_form.cleaned_data.get('smartchipapp_df')
                if df is not None and not df.empty:
                    num_sublibraries = bulk_create_sublibrary(
                        instance,
                        df
                        )
                    instance.num_sublibraries = num_sublibraries
                    instance.save()
                # save the formsets.
                [formset.save() for formset in formsets.values()]
                msg = "Successfully created the Library."
                messages.success(request, msg)
                return HttpResponseRedirect(instance.get_absolute_url())

        msg = "Failed to create the library. Please fix the errors below."
        messages.error(request, msg)
        return render(request, self.template_name, context)


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
def sequencing_create(request, from_library=None):
    """sequencing create page."""
    if from_library:
        library = get_object_or_404(Library, pk=from_library)
    else:
        library = None
    if request.method == 'POST':
        form = SequencingForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
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
        'related_seqs': Sequencing.objects.all()
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
            form.save_m2m()
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

    selected_related_seqs = sequencing.relates_to.only()
    context = {
        'pk': pk,
        'form': form,
        'seqdetail_formset': seqdetail_formset,
        'related_seqs': Sequencing.objects.all(),
        'selected_related_seqs': selected_related_seqs
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

def sequencing_get_samplesheet(request, pk):
    """generate downloadable samplesheet."""
    sequencing = get_object_or_404(Sequencing, pk=pk)
    ofilename = str(sequencing) + '_samplesheet.csv'
    ofilepath = generate_samplesheet(sequencing, ofilename)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % ofilename
    ofile = open(ofilepath, 'r')
    response.write(ofile.read())
    ofile.close()
    os.remove(ofilepath)
    return response


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
