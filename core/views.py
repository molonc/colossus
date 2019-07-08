"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""

import os
import csv
import collections
import subprocess
import json
from jira import JIRAError

#============================
# Django imports
#----------------------------
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required #, permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, render
from django.views.generic.base import TemplateView, View
from django.db import transaction
from django.shortcuts import redirect
from django.core.serializers.json import DjangoJSONEncoder
import pandas as pd
from django.conf import settings

#============================
# App imports
#----------------------------
from core.search_util.search_helper import return_text_search
from dlp.models import (
    DlpLibrary
)
from pbal.models import (
    PbalLibrary
)
from tenx.models import (
    TenxLibrary,
    TenxSequencing,
    TenxChip,
    TenxPool
)

from tenx.utils import tenxlibrary_naming_scheme

from .models import (
    Sample,
    SublibraryInformation,
    MetadataField,
    JiraUser,
    Project,
    Analysis
)

from sisyphus.models import *
from .forms import (
    SampleForm,
    AdditionalSampleInfoInlineFormset,
    GSCFormDeliveryInfo,
    GSCFormSubmitterInfo,
    ProjectForm,
    JiraConfirmationForm,
    AddWatchersForm,
    SublibraryForm
)
from .utils import (
    create_sublibrary_models,
    generate_samplesheet,
    generate_gsc_form,
)
from .jira_templates.templates import (
    get_reference_genome_from_sample_id,
    generate_dlp_jira_description,
    generate_tenx_jira_description,
)

from .jira_templates.jira_wrapper import (
    create_ticket,
    get_projects,
    get_project_id_from_name,
    validate_credentials,
    add_watchers,
    add_jira_comment,
    update_description,
)

from colossus.settings import LOGIN_URL

#============================
# Index page
#----------------------------
class IndexView(LoginRequiredMixin, TemplateView):
    """
    Home page.
    """
    login_url = LOGIN_URL
    template_name = "core/index.html"

    def get_context_data(self):
        context = {
            'sample_size': Sample.objects.count(),
            'project_size' : Project.objects.count(),
            'analysis_size': Analysis.objects.count(),
            'dlp_library_size': DlpLibrary.objects.count(),
            'dlp_sequencing_size': DlpSequencing.objects.count(),
            'pbal_library_size': PbalLibrary.objects.count(),
            'pbal_sequencing_size': PbalSequencing.objects.count(),
            'tenx_library_size': TenxLibrary.objects.count(),
            'tenx_sequencing_size': TenxSequencing.objects.count(),
            'tenx_chips_size': TenxChip.objects.count(),
            'tenx_pools_size': TenxPool.objects.count(),
            'analysisinformation_size':DlpAnalysisInformation.objects.count(),
            'analysisrun_size':AnalysisRun.objects.count(),
        }
        return context

@login_required
def gsc_submission_form(request):
  return render(
      request,
      "core/gsc_form.html",
      {"libraries" :
          json.dumps([{
                "value" : library.pk,
                "text" : "{}_{}".format(library.pool_id,library.sample.sample_id),
                "userselect" : False,
            } for library in DlpLibrary.objects.all()],
              cls=DjangoJSONEncoder)}
    )

@login_required
def pipeline_status_page(request):
  samples = Sample.objects.filter(pk__in=[123, 124, 7, 13, 12, 269])
  print(samples)
  return render(
      request,
      "core/vue/status-page.html",
      { "samples" : json.dumps([{
                "id" : s.pk,
                "name" : s.sample_id,
            } for s in samples],
              cls=DjangoJSONEncoder)} 
    )

def gsc_info_post(request):
    selected = DlpLibrary.objects.filter(pk__in=json.loads(request.body.decode('utf-8'))["selected"])
    returnJson = [{
        "Pool ID" : library.pool_id,
        "Sample ID" : library.sample.sample_id,
        "Sample Type": library.sample.sample_type,
        "Number of Sublibraries": library.num_sublibraries,
        "Anonymous Patient ID" : library.sample.anonymous_patient_id,
        "Sex" : library.sample.additionalsampleinformation.sex,
        "Anatomic Site" : library.sample.additionalsampleinformation.anatomic_site,
        "Pathology Disease Name" : library.sample.additionalsampleinformation.pathology_disease_name,
        "Construction Method" : "NanoWellSingleCellGenome",
        "Size Range" : library.dlplibraryquantificationandstorage.size_range,
        "Average Size" : library.dlplibraryquantificationandstorage.average_size,
        "Xenograph" : "Yes",
        "Concentration(nM)" : library.dlplibraryquantificationandstorage.dna_concentration_nm,
        "Volume" : library.dlplibraryquantificationandstorage.dna_volume,
        "Quantification Method" : library.dlplibraryquantificationandstorage.quantification_method,
    } for library in selected]
    return HttpResponse(json.dumps(returnJson, cls=DjangoJSONEncoder), content_type="application/json")


def download_sublibrary_info(request):
    library = get_object_or_404(DlpLibrary, pk=json.loads(request.body.decode('utf-8'))["libraryPk"])
    sublibraries = library.sublibraryinformation_set.all()

    csvString = "Sub-Library ID,Index Sequence\n"
    for sublib in sublibraries:
        csvString += "{},{}-{}\n".format(
            sublib.get_sublibrary_id(),
            sublib.primer_i7,
            sublib.primer_i5
        )

    return HttpResponse(csvString)



#============================
# Sample views
#----------------------------
class SampleList(LoginRequiredMixin, TemplateView):
    """
    List of samples.
    """
    login_url = LOGIN_URL
    template_name = "core/sample_list.html"

    def get_context_data(self):
        context = {
            'samples': Sample.objects.all().order_by('sample_id'),
        }
        return context


class SampleCreate(LoginRequiredMixin, TemplateView):
    """
    Sample create page.
    """
    login_url = LOGIN_URL
    template_name="core/sample_create.html"

    def get_context_and_render(self, request, form, formset, pk=None):
        context = {
            'pk': pk,
            'form': form,
            'formset': formset,
        }
        return render(request, self.template_name, context)

    def get(self, request):
        form = SampleForm()
        formset = AdditionalSampleInfoInlineFormset()
        return self.get_context_and_render(request, form, formset)

    def post(self, request):
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

    def get(self, request, pk):
        sample = get_object_or_404(Sample, pk=pk)
        form=SampleForm(instance=sample)
        formset=AdditionalSampleInfoInlineFormset(instance=sample)
        return self.get_context_and_render(request, form, formset, pk=pk)

    def post(self, request, pk):
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


class SampleDelete(LoginRequiredMixin, TemplateView):

    """
    Sample delete page.
    """
    login_url = LOGIN_URL
    template_name = "core/sample_delete.html"

    def get_context_data(self, pk):
        context = {
            'sample': get_object_or_404(Sample, pk=pk),
            'pk': pk,
        }
        return context

    def post(self, request, pk):
        get_object_or_404(Sample, pk=pk).delete()
        msg = "Successfully deleted the Sample."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('core:sample_list'))

@Render("core/analysis_list.html")
@login_required
def analys_list(request):
    context = {
        'analyses': Analysis.objects.all().order_by('id'),
    }
    return context

@Render("core/analysis_detail.html")
@login_required
def analysis_detail(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)
    library = analysis.__getattribute__(analysis.input_type.lower() + "_library")
    sequencings = analysis.__getattribute__(analysis.input_type.lower() + "sequencing_set")
    context = {
        'analysis': analysis,
        'library': library,
        'sequencings': sequencings
    }
    if analysis.input_type.lower() == 'tenx':
        tenx_pools = list(map(lambda x: x.tenx_pool, sequencings.all()))
        context['tenx_pools'] = tenx_pools
    return context

@Render("core/sample_detail.html")
@login_required
def sample_name_to_id_redirect(request, pk=None, sample_id=None):
    if pk is not None:
        context = dict(
            library_list=['dlp', 'pbal', 'tenx'],
            sample=get_object_or_404(Sample, pk=pk),
            pk=pk
        )
        return context

    elif sample_id is not None:
        pk = get_object_or_404(Sample, sample_id=sample_id).pk
        return redirect('/core/sample/{}'.format(pk))

#============================
# Library views
#----------------------------
class LibraryList(LoginRequiredMixin, TemplateView):

    """
    Library list base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/library_list.html"

    def get_context_data(self):
        context = {
            'libraries': self.library_class.objects.all().order_by(self.order),
            'library_type': self.library_type,
        }
        return context

class LibraryDetail(LoginRequiredMixin, TemplateView):

    """
    Library detail base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/library_detail.html"

    def get_context_and_render(self, request, library, library_type, analyses=None, sublibinfo_fields=None, chip_metadata=None, metadata_fields=None):
        library_dict = self.sort_library_order(library)
        context = {
            'library': library,
            'library_type': library_type,
            'analyses': analyses,
            'sublibinfo_fields': sublibinfo_fields,
            'chip_metadata': chip_metadata,
            'metadata_fields': metadata_fields,
            'library_dict':library_dict,
        }
        return render(request, self.template_name, context)

    def get(self, request, pk):
        library = get_object_or_404(self.library_class, pk=pk)
        library_type = self.library_type
        return self.get_context_and_render(request, library, library_type)

    def sort_library_order(self,library):
            return library.get_field_values()

class LibraryDelete(LoginRequiredMixin, TemplateView):

    """
    Library delete base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/library_delete.html"

    def get_context_data(self, pk):
        context = {
            'library': get_object_or_404(self.library_class, pk=pk),
            'pk': pk,
            'library_type': self.library_type,
        }
        return context

    def post(self, request, pk):
        get_object_or_404(self.library_class, pk=pk).delete()
        msg = "Successfully deleted the Library."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse(self.library_type + ':library_list'))

class JiraTicketConfirm(LoginRequiredMixin, TemplateView):

    login_url = LOGIN_URL

    template_name = 'core/jira_ticket_confirm.html'

    def get(self, request):
        projects = get_projects(request.session['jira_user'], request.session['jira_password'])
        form = JiraConfirmationForm()
        #Set default values for DLP and TenX Library Ticket Creation
        #If default value can't be found, no error will be thrown, and the field will just be empty by default
        if(request.session['library_type'] == 'dlp'):
            form.fields['title'].initial = '{} - {} - {}'.format(request.session['sample_id'], request.session['pool_id'], request.session['additional_title'])
            form.fields['description'].initial = generate_dlp_jira_description(request.session['description'], request.session['library_id'])
            form.fields['reporter'].initial = 'elaks'
        elif(request.session['library_type'] == 'tenx'):
            form.fields['title'].initial = '{} - {}'.format(request.session['sample_id'], request.session['additional_title'])
            form.fields['description'].initial = 'Awaiting first sequencing...'
            form.fields['reporter'].initial = 'coflanagan'

        form.fields['project'].choices = [(str(project.id), project.name) for project in projects]
        form.fields['project'].initial = get_project_id_from_name(request.session['jira_user'], request.session['jira_password'], 'Single Cell')
        context = {
            'form': form,
            'library_type': request.session['library_type']
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = JiraConfirmationForm(request.POST)
        projects = get_projects(request.session['jira_user'], request.session['jira_password'])
        form.fields['project'].choices = [(str(project.id), project.name) for project in projects]
        if form.is_valid():
            try:
                new_issue = create_ticket(username=request.session['jira_user'],
                      password=request.session['jira_password'],
                      project=form['project'].value(),
                      title=form['title'].value(),
                      description=form['description'].value(),
                      reporter=form['reporter'].value(),
                    )
            except JIRAError as e:
                #Do Something
                error_message = "Failed to create the Jira Ticket. {}".format(e.text)
                messages.error(request, error_message)
                return render(request, self.template_name)
            if(request.session['library_type'] == 'dlp'):
                library = DlpLibrary.objects.get(id=request.session['library_id'])
                library.jira_ticket = new_issue
                library.save()
            elif(request.session['library_type'] == 'tenx'):
                library = TenxLibrary.objects.get(id=request.session['library_id'])
                library.jira_ticket = new_issue
                library.save()
            return HttpResponseRedirect('/{}/library/{}'.format(request.session['library_type'], library.id))


class LibraryCreate(LoginRequiredMixin, TemplateView):

    """
    Library create base class.
    """
    login_url = LOGIN_URL

    class Meta:
        abstract = True

    template_name = "core/library_create.html"

    def get_context_data(self, pk=None):
        if pk:
            sample = get_object_or_404(Sample, pk=pk)
        else:
            sample = None

        context = {
            'lib_form': self.lib_form_class(),
            'sublib_form': SublibraryForm(),
            'libdetail_formset': self.libdetail_formset_class(),
            'libcons_formset': self.libcons_formset_class(),
            'libqs_formset': self.libqs_formset_class(),
            'projects': Project.objects.all(),
            'sample': str(sample),
            'sample_id': pk,
            'related_dlp_libs': DlpLibrary.objects.all(),
            'related_tenx_libs': TenxLibrary.objects.all(),
            'library_type': self.library_type,
        }
        return context

    def get(self, request, pk=None):
        context = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        context = self.get_context_data(pk)
        return self._post(request, context)

    def _post(self, request, context, library=None, create=False):

        lib_form = self.lib_form_class(request.POST, instance=library)
        sublib_form = SublibraryForm(request.POST, request.FILES or None)
        context['lib_form'] = lib_form
        context['sublib_form'] = sublib_form

        error_message = ''
        try:
            with transaction.atomic():
                if lib_form.is_valid() and sublib_form.is_valid():
                    instance = lib_form.save(commit=False)
                    if instance.pk is None:
                        create = True
                    all_valid, formsets = self._validate_formsets(request, instance)
                    context.update(formsets)
                    instance.name = tenxlibrary_naming_scheme(instance) if instance.library_type == "tenx" else None
                    instance.save()
                    lib_form.save_m2m()

                    region_metadata = sublib_form.cleaned_data.get('smartchipapp_region_metadata')
                    sublib_results = sublib_form.cleaned_data.get('smartchipapp_results')
                    if region_metadata is not None and sublib_results is not None:
                        instance.sublibraryinformation_set.all().delete()
                        instance.chipregion_set.all().delete()
                        create_sublibrary_models(instance, sublib_results, region_metadata)

                    if all_valid and create:
                        if context['library_type'] != 'pbal':
                            jira_user = lib_form['jira_user'].value()
                            jira_password = lib_form['jira_password'].value()
                            additional_title = lib_form['additional_title'].value()

                        #Add these fields into Session so the JiraTicketConfirm View can access them
                        if validate_credentials(jira_user, jira_password):
                            #For DLP Libaries
                            if(context['library_type'] == 'dlp'):
                                request.session['pool_id'] = str(instance.pool_id)
                                request.session['description'] = instance.description
                            elif(context['library_type'] == 'tenx'):
                                request.session['pool'] = request.POST['tenxlibraryconstructioninformation-0-pool']
                            if context['library_type'] != 'pbal':
                                request.session['jira_user'] = jira_user
                                request.session['jira_password'] = jira_password
                                request.session['additional_title'] = additional_title
                                request.session['sample_id'] = instance.sample.sample_id
                                request.session['library_type'] = context['library_type']
                        else:
                            messages.error(request, 'Invalid Jira Credentials')
                            return render(request, self.template_name, context)
                        # Save the library
                        request.session['library_id'] = instance.id
                        # save the formsets.
                        [formset.save() for formset in formsets.values()]
                        if context["library_type"] == "pbal":
                            return HttpResponseRedirect(instance.get_absolute_url())
                        else:
                            return HttpResponseRedirect(reverse('{}:jira_ticket_confirm'.format(context['library_type'])))
                    elif all_valid and not create:
                        # save the formsets.
                        [formset.save() for formset in formsets.values()]
                        return HttpResponseRedirect('/{}/library/{}'.format(context['library_type'], instance.id))
                else:
                    messages.info(request, lib_form.errors)
                    return HttpResponseRedirect(request.get_full_path())


        except ValueError as e:
            #Can't join into a string when some args are ints, so convert them first
            for arg in e.args:
                if(type(arg) is int):
                    arg = str(arg)
                error_message += arg.encode('ascii', 'ignore') + ' '
            error_message = "Failed to create the library. " + error_message + ". Please fix the errors below."
            messages.error(request, error_message)
            return render(request, self.template_name, context)

    def _validate_formsets(self, request, instance):
        all_valid = True
        formsets = {
            'libdetail_formset': self.libdetail_formset_class(
                request.POST,
                instance=instance,
            ),
            'libcons_formset': self.libcons_formset_class(
                request.POST,
                instance=instance,
            ),
            'libqs_formset': self.libqs_formset_class(
                request.POST,
                request.FILES or None,
                instance=instance,
            ),
        }
        for k, formset in formsets.items():
            if not formset.is_valid():
                all_valid = False
            formsets[k] = formset
        return all_valid, formsets

class LibraryUpdate(LibraryCreate):

    """
    Library update base class.
    """

    class Meta:
        abstract = True

    template_name = "core/library_update.html"

    def get_context_data(self, pk):
        library = get_object_or_404(self.library_class, pk=pk)
        selected_projects = library.projects.all()
        selected_related_dlp_libs = library.relates_to_dlp.all()
        selected_related_tenx_libs = library.relates_to_tenx.all()

        context = {
            'pk': pk,
            'lib_form': self.lib_form_class(instance=library),
            'sublib_form': SublibraryForm(),
            'libdetail_formset': self.libdetail_formset_class(instance=library),
            'libcons_formset': self.libcons_formset_class(instance=library),
            'libqs_formset': self.libqs_formset_class(instance=library),
            'projects': Project.objects.all(),
            'selected_projects': selected_projects,
            'related_dlp_libs': DlpLibrary.objects.all(),
            'related_tenx_libs': TenxLibrary.objects.all(),
            'selected_related_dlp_libs': selected_related_dlp_libs,
            'selected_related_tenx_libs': selected_related_tenx_libs,
            'library_type': self.library_type,
        }
        return context

    def post(self, request, pk, create=False):
        context = self.get_context_data(pk)
        library = get_object_or_404(self.library_class, pk=pk)
        return self._post(request, context, library=library)


#============================
# Project views
#----------------------------
class ProjectList(LoginRequiredMixin, TemplateView):

    """
    Project detail page.
    """
    login_url = LOGIN_URL
    template_name = "core/project_list.html"

    def get_context_data(self):
        context = {
            'projects': Project.objects.all().order_by('name'),
        }
        return context

class ProjectDetail(TemplateView):

    template_name = "core/project_detail.html"

    def get_context_data(self, pk):
        context = {
            'project': get_object_or_404(Project, pk=pk),
        }
        return context


class ProjectDelete(LoginRequiredMixin, TemplateView):

    """
    Project delete page.
    """
    login_url = LOGIN_URL
    template_name = "core/project_delete.html"

    def get_context_data(self, pk):
        context = {
            'project': get_object_or_404(Project, pk=pk),
            'pk': pk,
        }
        return context

    def post(self, request, pk):
        get_object_or_404(Project, pk=pk).delete()
        msg = "Successfully deleted the Project."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('core:project_list'))


class ProjectCreate(LoginRequiredMixin,TemplateView):

    """
    Project create page.
    """
    login_url = LOGIN_URL
    template_name = "core/project_create.html"

    def get_context_data(self):
        context = {
            'form': ProjectForm(),
        }
        return context

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            instance = form.save()
            msg = "Successfully created the %s project." % instance.name
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())


class ProjectUpdate(LoginRequiredMixin, TemplateView):

    """
    Project update page.
    """
    login_url = LOGIN_URL
    template_name = "core/project_update.html"

    def get_context_data(self, pk):
        context = {
            'pk': pk,
            'form': ProjectForm(instance=get_object_or_404(Project, pk=pk)),
        }
        return context

    def post(self, request, pk):
        form = ProjectForm(request.POST, instance=get_object_or_404(Project, pk=pk))
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            msg = "Successfully updated the Project."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.get_absolute_url())

#============================
# Sequencing views
#----------------------------
class SequencingList(LoginRequiredMixin, TemplateView):

    """
    Sequencing list base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/sequencing_list.html"

    def get_context_data(self):

        sequencing_list = self.sequencing_class.objects.all().order_by('library')
        for sequencing in sequencing_list:
            try:
                sequencing.most_recent_lane = sequencing.dlplane_set.order_by('-id')[0].sequencing_date.strftime('%b. %d, %Y')
            except IndexError:
                sequencing.most_recent_lane = None
            except AttributeError:
                sequencing.most_recent_lane = None

        context = {
            'sequencings': sequencing_list,
            'library_type': self.library_type,
        }

        return context




class SequencingDetail(LoginRequiredMixin, TemplateView):

    """
    Sequencing detail base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/sequencing_detail.html"

    def get(self, request, pk):
        key = "gsc_form_metadata_%s" % pk
        download = False
        if key in request.session.keys():
            download = True

        context = {
            'sequencing': get_object_or_404(self.sequencing_class, pk=pk),
            'download': download,
            'library_type': self.library_type,
        }
        return render(request, self.template_name, context)


class AddWatchers(LoginRequiredMixin, TemplateView):

    login_url = LOGIN_URL
    template_name = "core/add_watchers.html"

    def get(self, request):
        if request.session['library_type'] == 'dlp':
            #Set initial checkboxes to every Jira User associated with DLP
            form = AddWatchersForm(initial={'watchers': list(JiraUser.objects.filter(associated_with_dlp=True).values_list('username', flat=True))})
            form.fields['comment'].initial = "A new Sequencing has been created and awaits {} lanes".format(request.session['number_of_lanes_requested'])
        elif request.session['library_type'] == 'tenx':
            form = AddWatchersForm(initial={'watchers': list(JiraUser.objects.filter(associated_with_tenx=True).values_list('username', flat=True))})
            form.fields['comment'].initial = "A new Sequencing has been created and awaits {} lanes".format(request.session['number_of_lanes_requested'])
        else:
            form = AddWatchersForm()
        context = {
            'form': form,
            'library_type': request.session['library_type'],
            'jira_ticket': request.session['jira_ticket'],
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = AddWatchersForm(request.POST)
        if form.is_valid():
            if request.session['library_type'] == 'tenx' and request.session["jira_ticket"]:
                for i in range(0,len(request.session["jira_ticket"])):
                    reference_genome = get_reference_genome_from_sample_id(request.session['sample_id'][i])
                    updated_description = generate_tenx_jira_description(request.session['sequencing_center'], reference_genome, request.session['pool_id'])
                    try:
                        update_description(request.session['jira_user'], request.session['jira_password'], request.session['jira_ticket'][i], updated_description)
                        self.update_watchers(request.session['jira_user'], request.session['jira_password'],
                                             request.session['jira_ticket'][i], form.cleaned_data['watchers'],
                                             form.cleaned_data['comment'])
                    except JIRAError as e:
                        msg = e.text
                        messages.error(request, msg)
                        return self.get(request)
            elif request.session['library_type'] == 'dlp':
                try:
                    self.update_watchers(request.session['jira_user'], request.session['jira_password'], request.session['jira_ticket'], form.cleaned_data['watchers'], form.cleaned_data['comment'])
                except JIRAError as e:
                    msg = e.text
                    messages.error(request, msg)
                    return self.get(request)
            else:
                messages.error(request, "Failed to create Jira ticket")
                return self.get(request)
        return HttpResponseRedirect('/{}/sequencing/{}'.format(request.session['library_type'], request.session['sequencing_id']))

    def update_watchers(self, user, password, ticket, watchers, comment):
        add_watchers(user, password, ticket, watchers)
        add_jira_comment(user, password, ticket, comment)

class SequencingCreate(LoginRequiredMixin, TemplateView):

    """
    Sequencing create base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/sequencing_create.html"

    def get_context_and_render(self, request, from_library, form):
        if from_library:
            library = get_object_or_404(self.library_class, pk=from_library)
        else:
            library = None

        context = {
            'form': form,
            'library': str(library),
            'library_id': from_library,
            'related_seqs': self.sequencing_class.objects.all(),
            'library_type': self.library_type,
        }
        return render(request, self.template_name, context)

    def get(self, request, from_library=None):
        form = self.form_class()
        return self.get_context_and_render(request, from_library, form)

    def post(self, request, from_library=None):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)

            if(validate_credentials(form.cleaned_data['jira_user'], form.cleaned_data['jira_password']) ):
                request.session['jira_user'] = form.cleaned_data['jira_user']
                request.session['jira_password'] = form.cleaned_data['jira_password']
                request.session['library_type'] = self.library_type
                if (self.library_type == 'dlp'):
                    library = instance.library
                    request.session['jira_ticket'] = library.jira_ticket
                    request.session['sample_id'] = library.sample.sample_id
                if (self.library_type == 'tenx'):
                    request.session['jira_ticket'] = instance.tenx_pool.jira_tickets()[0] if instance.tenx_pool else []
                    request.session['sample_id'] = instance.tenx_pool.jira_tickets()[1] if instance.tenx_pool else []
                    request.session['pool_id'] = instance.tenx_pool.id if instance.tenx_pool else None
                request.session['number_of_lanes_requested'] = instance.number_of_lanes_requested
                request.session['sequencing_center'] = instance.sequencing_center
            else:
                messages.error(request, 'Invalid Jira Credentials')
                return self.get_context_and_render(request, from_library, form)

            instance.save()
            request.session['sequencing_id'] = instance.id
            messages.success(request, "Successfully created the Sequencing.")
            return HttpResponseRedirect(reverse('{}:add_watchers'.format(self.library_type)))
        else:
            msg = "Failed to create the sequencing. Please fix the errors below."
            messages.error(request, msg)
            return self.get_context_and_render(request, from_library, form)

class SequencingUpdate(LoginRequiredMixin, TemplateView):

    """
    Sequencing update base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/sequencing_update.html"

    def get_context_and_render(self, request, sequencing, form):
        context = {
            'pk': sequencing.pk,
            'form': form,
            'library_type': self.library_type,
        }

        if self.library_type != "tenx":
            context['related_seqs'] =  self.sequencing_class.objects.all(),
            context['selected_related_seqs'] =  sequencing.relates_to.only(),

        return render(request, self.template_name, context)

    def get(self, request, pk):
        sequencing = get_object_or_404(self.sequencing_class, pk=pk)
        form = self.form_class(instance=sequencing)
        return self.get_context_and_render(request, sequencing, form)

    def post(self, request, pk):
        sequencing = get_object_or_404(self.sequencing_class, pk=pk)
        old_count = sequencing.number_of_lanes_requested
        form = self.form_class(request.POST, instance=sequencing)
        if form.is_valid():
            instance = form.save(commit=False)
            #Don't require JIRA integration if not updating the number of lanes field
            if(old_count != instance.number_of_lanes_requested):
                jira_comment = "Sequencing Goal has been updated from {} to {} for this [Sequencing|http://colossus.bcgsc.ca/{}/sequencing/{}]".format(old_count, instance.number_of_lanes_requested, self.library_type, pk)
                try:
                    if self.library_type == "tenx" and instance.tenx_pool:
                        jira_tickets, sample_ids = instance.tenx_pool.jira_tickets()
                        for jira in jira_tickets:
                            add_jira_comment(
                                form.cleaned_data['jira_user'],
                                form.cleaned_data['jira_password'],
                                jira,
                                jira_comment
                            )
                    elif self.library_type == "dlp":
                        add_jira_comment (
                            form.cleaned_data['jira_user'],
                            form.cleaned_data['jira_password'],
                            instance.library.jira_ticket,
                            jira_comment
                        )
                    else:
                        messages.error(request, "Failed to update Jira Ticket")
                        return self.get_context_and_render(request, sequencing, form)

                except JIRAError as e:
                    msg = "JIRA Error: {}".format(e.response.reason)
                    messages.error(request, msg)
                    return self.get_context_and_render(request, sequencing, form)

            instance.save()
            form.save_m2m()

            messages.success(request, "Successfully updated the Sequencing.")
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            messages.error(request, "Failed to update the sequencing. Please fix the errors below.")
            return self.get_context_and_render(request, sequencing, form)


class SequencingDelete(LoginRequiredMixin, TemplateView):

    """
    Sequencing delete base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/sequencing_delete.html"

    def get_context_data(self, pk):
        context = {
            'sequencing': get_object_or_404(self.sequencing_class, pk=pk),
            'pk': pk,
            'library_type': self.library_type,
        }
        return context

    def post(self, request, pk):
        get_object_or_404(self.sequencing_class, pk=pk).delete()
        msg = "Successfully deleted the Sequencing."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse(self.library_type + ':sequencing_list'))


#============================
# Lane views
#----------------------------
class LaneCreate(LoginRequiredMixin, TemplateView):

    """
    Lane create page.
    """
    login_url = LOGIN_URL
    template_name = "core/lane_create.html"

    def get_context_and_render(self, request, from_sequencing, form):
        if from_sequencing:
            sequencing = get_object_or_404(self.sequencing_class, pk=from_sequencing)
        else:
            sequencing = None

        context = {
            'form': form,
            'sequencing': str(sequencing),
            'sequencing_id': from_sequencing,
            'library_type': self.library_type,
        }
        return render(request, self.template_name, context)

    def get(self, request, from_sequencing=None):
        form = self.form_class()
        return self.get_context_and_render(request, from_sequencing, form)

    def post(self, request, from_sequencing=None):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save()
            msg = "Successfully created the lane."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.sequencing.get_absolute_url())
        else:
            msg = "Failed to create the lane. Please fix the errors below."
            messages.error(request, msg)
            return self.get_context_and_render(request, from_sequencing, form)




class LaneUpdate(LoginRequiredMixin, TemplateView):

    """
    Lane update base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/lane_update.html"

    def get_context_and_render(self, request, lane, form, pk):
        context = {
            'sequencing': lane.sequencing,
            'sequencing_id': lane.sequencing_id,
            'form': form,
            'pk': pk,
            'library_type': self.library_type,
        }
        return render(request, self.template_name, context)

    def get(self, request, pk):
        lane = get_object_or_404(self.lane_class, pk=pk)
        form = self.form_class(instance=lane)
        return self.get_context_and_render(request, lane, form, pk)

    def post(self, request, pk):
        lane = get_object_or_404(self.lane_class, pk=pk)
        form = self.form_class(request.POST, instance=lane)
        if form.is_valid():
            instance = form.save()
            msg = "Successfully updated the lane."
            messages.success(request, msg)
            return HttpResponseRedirect(instance.sequencing.get_absolute_url())
        else:
            msg = "Failed to update the lane. Please fix the errors below."
            messages.error(request, msg)
            return self.get_context_and_render(request, lane, form, pk)

class LaneDelete(LoginRequiredMixin, TemplateView):

    """
    Lane delete base class.
    """
    login_url = LOGIN_URL
    class Meta:
        abstract = True

    template_name = "core/lane_delete.html"

    def get_context_and_render(self, request, lane, pk, sequencing):
        context = {
            'lane': lane,
            'pk': pk,
            'sequencing_id': sequencing.id,
            'library_type': self.library_type,
        }
        return render(request, self.template_name, context)

    def get(self, request, pk):
        lane = get_object_or_404(self.lane_class, pk=pk)
        sequencing = lane.sequencing
        return self.get_context_and_render(request, lane, pk, sequencing)

    def post(self, request, pk):
        lane = get_object_or_404(self.lane_class, pk=pk)
        sequencing = lane.sequencing
        lane.delete()
        msg = "Successfully deleted the Lane."
        messages.success(request, msg)
        return HttpResponseRedirect(sequencing.get_absolute_url())

#============================
# Search view
#----------------------------
class SearchView(TemplateView):

    login_url = LOGIN_URL
    template_name = "core/search/search_main.html"


    def get_context_data(self):

        query_str = self.request.GET.get('query_str')

        if len(query_str) < 1:
            return {"total" : 0}

        return return_text_search(query_str)
