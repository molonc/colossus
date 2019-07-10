"""
Created on May 24, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated Nov 27, 2017 by Spencer Vatrt-Watts (github.com/Spenca)
"""

import os

#===========================
# Django imports
#---------------------------
import datetime
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
    BaseInlineFormSet,
    forms)
from django import forms
from django.forms.extras.widgets import SelectDateWidget


#===========================
# App imports
#---------------------------

from .models import (
    Sample,
    AdditionalSampleInformation,
    JiraUser,
    Project)
from .utils import parse_smartchipapp_results_file
from .utils import generate_doublet_info
from .jira_templates.jira_wrapper import *
from jira import JIRA, JIRAError
from colossus.settings import JIRA_URL

#===========================
# 3rd-party app imports
#---------------------------



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

    def clean(self):
        cleaned_data = super(SaveDefault, self).clean()
        disease_condition_health_status = cleaned_data.get("disease_condition_health_status")
        pathology_disease_name = cleaned_data.get("pathology_disease_name")
        tissue_type = cleaned_data.get("tissue_type")

        if disease_condition_health_status and not pathology_disease_name:
            msg = "This field is required for diseased samples"
            self.add_error('pathology_disease_name', msg)

        # Only trigger this on the Sample form!
        if (self.__class__.__name__ == 'AdditionalSampleInformationForm'
                and tissue_type != 'N'
                and not pathology_disease_name):
            msg = "This field is required for diseased samples"
            self.add_error('pathology_disease_name', msg)


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
                empty_label=('year', 'month', 'day'),
            )
        }
        labels = {
            'sample_id': ('*Sample ID'),
        }
        help_texts = {
            'sample_id': ('Sequencing ID (usually SA ID).'),
            'anonymous_patient_id': ('Original/clinical patient ID.'),
        }

    def clean(self):
        # if it's a new instance, the sample_id should not exist.
        if not self.instance.pk:
            cleaned_data = super(SampleForm, self).clean()
            sample_id = cleaned_data.get("sample_id")
            if len(Sample.objects.filter(sample_id=sample_id)):
                msg = "Sample ID already exists."
                self.add_error('sample_id', msg)

    def __init__(self, *args, **kwargs):
        super(SampleForm, self).__init__(*args, **kwargs)
        uneditable_fields = ['sample_id']
        if self.instance.pk:
            for field in uneditable_fields:
                self.fields[field].widget.attrs['readonly'] = 'true'

AdditionalSampleInfoInlineFormset =  inlineformset_factory(
    Sample,
    AdditionalSampleInformation,
    form = SaveDefault,
    can_delete = False,
    fields = "__all__",
    widgets = {
        'patient_biopsy_date': SelectDateWidget(
            years=range(2000, 2020),
            empty_label=('year', 'month', 'day'),
        )
    },
    labels = {
        'tissue_type':('*Tissue type'),
        'anatomic_site':('*Anatomic site'),
        'pathology_disease_name': ('*Pathology/disease name (for diseased samples only)')
    },
)


def get_user_list():
    #Default empty choice for user_list
    user_list = []
    for user in JiraUser.objects.all().order_by('name'):
        user_list.append((user.username, user.name))
    return user_list


'''
JIRA Ticket Creation Confirmation Form For Library Creation
'''
class JiraConfirmationForm(Form):
    title = forms.CharField(max_length=1000)
    description = forms.CharField(widget=forms.Textarea)
    project = forms.ChoiceField()
    reporter = forms.ChoiceField(choices=get_user_list)




#===========================
# Library forms
#---------------------------
class LibraryForm(ModelForm):
    class Meta:
        abstract = True

class SublibraryForm(Form):
    # SmartChipApp results file
    smartchipapp_results_file = FileField(
        label="SmartChipApp results:",
        required=False,
    )

    def clean_smartchipapp_results_file(self):
        filename = self.cleaned_data['smartchipapp_results_file']
        if filename:
            try:
                results, region_metadata = parse_smartchipapp_results_file(filename)
                doublet_info = generate_doublet_info(filename)
                self.cleaned_data['smartchipapp_results'] = results
                self.cleaned_data['smartchipapp_region_metadata'] = region_metadata
                self.cleaned_data['smartchipapp_doublet_info'] = doublet_info
            except ValueError as e:
                self.add_error('smartchipapp_results_file', ' '.join(e.args))
            except Exception as e:
                self.add_error('smartchipapp_results_file', 'failed to parse the file.')


class DoubletInfoForm(Form):
    # SmartChipApp results file
    smartchipapp_summary_file = FileField(
        label="SmartChipApp summary:",
        required=False,
    )

    def clean_smartchipapp_summary_file(self):
        filename = self.cleaned_data['smartchipapp_summary_file']
        if filename:
            try:
                results = generate_doublet_info(filename)
                self.cleaned_data['smartchipapp_summary'] = results
            except ValueError as e:
                self.add_error('smartchipapp_summary_file', ' '.join(e.args))
            except Exception as e:
                self.add_error('smartchipapp_summary_file', 'failed to parse the file.')


class LibraryQuantificationAndStorageForm(ModelForm):

    """
    Base class for cleaning uploaded files.
    """

    class Meta:
        abstract = True
        fields = "__all__"

    def has_changed(self):
        """ Should returns True if data differs from initial.
        By always returning true even unchanged inlines will
        get validated and saved."""
        return True


#===========================
# Project forms
#---------------------------
class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']

class AddWatchersForm(Form):
    watchers = forms.MultipleChoiceField(choices=get_user_list, widget=forms.CheckboxSelectMultiple())
    comment = forms.CharField(widget=forms.Textarea(attrs={'style': 'height: 80px;'}))


#===========================
# Sequencing forms
#---------------------------
class SequencingForm(ModelForm):

    class Meta:
        abstract = True
        exclude = ['pool_id', 'lane_requested_date']
        widgets = {
            'submission_date': SelectDateWidget(
                years=range(2000,2020),
                empty_label=('year', 'month', 'day'),
            )
        }
        labels = {
            'library': ('*Library'),
        }

#===========================
# Lane forms
#---------------------------
class LaneForm(ModelForm):
    class Meta:
        abstract = True
        fields = "__all__"

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
        initial="Andy Mungall, Room 508",
    )
    org = CharField(
        label="Organization",
        max_length=100,
        initial="Biospecimen Core",
    )
    org_gsc = CharField(
        label="GSC",
        max_length=100,
        initial="Genome Sciences Centre",
    )
    org_bcca = CharField(
        label="BC Cancer Agency",
        max_length=100,
        initial="BC Cancer Agency",
    )
    addr = CharField(
        label="Address",
        max_length=100,
        initial="Suite 100, 570 West 7th Avenue",
    )
    city = CharField(
        label="City",
        max_length=100,
        initial="Vancouver, BC  V5Z 4S6",
    )
    country = CharField(
        label="Country",
        max_length=100,
        initial="Canada",
    )
    email = EmailField(
        label="Email",
        initial="amungall@bcgsc.ca",
    )
    tel = CharField(
        label="Tel",
        max_length=100,
        initial="604-707-5900 ext 673251",
    )


class GSCFormSubmitterInfo(Form):

    """
    Delivery information section of GSC submission form.
    """

    # choices
    at_completion_choices = (
        ('R', 'Return unused sample'),
        ('D', 'Destroy unused sample'),
    )

    library_construction = (
        ('Nanowell Single Cell Genome', 'Nanowell Single Cell Genome'),
        ('Chromium Single Cell RNA', 'Chromium Single Cell RNA'),
        ('Chromium Genome','Chromium Genome'),
        ('Chromium Single Cell VDJ','Chromium Single Cell VDJ')
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
        initial= datetime.date.today
    )
    submitting_org = CharField(
        label="Submitting Organization",
        max_length=100,
        initial="BCCRC/ UBC",
    )
    pi_name = CharField(
        label="Name of Principal Investigator",
        max_length=100,
        initial="Sam Aparicio/ Carl Hansen",
    )
    pi_email = EmailField(
        label="Principal Investigator's email",
        initial="saparicio@bccrc.ca",
    )
    project_name = CharField(
        label="Project Name",
        max_length=100,
        initial="Single cell indexing",
    )
    sow = CharField(
        label="Statement of Work (SOW) #",
        max_length=100,
        initial="GSC-0297",
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
    bsgsc_standard = BooleanField(
        label='BC GSC Standard',
        required=False,
    )
    custom = BooleanField(
        label="Custom",
        required=False,
    )
    is_this_pbal_library = BooleanField(
        label="Is this pbal library",
        required=False,
    )
    is_this_chromium_library = BooleanField(
        label="Is this Chromium library",
        required=False,
    )

    library_method = ChoiceField(
        label="Library Construction Method",
        choices=library_construction,
    )

    at_completion = ChoiceField(
        label="At completion of project",
        choices=at_completion_choices,
        initial='R',
    )
