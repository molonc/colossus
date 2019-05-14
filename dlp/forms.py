import os

from django.forms import (
    inlineformset_factory,
    forms
)
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from core.forms import (
    LibraryForm,
    LibraryQuantificationAndStorageForm,
    SaveDefault,
    SequencingForm,
    LaneForm
)
from .models import *

class DlpLibraryForm(LibraryForm):
    field_order = [
        'sample',
        'description',
        'result',
        'pool_id',
        'title',
        'quality',
        'relates_to_dlp',
        'relates_to_tenx',
        'projects',
    ]

    def __init__(self,*args, **kwargs):
        super(DlpLibraryForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            # Get Jira info
            self.fields['create_jira_ticket'] = forms.BooleanField(initial=True, required=False)
            self.fields['additional_title'] = forms.CharField(max_length=100, required=False)
            self.fields['jira_user'] = forms.CharField(max_length=100, required=False)
            self.fields['jira_password'] = forms.CharField(widget=forms.PasswordInput, required=False)

            # Remove the field which allows explicitly setting the Jira
            # ticket ID (since it's done automatically)
            self.fields.pop('jira_ticket')
        else:
            uneditable_fields = ['pool_id']
            for field in uneditable_fields:
                    self.fields[field].widget.attrs['readonly'] = 'true'

    class Meta:
        model = DlpLibrary
        exclude = ['num_sublibraries']

        labels = {
            'primary sample': ('*Sample'),
            'pool_id': ('*Chip ID'),
            'additional_title': ('*Additional Title')
        }
        help_texts = {
            'sample': ('Sequencing ID (usually SA ID) of the sample composing the majority of the library.'),
            'pool_id': ('Chip ID.'),
        }

    def clean(self):
        # if it's a new instance, the pool_id should not exist.
        cleaned_data = super(DlpLibraryForm, self).clean()
        if not self.instance.pk:
            pool_id = cleaned_data.get("pool_id")
            if len(DlpLibrary.objects.filter(pool_id=pool_id)):
                msg = "Chip ID already exists."
                self.add_error('pool_id', msg)
        create_jira_ticket = cleaned_data.get('create_jira_ticket')
        jira_info = cleaned_data.get('additional_title')
        if create_jira_ticket and not jira_info:
            msg = "Additional title required"
            self.add_error('additional_title', msg)
        return cleaned_data

class DlpLibraryQuantificationAndStorageForm(LibraryQuantificationAndStorageForm):

    """
    Clean uploaded DLP-related files.
    """

    class Meta(LibraryQuantificationAndStorageForm.Meta):
        model = DlpLibraryQuantificationAndStorage

    def clean(self):
        """if Freezer specified, so should Rack, Shelf, Box, Position in box."""
        cleaned_data = super(DlpLibraryQuantificationAndStorageForm, self).clean()
        freezer = cleaned_data.get('freezer')
        if freezer:
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

DlpLibrarySampleDetailInlineFormset = inlineformset_factory(
    DlpLibrary,
    DlpLibrarySampleDetail,
    form = SaveDefault,
    can_delete = False,
    fields = "__all__",
    widgets = {
        'sample_spot_date': SelectDateWidget(
            years=range(2000,2020),
            empty_label=('year', 'month', 'day'),
        )
    }
)

DlpLibraryConstructionInfoInlineFormset =  inlineformset_factory(
    DlpLibrary,
    DlpLibraryConstructionInformation,
    form = SaveDefault,
    can_delete = False,
    fields = "__all__",
    widgets = {
        'library_prep_date': SelectDateWidget(
            years=range(2000,2020),
            empty_label=('year', 'month', 'day'),
        )
    }
)

DlpLibraryQuantificationAndStorageInlineFormset =  inlineformset_factory(
    DlpLibrary,
    DlpLibraryQuantificationAndStorage,
    form = DlpLibraryQuantificationAndStorageForm,
    can_delete = False,
    fields = "__all__",
    help_texts = {
        'agilent_bioanalyzer_xad': ('Select a xad file to upload.'),
        'agilent_bioanalyzer_png': ('Supported formats: png, jpg, jpeg, bmp.'),
    }
)


class DlpSequencingForm(SequencingForm):

    def __init__(self,*args,**kwargs):
        super(DlpSequencingForm,self).__init__(*args,**kwargs)
        if not self.instance.pk:
            self.fields['jira_user'] = forms.CharField(max_length=100)
            self.fields['jira_password'] = forms.CharField(widget=forms.PasswordInput)
        else:
            self.fields['jira_user'] = forms.CharField(max_length=100, required=False)
            self.fields['jira_password'] = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta(SequencingForm.Meta):
        model = DlpSequencing

class DlpLaneForm(LaneForm):
    class Meta(LaneForm.Meta):
        model = DlpLane

