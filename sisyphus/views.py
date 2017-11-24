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
from core.helpers import *
from core.models import (
    DlpLibrary,
    DlpSequencingDetail
)
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
    if (request.method == 'POST'):
        form = AnalysisLibrarySelection(request.POST)
        if form.is_valid():
            library_pk = form.cleaned_data['library'].pk
            return HttpResponseRedirect(
                reverse('sisyphus:analysisinformation_create_from_library',
                        kwargs={'from_library':library_pk}))
    else:
        form = AnalysisLibrarySelection()
        context = {'form':form}
        return context


@method_decorator(login_required, name='dispatch')
class AnalysisInformationCreate(CreateView):
    form_class=AnalysisInformationForm
    template_name='sisyphus/analysisinformation_create.html'

    def get_context_data(self, **kwargs):
        library = get_object_or_404(DlpLibrary, pk=kwargs.get('from_library'))
        # Assigning self.object to self is required so that in the AnalysisInformationForm,
        # access to the instance of AnalysisInformation in the AnalysisInformationCreate view is possible
        self.object = AnalysisInformation()
        self.library = library

        # adding library to TEMPLATE context here
        context =  super(AnalysisInformationCreate, self).get_context_data()
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
        self.library=get_object_or_404(DlpLibrary, pk=kwargs.get('from_library'))
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        """
        If the form is valid, save the associated model, and create the associated analysis run model
        """
        self.object = form.save()
        analysis_run = AnalysisRun(
                analysis_information=self.object,
                analysis_submission_date=timezone.now(),
                analysis_completion_date=None,
                run_status='W',
        )
        analysis_run.save()
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
        self.object = get_object_or_404(AnalysisInformation, pk=kwargs.get('analysis_pk'))
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
        self.object = get_object_or_404(AnalysisInformation, pk=kwargs.get('analysis_pk'))
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
    analysis = get_object_or_404(AnalysisInformation, pk=pk)

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
        'analyses': AnalysisInformation.objects.all().order_by('analysis_jira_ticket'),
    }
    return context


class AnalysisInformationDetailView(DetailView):
    model = AnalysisInformation
    def get_context_data(self, **kwargs):
        context = super(AnalysisInformationDetailView, self).get_context_data(**kwargs)
        instance_sequencings = context['object'].sequencings.all()
        context['library']=DlpLibrary.objects.filter(sequencing__in=instance_sequencings).distinct()[0]
        context['analysisrun']=context['object'].analysisrun
        return context
