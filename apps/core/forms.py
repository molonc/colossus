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
    CharField,
    FileField,
    EmailField,
    DateField,
    BooleanField,
    ChoiceField,
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
# Helpers
#---------------------------
class SaveDefault(ModelForm):

    """
    Save the default values all the time.
    """

    def has_changed(self):
        """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will
        get validated and saved."""
        return True

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
    form = SaveDefault,
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
        # fields = "__all__"
        exclude = ['num_sublibraries']
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

    def clean(self):
        """if Freezer specified, so should Rack,Shelf,Box,Positoin in box."""
        cleaned_data = super(LibraryQuantificationAndStorageForm, self).clean()
        freezer = cleaned_data.get('freezer')
        if freezer != '':
            if cleaned_data.get('rack') is None:
                msg = "Rack is required when specifying the Freezer."
                self.add_error('rack', msg)

            if cleaned_data.get('shelf') is None:
                msg = "Shelf is required when specifying the Freezer."
                self.add_error('shelf', msg)

            if cleaned_data.get('box') is None:
                msg = "Box is required when specifying the Freezer."
                self.add_error('box', msg)

            if cleaned_data.get('position_in_box') is None:
                msg = "Position in box is required when specifying the Freezer."
                self.add_error('position_in_box', msg)
        return cleaned_data

    def clean_agilent_bioanalyzer_xad(self):
        """check if it's a right filetype."""
        file = self.cleaned_data['agilent_bioanalyzer_xad']
        if file:
            _, ext = os.path.splitext(file.name)
            if ext != '.xad':
                msg = "file not supported with extension: %s" % ext
                self.add_error('agilent_bioanalyzer_xad', msg)
        return file

    def clean_agilent_bioanalyzer_image(self):
        """check if it's a right filetype."""
        file = self.cleaned_data['agilent_bioanalyzer_image']
        if file:
            _, ext = os.path.splitext(file.name)
            if ext.lower() not in ('.png', '.jpg', '.jpeg', '.bmp'):
                msg = "file not supported with extension: %s" % ext
                self.add_error('agilent_bioanalyzer_image', msg)
        return file

    def has_changed(self):
        """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will
        get validated and saved."""
        return True

LibrarySampleDetailInlineFormset = inlineformset_factory(
    Library,
    LibrarySampleDetail,
    form = SaveDefault,
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
    form = SaveDefault,
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
        'agilent_bioanalyzer_xad': ('Select a xad file to upload.'),
        'agilent_bioanalyzer_png': ('Supported formats: png, jpg, jpeg, bmp.'),
    }
    )


#===========================
# Project forms
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
    form = SaveDefault,
    fields = "__all__"
    )


#===========================
# GSC submission forms
#---------------------------
class GSCFormDeliveryInfo(Form):

    """
    Delivery information section of GSC submission form.
    """

    # fields
    name = CharField(
        label="Name",
        max_length=100,
        initial="Andy Mungall, Room 508"
        )
    org = CharField(
        label="Organization",
        max_length=100,
        initial="Biospecimen Core, Genome Sciences Centre, BC Cancer Agency"
        )
    addr = CharField(
        label="Address",
        max_length=100,
        initial="Suite 100, 570 West 7th Avenue, Vancouver, BC  V5Z 4S6, Canada"
        )
    email = EmailField(
        label="Email",
        initial="amungall@bcgsc.ca"
        )
    tel = CharField(
        label="Tel",
        max_length=100,
        initial="604-707-5900 ext 673251")

class GSCFormSubmitterInfo(Form):

    """
    Delivery information section of GSC submission form.
    """

    #choices
    at_completion_choices = (
        ('R', 'Return unused sample'),
        ('D', 'Destroy unused sample')
        )

    # fields
    submitter_name = CharField(
        label="Name of Submitter",
        max_length=100,
        )
    submitter_email = EmailField(
        label="Submitter's email",
        )
    submission_date = DateField(
        label="Submission Date",
        help_text = 'yyyy-mm-dd',
        # widget=SelectDateWidget
        )
    submitting_org = CharField(
        label="Submitting Organization",
        max_length=100,
        initial="BCCRC/ UBC"
        )
    pi_name = CharField(
        label="Name of Principal Investigator",
        max_length=100,
        initial="Sam Aparicio/ Carl Hansen"
        )
    pi_email = EmailField(
        label="Principal Investigator's email",
        initial="saparicio@bccrc.ca"
        )
    project_name = CharField(
        label="Project Name",
        max_length=100,
        initial="Single cell indexing"
        )
    sow = CharField(
        label="Statement of Work (SOW) #",
        max_length=100,
        initial="GSC-0297"
        )
    nextera_compatible = BooleanField(
        label="Nextera compatible",
        required=False,
        initial=True,
        )
    truseq_compatible = BooleanField(
        label="TruSeq compatible",
        required=False,
        )
    custom = BooleanField(
        label="Custom",
        required=False,
        )
    is_this_pbal_library = BooleanField(
        label="Is this PBAL library",
        required=False,
        )
    at_completion = ChoiceField(
        label="At completion of project",
        choices=at_completion_choices,
        initial='R'
        )

