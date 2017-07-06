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
from django.db import transaction

#============================
# App imports
#----------------------------
from .helpers import Render
from .models import (
    Sample,
    Library,
    Sequencing,
    SublibraryInformation,
    ChipRegion,
    ChipRegionMetadata,
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
    GSCFormDeliveryInfo,
    GSCFormSubmitterInfo,
    ProjectForm
    )
from .utils import (
    create_sublibrary_models,
    generate_samplesheet,
    generate_gsc_form,
    )

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
            

@method_decorator(login_required, name='dispatch')
class SampleCreate(TemplateView):

    """"
    Sample create page.
    """

    template_name="core/sample_create.html"

    def get_context_and_render(self, request, form, formset, pk=None):
        context = {
            'pk':pk,
            'form': form,
            'formset': formset
        }
        return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        form = SampleForm()
        formset = AdditionalSampleInfoInlineFormset()
        return self.get_context_and_render(request, form, formset)

    def post(self, request, *args, **kwargs):
        form = SampleForm(request.POST)
        formset = AdditionalSampleInfoInlineFormset(request.POST)
        if form.is_valid() and formset.is_valid():
            instance = form.save(commit=False)
            formset.instance = instance
            instance.save()
            formset.save()
            msg = "Successfully created the Sample."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())

        msg = "Failed to create the sample. Please fix the errors below."
        messages.error(request, msg)
        return self.get_context_and_render(request, form, formset)

class SampleUpdate(SampleCreate):
    """
    Sample update page.
    """

    template_name = "core/sample_update.html"

    def get(self, request, pk, *args, **kwargs):
        sample = get_object_or_404(Sample, pk=pk)
        form=SampleForm(instance=sample)
        formset=AdditionalSampleInfoInlineFormset(instance=sample)
        return self.get_context_and_render(request, form, formset, pk=pk)

    def post(self, request, pk, *args, **kwargs):
        sample = get_object_or_404(Sample, pk=pk)
        form = SampleForm(request.POST, instance=sample)
        formset = AdditionalSampleInfoInlineFormset(request.POST, instance=sample)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            msg = "Successfully updated the Sample."
            messages.success(request, msg)
            return HttpResponseRedirect(sample.get_absolute_url())

        msg = "Failed to update the sample. Please fix the errors below."
        messages.error(request, msg)
        return self.get_context_and_render(request, form, formset, pk=pk)

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
        return self._post(request, context, *args, **kwargs)

    def _post(self, request, context, *args, **kwargs):
        ## this is becaues of this django feature:
        ## https://code.djangoproject.com/ticket/1130
        request.POST['projects'] = ','.join(request.POST.getlist('projects'))

        lib_form = LibraryForm(request.POST, instance=kwargs.get('library', None))
        sublib_form = SublibraryForm(request.POST, request.FILES or None)
        context['lib_form'] = lib_form
        context['sublib_form'] = sublib_form

        error_message = ''
        try:
            with transaction.atomic():
                if lib_form.is_valid() and sublib_form.is_valid():
                    # if 'commit=True' when saving lib_form, then it strangely
                    # raises the following error when trying to save the
                    # ManyToMany 'Projects' field:
                    # 'LibraryForm' object has no attribute 'save_m2m'.
                    # see this: https://stackoverflow.com/questions/7083152/is-save-m2m-required-in-the-django-forms-save-method-when-commit-false
                    instance = lib_form.save(commit=False)
                    all_valid, formsets = self._validate_formsets(request, instance)
                    context.update(formsets)
                    if all_valid:
                        instance.save()
                        # save the ManyToMany field.
                        lib_form.save_m2m()
                        # Add information from SmartChipApp files
                        region_codes = sublib_form.cleaned_data.get('smartchipapp_region_codes')
                        region_metadata = sublib_form.cleaned_data.get('smartchipapp_region_metadata')
                        sublib_results = sublib_form.cleaned_data.get('smartchipapp_results')
                        if region_codes is not None and region_metadata is not None and sublib_results is not None:
                            instance.sublibraryinformation_set.all().delete()
                            create_sublibrary_models(instance, sublib_results, region_codes, region_metadata)
                        # save the formsets.
                        [formset.save() for formset in formsets.values()]
                        messages.success(request, "Successfully created the Library.")
                        return HttpResponseRedirect(instance.get_absolute_url())
        except ValueError as e:
            error_message = ' '.join(e.args)

        error_message = "Failed to create the library. " + error_message + ". Please fix the errors below."
        messages.error(request, error_message)
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
        library = get_object_or_404(Library, pk=pk)
        return self._post(request, context, *args, library=library, **kwargs)


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
    key = "gsc_form_metadata_%s" % pk
    donwload = False
    if key in request.session.keys():
        donwload = True
    context = {
    'sequencing': sequencing,
    'download': donwload,
    }
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
    ofilename, ofilepath = generate_samplesheet(pk)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % ofilename
    ofile = open(ofilepath, 'r')
    response.write(ofile.read())
    ofile.close()
    os.remove(ofilepath)
    return response

def sequencing_get_queried_samplesheet(request, pool_id, flowcell):
    """ make downloading samplesheets from flowcell possible """

    try:
        pk = Sequencing.objects.get(sequencingdetail__flow_cell_id=flowcell, library__pool_id=pool_id).pk
        return sequencing_get_samplesheet(request, pk)
    except Sequencing.DoesNotExist:
        msg = "Sorry, no sequencing with flowcell {} and chip id {} found.".format(flowcell, pool_id)
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('index'))


@method_decorator(login_required, name='dispatch')
class SequencingCreateGSCFormView(TemplateView):

    """
    Sequencing GSC submission form.
    """

    template_name = "core/sequencing_create_gsc_form.html"

    def get_context_data(self, pk):
        context = {
        'pk': pk,
        'delivery_info_form': GSCFormDeliveryInfo(),
        'submitter_info_form': GSCFormSubmitterInfo(),
        }
        return context

    def get(self, request, pk):
        context = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk):
        sequencing = get_object_or_404(Sequencing, pk=pk)
        context = self.get_context_data(pk)
        delivery_info_form = GSCFormDeliveryInfo(request.POST)
        submitter_info_form = GSCFormSubmitterInfo(request.POST)
        if delivery_info_form.is_valid() and submitter_info_form.is_valid():
            key = "gsc_form_metadata_%s" % pk
            request.session[key] = request.POST
            msg = "Successfully started downloading the GSC submission form."
            messages.success(request, msg)
            return HttpResponseRedirect(sequencing.get_absolute_url())
        else:
            context['delivery_info_form'] = delivery_info_form
            context['submitter_info_form'] = submitter_info_form
            msg = "please fix the errors below."
            messages.error(request, msg)
        return render(request, self.template_name, context)

def sequencing_get_gsc_form(request, pk):
    """generate downloadable GSC submission form."""
    key = "gsc_form_metadata_%s" % pk
    metadata = request.session.pop(key)
    ofilename, ofilepath = generate_gsc_form(pk, metadata)
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
    if Sample.objects.filter(sample_id=query_str):
        instance = Sample.objects.filter(sample_id=query_str)[0]

    ## search for libraries
    elif Library.objects.filter(pool_id=query_str):
        instance = Library.objects.filter(pool_id=query_str)[0]

    ## search for Jira Ticket
    elif Library.objects.filter(jira_ticket=query_str):
        instance = Library.objects.filter(jira_ticket=query_str)[0]

    if instance:
        return HttpResponseRedirect(instance.get_absolute_url())
    else:
        msg = "Sorry, no match found."
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('index'))

#============================
# Summary view
#----------------------------
@Render("core/summary.html")
def summary_view(request):

    library_per_sample_count = {s.sample_id : s.library_set.count()
                    for s in Sample.objects.all()}

    sublibrary_per_sample_count = { s.sample_id : s.sublibraryinformation_set.count()
                                   for s in Sample.objects.all()}

    context ={
        'library_per_sample': library_per_sample_count,
        'sublibrary_per_sample': sublibrary_per_sample_count,
        'total_sublibs': SublibraryInformation.objects.count(),
        'total_libs': Library.objects.count(),
        'samples':Sample.objects.all().order_by('sample_id')
    }

    return context
