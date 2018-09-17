"""
Created on July 6, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

#============================
# Django imports
#----------------------------
from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.generic import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect


#============================
# App imports
#----------------------------
from jira import JIRA, JIRAError

from core.helpers import *
from core.models import (
    DlpLibrary,
    DlpSequencingDetail,
    DlpLane)
from .forms import *
from .models import *


#============================
# Home page of the app
#----------------------------
@Render("sisyphus/home.html")
def home_view(request):
    """home page of the app."""
    context = {}
    return context

#============================
# Analysis Information (for general User) Views
#----------------------------
@Render("sisyphus/analysisinformation_choose_library.html")
@login_required()
def analysisinformation_create_choose_library(request):
    """ Library selection before proceding with analysis information creation """
    if request.method == 'POST':
        form = AnalysisLibrarySelection(request.POST)

        if form.is_valid():
            library_pk = form.cleaned_data['library'].pk

            return HttpResponseRedirect(
                reverse('sisyphus:analysisinformation_create_from_library',
                        kwargs={'from_library': library_pk}))
    else:
        form = AnalysisLibrarySelection()

        context = {'form': form}
        return context


@method_decorator(login_required, name='dispatch')
class AnalysisInformationCreate(CreateView):
    form_class = AnalysisInformationForm
    template_name = 'sisyphus/analysisinformation_create.html'

    def get_context_data(self, **kwargs):
        library = get_object_or_404(DlpLibrary, pk=kwargs.get('from_library'))

        # Assigning self.object to self is required so that in the
        # AnalysisInformationForm, access to the instance of
        # AnalysisInformation in the AnalysisInformationCreate view is
        # possible
        self.object = DlpAnalysisInformation()
        self.library = library

        # adding library to TEMPLATE context here
        context = super(AnalysisInformationCreate, self).get_context_data()

        if DlpSequencing.objects.filter(library__pk=library.pk).filter().exists():
            context_dict = {}

            for sequences in DlpSequencing.objects.filter(library__pk=library.pk).filter():
                flow_cell_id = DlpLane.objects.filter(
                    sequencing=sequences).values_list('flow_cell_id', flat=True)
                context_dict[str(sequences)] = flow_cell_id

            context.update({'library': library, 'lane': context_dict})
            return context

        context.update({'library':library})
        return context

    def get_form_kwargs(self):
        """
            get form context, and adding library to modelform context,
            so that filter on sequences based on library is possible
        """
        kwargs = super(AnalysisInformationCreate, self).get_form_kwargs()
        kwargs.update({'library':self.library})
        return kwargs

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        self.library = get_object_or_404(DlpLibrary, pk=kwargs.get('from_library'))
        form = self.get_form()
        if form.is_valid():
            # Try creating a Jira ticket
            try:
                analysis_jira_ticket = self.create_jira(form)
            except JIRAError as e:
                # Failed to create Jira ticket. Show a message
                # containing what went wrong
                messages.error(request, e.text)
                return HttpResponseRedirect(request.get_full_path())

            # need to save analysis information in order to set many-to-many field
            analysis_information = form.save()
            analysis_information.analysis_jira_ticket = analysis_jira_ticket
            sequencings = form['sequencings'].value()
            analysis_information.lanes = DlpLane.objects.filter(sequencing__in=sequencings).filter()
            analysis_information.analysis_run = AnalysisRun.objects.create(
                log_file=" ",
                last_updated=None)
            analysis_information.save()

            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

    def get_credentials(self, jira_user, jira_password):
        username = str(jira_user)
        password = str(jira_password)
        return username, password

    def create_jira(self, form):
        #  Get authentication info for the JIRA login
        auth = self.get_credentials(form['jira_user'].value(), form['jira_password'].value())

        # Create the JIRA ticket
        jira = JIRA('https://www.bcgsc.ca/jira/', basic_auth=auth)
        library = form['library'].value()
        library = get_object_or_404(DlpLibrary, id=library)
        title = "Analysis of " + str(library)
        issue_dict = {
            'project': {'id': 11220},
            'summary': title,
            'issuetype': {'name': 'Sub-task'},
            'priority': {'name': 'Medium'},
            'assignee': {'name': 'sochan'},
            'parent': {'id': str(library.jira_ticket)},
        }
        new_issue = jira.create_issue(fields=issue_dict)
        return str(new_issue)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        """
        If the form is valid, save the associated model, and create the
        associated analysis run model
        """
        self.object = form.save()
        return super(AnalysisInformationCreate, self).form_valid(form)

    def form_invalid(self, form, **kwargs):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors. Also passing library pk in kwargs.
        """
        return self.render_to_response(self.get_context_data(form=form, **kwargs))


@method_decorator(login_required, name='dispatch')
class AnalysisInformationUpdate(UpdateView):
    """ Analysis update view """

    form_class = AnalysisInformationForm
    template_name = 'sisyphus/analysisinformation_update.html'

    def get_context_data(self, **kwargs):
        self.object = get_object_or_404(DlpAnalysisInformation, pk=kwargs.get('analysis_pk'))
        self.library = get_object_or_404(DlpLibrary, pk=kwargs.get('library_pk'))
        context = super(AnalysisInformationUpdate, self).get_context_data()
        context.update({'analysisinformation':self.object,
                        'library':self.library})
        return context

    def get_form_kwargs(self):
        kwargs = super(AnalysisInformationUpdate, self).get_form_kwargs()
        kwargs.update({'library': self.library})
        return kwargs

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(DlpAnalysisInformation, pk=kwargs.get('analysis_pk'))
        self.library = get_object_or_404(DlpLibrary, pk=kwargs.get('library_pk'))
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

    def form_invalid(self, form, **kwargs):
        return self.render_to_response(self.get_context_data(form=form, **kwargs))


@Render("sisyphus/analysis_delete.html")
@login_required()
def analysis_delete(request, pk):
    """analysis delete page."""
    analysis = get_object_or_404(DlpAnalysisInformation, pk=pk)

    if request.method == 'POST':
        analysis.delete()
        msg = "Successfully deleted the Analysis."
        messages.success(request, msg)
        return HttpResponseRedirect(reverse('sisyphus:analysisinformation_list'))

    context = {
        'analysis': analysis,
        'pk': pk
    }
    return context


@Render("sisyphus/analysisinformation_list.html")
def analysisinformation_list(request):
    """list of analysis information."""

    context = {
        'analyses': DlpAnalysisInformation.objects.all().order_by('analysis_jira_ticket'),
    }
    return context


class AnalysisInformationDetailView(DetailView):
    model = DlpAnalysisInformation
    def get_context_data(self, **kwargs):
        context = super(AnalysisInformationDetailView, self).get_context_data(**kwargs)
        instance_sequencings = context['object'].sequencings.all()
        context['library'] = DlpLibrary.objects.filter(
            dlpsequencing__in=instance_sequencings).distinct()[0]
        context['analysisrun'] = context['object'].analysis_run
        return context
