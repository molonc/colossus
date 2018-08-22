"""
Created on July 10, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

#===========================
# Django imports
#---------------------------
from django.forms import (
    ModelForm,
    inlineformset_factory,
    modelform_factory,
    widgets,
    ModelChoiceField,
    ValidationError,
    Form
)
from django import forms
#===========================
# App imports
#---------------------------
from .models import *

from core.models import(
    DlpLibrary, DlpSequencing
)

#===========================
# Analysis forms (User)
#---------------------------
class AnalysisInformationForm(ModelForm):
    class Meta:
        model = DlpAnalysisInformation
        fields = [
            'library',
            'sequencings',
            'version',
            'aligner',
            'smoothing',
            'reference_genome',
            'analysis_submission_date',
            'verified'
        ]

        labels = {
            'library':'Library',
            'sequencings':'Sequence(s)',
            'version':'Workflow',
            'aligner':'Aligner Option',
            'smoothing':'Smoothing Option',
            'reference_genome':'Reference Genome',
            'analysis_submission_date':'Analysis Submission Date',
        }
        help_texts = {
            'library' :'Library',
            'sequencings': 'Sequence(s) to analyze',
            'version': 'Workflow and version to run',
            'aligner': 'Please provide aligner options',
            'smoothing': 'Please provide smoothing options',
            'reference_genome' : 'Please provide reference genome',
            'analysis_submission_date' :'Analysis Submission Date',
        }
    def __init__(self, *args, **kwargs):
        library = kwargs.pop('library')
        super(AnalysisInformationForm, self).__init__(*args, **kwargs)
        self.fields['sequencings'].widget = widgets.CheckboxSelectMultiple()
        self.fields['sequencings'].queryset = DlpSequencing.objects.filter(library__pk=library.pk)
        self.fields['library'].queryset = DlpLibrary.objects.filter(id=library.pk)
        if not self.instance.pk:
            self.fields['jira_user'] = forms.CharField(max_length=100)
            self.fields['jira_password'] = forms.CharField(widget=forms.PasswordInput)

        # Always select the most recent workflow
        self.fields['version'].initial = DlpAnalysisVersion.objects.latest('pk')


class AnalysisLibrarySelection(Form):
    def __init__(self, *args, **kwargs):
        """Only show DLP libs with sequences."""
        # Call parent constructor method
        super(AnalysisLibrarySelection, self).__init__(*args, **kwargs)

        # Get DlpLibraries with at least one sequence
        all_dlp_libs = DlpLibrary.objects.all()

        # Build a list of DlpLibraries to exclude
        exclude_ids = [dlp_lib.id for dlp_lib in all_dlp_libs
                       if not dlp_lib.dlpsequencing_set.count()]

        # Build the queryset to return
        queryset = all_dlp_libs.exclude(id__in=exclude_ids).order_by('pool_id')

        # Add the library choice field
        self.fields['library'] = ModelChoiceField(queryset=queryset)


class ReferenceGenomeSelection(Form):
    ref_genome = ModelChoiceField(queryset=ReferenceGenome.objects.all())

