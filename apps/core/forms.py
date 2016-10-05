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
from django.forms.extras.widgets import SelectDateWidget

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
        widgets = {
        'xenograft_biopsy_date': SelectDateWidget(
            years=range(2000, 2020),
            empty_label=('year', 'month', 'day')
            )
        }
        labels = {
            'sample_id': ('*Sample ID'),
        }
        help_texts = {
            'sample_id': ('Sequencing ID (usually SA ID).'),
            'anonymous_patient_id': ('Original/clinical patient ID.'),
            # 'xenograft_biopsy_date': ('yyyy-mm-dd.')
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
    # exclude = ['delete'],
    fields = "__all__",
    widgets = {
    'patient_biopsy_date': SelectDateWidget(
        years=range(2000, 2020),
        empty_label=('year', 'month', 'day')
        )
    }
    # can_delete = True,
    # help_texts = {
    #     'patient_biopsy_date': ('yyyy-mm-dd.')
    # },
    )


#===========================
# Library forms
#---------------------------
class LibraryForm(ModelForm):
    class Meta:
        model = Library
        fields = "__all__"
        # exclude = ['projects']
        labels = {
            'sample': ('*Sample'),
            'pool_id': ('*Chip ID'),
            'jira_ticket': ('*Jira Ticket'),
            }
        help_texts = {
            'sample': ('Sequencing ID (usually SA ID).'),
            'pool_id': ('Chip ID.'),
            'jira_ticket': ('Jira Ticket.'),
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
            if ext.lower() != '.png':
                msg = "file not supported with extension: %s" % ext
                self.add_error('agilent_bioanalyzer_png', msg)
        return file

LibrarySampleDetailInlineFormset = inlineformset_factory(
    Library,
    LibrarySampleDetail,
    fields = "__all__",
    widgets = {
    'sample_spot_date': SelectDateWidget(
        years=range(2000,2020),
        empty_label=('year', 'month', 'day')
        )
    }
    # help_texts = {
    #     'sample_spot_date': ('yyyy-mm-dd.')
    # }
    )

LibraryConstructionInfoInlineFormset =  inlineformset_factory(
    Library,
    LibraryConstructionInformation,
    fields = "__all__",
    widgets = {
    'library_prep_date': SelectDateWidget(
        years=range(2000,2020),
        empty_label=('year', 'month', 'day')
        )
    }
    # help_texts = {
    #     'library_prep_date': ('yyyy-mm-dd.'),
    # }
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
        widgets = {
            'submission_date': SelectDateWidget(
                years=range(2000,2020),
                empty_label=('year', 'month', 'day')
                )
        }
        labels = {
            'library': ('*Library'),
            }
        help_texts = {
            'library': ('Select a library.'),
            # 'submission_date': ('yyyy-mm-dd.')
            }

SequencingDetailInlineFormset = inlineformset_factory(
    Sequencing,
    SequencingDetail,
    fields = "__all__"
    )
