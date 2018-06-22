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
            'priority_level',
            'analysis_jira_ticket',
            'version',
            'aligner',
            'smoothing',
            'reference_genome',
            'analysis_submission_date',
            'sftp_path',
            'tantalus_path',
        ]

        labels = {
            'library':'Library',
            'sequencings':'Sequence(s)',
            'priority_level':'Priority Level',
            'analysis_jira_ticket':'Jira Ticket',
            'version':'Workflow',
            'aligner':'Aligner Option',
            'smoothing':'Smoothing Option',
            'reference_genome':'Reference Genome',
            'analysis_submission_date':'Analysis Submission Date',
            'sftp_path':"SFTP Path",
            'tantalus_path':"Tantalus Path",
        }
        help_texts = {
            'library' :'Library',
            'sequencings': 'Sequence(s) to analyze',
            'priority_level': 'Priority should match the urgency of this request.',
            'analysis_jira_ticket': 'Jira Ticket associated with this request',
            'version': 'Workflow and version to run',
            'aligner': 'Please provide aligner options',
            'smoothing': 'Please provide smoothing options',
            'reference_genome' : 'Please provide reference genome',
            'analysis_submission_date' :'Analysis Submission Date',
            'sftp_path':"Sftp path",
            'tantalus_path':"Tantalus path",
        }
    def __init__(self, *args, **kwargs):
        library = kwargs.pop('library')
        super(AnalysisInformationForm, self).__init__(*args, **kwargs)
        self.fields['sequencings'].widget = widgets.CheckboxSelectMultiple()
        self.fields['sequencings'].queryset = DlpSequencing.objects.filter(library__pk=library.pk)
        self.fields['library'].queryset = DlpLibrary.objects.filter(id=library.pk)


class AnalysisLibrarySelection(Form):
    library = ModelChoiceField(queryset=DlpLibrary.objects.all().order_by('pool_id'))


class ReferenceGenomeSelection(Form):
    ref_genome = ModelChoiceField(queryset=ReferenceGenome.objects.all())

