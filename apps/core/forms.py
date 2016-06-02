"""
Created on May 24, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from .models import Sample, AdditionalSampleInformation
from .models import Library, SublibraryInformation, LibraryConstructionInformation
from .models import Sequencing
from django.forms import ModelForm
from django.forms import inlineformset_factory


#===========================
# Sample forms
#---------------------------
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


AdditionalInfoInlineFormset =  inlineformset_factory(
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
		# exclude = ['sample']

class SequencingForm(ModelForm):
	class Meta:
		model = Sequencing
		# fields = "__all__"
		exclude = ['pool_id']

# InlineFormset =  inlineformset_factory(
#     Library,
#     [
#         SublibraryInformation,
#         LibraryConstructionInformation
#     ],
#     # exclude = ['delete']
#     fields = "__all__"
#         )
