"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib import admin
from .models import Sample, Patient, Library, CellTable
from .models import Cell, Analyte, SequencingInfo

class PatientInline(admin.StackedInline):
    model = Patient
    extra = 0

class LibraryInline(admin.StackedInline):
    model = Library
    extra = 0
    
class AnalyteInline(admin.StackedInline):
    model = Analyte
    extra = 0

class CellInline(admin.TabularInline):
    model = Cell
    extra = 5

class SequencingInfoInline(admin.StackedInline):
    model = SequencingInfo
    extra = 0

class CellTableAdmin(admin.ModelAdmin):
        inlines = [
#                    PatientInline,
                   CellInline,
                   LibraryInline,
                   AnalyteInline,
                   SequencingInfoInline,
                   ]
    

class SampleAdmin(admin.ModelAdmin):
#     fieldsets = [
#                  ('Sample Information (required)', {'fields':['sample_id',
#                                                               'pool_id',
#                                                               'jira_ticket',
#                                                               ]
#                                                     }
#                   ),
#                  ]
    
    list_display = ['sample_id', 'pool_id', 'jira_ticket']
    list_filter = ['jira_ticket']
    search_fields = ['sample_id']

    
# admin.site.register(Patient)
admin.site.register(Patient)
admin.site.register(CellTable, CellTableAdmin)
admin.site.register(Sample, SampleAdmin)