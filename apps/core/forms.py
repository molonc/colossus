"""
Created on May 24, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from .models import Sample
from django.forms import ModelForm

class SampleForm(ModelForm):
    class Meta:
        model = Sample
        # fields = [
        # 'sample_id',
        # 'pool_id',
        # 'jira_ticket',
        # 'tube_label',
        # 'patient',
        # 'collect_date',
        # 'description',
        # ]
        fields = "__all__"
        # widgets = {
        #     'collect_date': DateWidget(attrs = {'id':'id_dateTimeField'}, bootstrap_version=3, usel10n=True)
        #     }
