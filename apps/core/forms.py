"""
Created on May 24, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from .models import Sample, AdditionalSampleInformation
from django.forms import ModelForm


class SampleForm(ModelForm):
    class Meta:
        model = Sample
        fields = "__all__"
        # widgets = {
        #     'collect_date': DateWidget(attrs = {'id':'id_dateTimeField'}, bootstrap_version=3, usel10n=True)
        #     }
        help_texts = {
        'sample_id': ('Sequencing ID (usually SA ID).'),
        'anonymous_patient_id': ('Original/clinical patient ID.'),
        }
        labels = {
        'sample_id': ('*Sample ID'),
        }


class AdditionalSampleInformationForm(ModelForm):
	class Meta:
		model = AdditionalSampleInformation
		fields = "__all__"
		exclude = ['sample']
