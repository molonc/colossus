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
    library = ModelChoiceField(queryset=DlpLibrary.objects.all().order_by('pool_id'))


class ReferenceGenomeSelection(Form):
    ref_genome = ModelChoiceField(queryset=ReferenceGenome.objects.all())

