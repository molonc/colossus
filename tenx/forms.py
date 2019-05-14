from django.forms import (
    ModelForm,
    inlineformset_factory,
    forms)
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from core.forms import LibraryForm, LibraryQuantificationAndStorageForm, SaveDefault, SequencingForm, LaneForm
from .models import *


class TenxChipForm(ModelForm):
    class Meta:
        model = TenxChip
        fields = "__all__"


class TenxPoolForm(ModelForm):
    class Meta:
        model = TenxPool
        exclude = ['pool_name']
        fields = "__all__"
        widgets = {
            'constructed_date': SelectDateWidget(
                years=range(2000, 2020),
                empty_label=('year', 'month', 'day'),
            )
        }

class TenxLibraryForm(LibraryForm):
    field_order = [
        'chips',
        'sample',
        'description',
        'result',
        'num_sublibraries',
        'relates_to_dlp',
        'relates_to_tenx',
        'projects',
        'jira_ticket',
    ]

    def __init__(self,*args, **kwargs):
        super(TenxLibraryForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            # Get Jira info
            self.fields['create_jira_ticket'] = forms.BooleanField(initial=True, required=False)
            self.fields['additional_title'] = forms.CharField(max_length=100, required=False)
            self.fields['jira_user'] = forms.CharField(max_length=100, required=False)
            self.fields['jira_password'] = forms.CharField(widget=forms.PasswordInput, required=False)

            # Remove the field which allows explicitly setting the Jira
            # ticket ID (since it's done automatically)
            self.fields.pop('jira_ticket')

    class Meta:
        model = TenxLibrary
        fields = '__all__'
        labels = {
            'primary sample': ('*Sample'),
        }
        help_texts = {
            'sample': ('Sequencing ID (usually SA ID) of the sample composing the majority of the library.'),
        }

    def clean(self):
        cleaned_data = super(TenxLibraryForm, self).clean()
        create_jira_ticket = cleaned_data.get('create_jira_ticket')
        jira_info = cleaned_data.get('additional_title')
        if create_jira_ticket and not jira_info:
            msg = "Additional title required"
            self.add_error('additional_title', msg)
        return cleaned_data

class TenxLibraryQuantificationAndStorageForm(LibraryQuantificationAndStorageForm):

    """
    Clean uploaded 10x-related files.
    """

    class Meta(LibraryQuantificationAndStorageForm.Meta):
        model = TenxLibraryQuantificationAndStorage

TenxLibrarySampleDetailInlineFormset = inlineformset_factory(
    TenxLibrary,
    TenxLibrarySampleDetail,
    form = SaveDefault,
    can_delete = False,
    fields = "__all__",
    widgets = {
        'sample_prep_date': SelectDateWidget(
            years=range(2000,2020),
            empty_label=('year', 'month', 'day'),
        )
    }
)

TenxLibraryConstructionInfoInlineFormset =  inlineformset_factory(
    TenxLibrary,
    TenxLibraryConstructionInformation,
    form = SaveDefault,
    can_delete = False,
    fields = "__all__",
    widgets = {
        'submission_date': SelectDateWidget(
            years=range(2000,2020),
            empty_label=('year', 'month', 'day'),
        )
    }
)

TenxLibraryQuantificationAndStorageInlineFormset =  inlineformset_factory(
    TenxLibrary,
    TenxLibraryQuantificationAndStorage,
    can_delete = False,
    form = TenxLibraryQuantificationAndStorageForm,
    fields = "__all__",
)


class TenxSequencingForm(SequencingForm):

    def __init__(self, *args, **kwargs):
        super(TenxSequencingForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['jira_user'] = forms.CharField(max_length=100)
            self.fields['jira_password'] = forms.CharField(widget=forms.PasswordInput)
        else:
            self.fields['jira_user'] = forms.CharField(max_length=100, required=False)
            self.fields['jira_password'] = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta(SequencingForm.Meta):
        model = TenxSequencing
        labels = {
            'tenx_pool': ('*TENX POOL'),
        }


class TenxLaneForm(ModelForm):
    class Meta(LaneForm.Meta):
        fields = "__all__"
        model = TenxLane

