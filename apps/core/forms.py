"""
Created on May 24, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os

#===========================
# Django imports
#---------------------------
from django.forms import (
    ModelForm,
    Form,
    FileField,
    ValidationError,
    inlineformset_factory,
    BaseInlineFormSet
    )

#===========================
# App imports
#---------------------------
from .models import (
    Sample,
    AdditionalSampleInformation,
    Library,
    SublibraryInformation,
    LibrarySampleDetail,
    LibraryConstructionInformation,
    LibraryQuantificationAndStorage,
    Sequencing,
    SequencingDetail
    )
from .utils import parse_smartchipapp_file

#===========================
# 3rd-party app imports
#---------------------------
from taggit.models import Tag


#===========================
# Sample forms
#---------------------------
class SampleForm(ModelForm):
    class Meta:
        model = Sample
        fields = "__all__"
        # widgets = {
        #     'collect_date': DateWidget(
        #         attrs = {'id':'id_dateTimeField'},
        #         bootstrap_version=3,
        #         usel10n=True
        #         )
        #     }
        help_texts = {
            'sample_id': ('Sequencing ID (usually SA ID).'),
            'anonymous_patient_id': ('Original/clinical patient ID.'),
            'xenograft_biopsy_date': ('yyyy-mm-dd.')
            }
        labels = {
            'sample_id': ('*Sample ID'),
        }

    def clean(self):
        ## if it's a new instance, the sample_id should not exist.
        if not self.instance.pk:
            cleaned_data = super(SampleForm, self).clean()
            sample_id = cleaned_data.get("sample_id")
            if len(Sample.objects.filter(sample_id=sample_id)):
                msg = "Sample ID already exists."
                self.add_error('sample_id', msg)

AdditionalSampleInfoInlineFormset =  inlineformset_factory(
    Sample,
    AdditionalSampleInformation,
    fields = "__all__",
    help_texts = {
        'patient_biopsy_date': ('yyyy-mm-dd.')
    }
    # can_delete = True,
    )


#===========================
# Library forms
#---------------------------
class LibraryForm(ModelForm):
    class Meta:
        model = Library
        fields = "__all__"
        # exclude = ['projects']
        help_texts = {
            'sample': ('Sequencing ID (usually SA ID).'),
            'pool_id': ('Chip ID.'),
            'jira_ticket': ('Jira Ticket.'),
            }
        labels = {
            'sample': ('*Sample'),
            'pool_id': ('*Chip ID'),
            'jira_ticket': ('*Jira Ticket'),
            }

    def clean(self):
        ## if it's a new instance, the pool_id should not exist.
        if not self.instance.pk:
            cleaned_data = super(LibraryForm, self).clean()
            pool_id = cleaned_data.get("pool_id")
            if len(Library.objects.filter(pool_id=pool_id)):
                msg = "Chip ID already exists."
                self.add_error('pool_id', msg)

class SublibraryForm(Form):
    ## File field
    smartchipapp_file = FileField(
        label="File",
        required=False,
        )

    def clean_smartchipapp_file(self):
        file = self.cleaned_data['smartchipapp_file']
        if file:
            try:
                df = parse_smartchipapp_file(file)
                self.cleaned_data['smartchipapp_df'] = df
            except:
                msg = "failed to parse the file."
                self.add_error('smartchipapp_file', msg)

class LibraryQuantificationAndStorageForm(ModelForm):

    """
    Clean uploaded files.
    """

    class Meta:
        model = LibraryQuantificationAndStorage
        fields = "__all__"
        # exclude = ['library']

    def clean_agilent_bioanalyzer_xad(self):
        """check if it's a right filetype."""
        file = self.cleaned_data['agilent_bioanalyzer_xad']
        if file:
            _, ext = os.path.splitext(file.name)
            if ext != '.xad':
                msg = "file not supported with extension: %s" % ext
                self.add_error('agilent_bioanalyzer_xad', msg)
        return file

    def clean_agilent_bioanalyzer_png(self):
        """check if it's a right filetype."""
        file = self.cleaned_data['agilent_bioanalyzer_png']
        if file:
            _, ext = os.path.splitext(file.name)
            if ext != '.png':
                msg = "file not supported with extension: %s" % ext
                self.add_error('agilent_bioanalyzer_png', msg)
        return file

LibrarySampleDetailInlineFormset = inlineformset_factory(
    Library,
    LibrarySampleDetail,
    fields = "__all__",
    help_texts = {
        'sample_spot_date': ('yyyy-mm-dd.')
    }
    )

LibraryConstructionInfoInlineFormset =  inlineformset_factory(
    Library,
    LibraryConstructionInformation,
    fields = "__all__",
    help_texts = {
        'library_prep_date': ('yyyy-mm-dd.'),
    }
    )

LibraryQuantificationAndStorageInlineFormset =  inlineformset_factory(
    Library,
    LibraryQuantificationAndStorage,
    form = LibraryQuantificationAndStorageForm,
    fields = "__all__",
    help_texts = {
        'agilent_bioanalyzer_xad': ('Select a .xad file to upload.'),
        'agilent_bioanalyzer_png': ('Select a .png file to upload.'),
    }
    )


#===========================
# Sequencing forms
#---------------------------
class ProjectForm(ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


#===========================
# Sequencing forms
#---------------------------
class SequencingForm(ModelForm):
    class Meta:
        model = Sequencing
        # fields = "__all__"
        exclude = ['pool_id']
        help_texts = {
            'library': ('Select a library.'),
            'submission_date': ('yyyy-mm-dd.')
            }
        labels = {
            'library': ('*Library'),
            }

SequencingDetailInlineFormset = inlineformset_factory(
    Sequencing,
    SequencingDetail,
    fields = "__all__"
    )
