"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib import admin
from .models import Sample, Patient

class PatientInline(admin.StackedInline):
    model = Patient
    extra = 0
    
class SampleAdmin(admin.ModelAdmin):
    fieldsets = [
                 ('Sample Information (required)', {'fields':['sample_id',
                                                              'pool_id',
                                                              'jira_ticket',
                                                              ]}),
                 ('More Sample Information', {'fields': ['tube_label',
                                                         'num_libraries',
                                                         'num_cells',
                                                         'collect_date',
                                                         'description'],
                                        'classes': ['collapse']}),
                 ]
    
    list_display = ['sample_id', 'pool_id', 'jira_ticket']
    list_filter = ['jira_ticket']
    search_fields = ['sample_id']
    inlines = [PatientInline]
    
# admin.site.register(Patient)
admin.site.register(Sample, SampleAdmin)