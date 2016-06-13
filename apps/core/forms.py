"""
Created on May 24, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

#===========================
# Django imports
#---------------------------
from django.forms import ModelForm, Form, FileField
from django.forms import inlineformset_factory

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
    # exclude = ['delete'],
    fields = "__all__",
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
            'pool_id': ('Pool ID.'),
            'jira_ticket': ('Jira Ticket.'),
            }
        labels = {
            'sample': ('*Sample'),
            'pool_id': ('*Pool ID'),
            'jira_ticket': ('*Jira Ticket'),
            }

    def clean(self):
        ## if it's a new instance, the pool_id should not exist.
        if not self.instance.pk:
            cleaned_data = super(LibraryForm, self).clean()
            pool_id = cleaned_data.get("pool_id")
            if len(Library.objects.filter(pool_id=pool_id)):
                msg = "Pool ID already exists."
                self.add_error('pool_id', msg)


class SublibraryForm(Form):
    ## File field
    smartchipapp_file = FileField(label="File")

# SublibraryInfoInlineFormset =  inlineformset_factory(
#     Library,
#     SublibraryInformation,
#     # exclude = ['delete'],
#     fields = "__all__"
#         )

LibrarySampleDetailInlineFormset = inlineformset_factory(
    Library,
    LibrarySampleDetail,
    # exclude = ['delete'],
    fields = "__all__"
    )

LibraryConstructionInfoInlineFormset =  inlineformset_factory(
    Library,
    LibraryConstructionInformation,
    # exclude = ['delete'],
    fields = "__all__"
        )

LibraryQuantificationAndStorageInlineFormset =  inlineformset_factory(
    Library,
    LibraryQuantificationAndStorage,
    # exclude = ['delete'],
    fields = "__all__"
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

SequencingDetailInlineFormset = inlineformset_factory(
    Sequencing,
    SequencingDetail,
    # exclude = ['delete'],
    fields = "__all__"
    )
