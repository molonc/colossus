"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib import admin
from .models import Sample, Patient, Xenograft, CellLine, Library, Cell

# class PatientInline(admin.StackedInline):
#     model = Patient
#     extra = 0

# class LibraryInline(admin.StackedInline):
#     model = Library
#     extra = 0
    
# class AnalyteInline(admin.StackedInline):
#     model = Analyte
#     extra = 0

class CellInline(admin.TabularInline):
    model = Cell
    extra = 5

# class SequencingInfoInline(admin.StackedInline):
#     model = SequencingInfo
#     extra = 0

class LibraryAdmin(admin.ModelAdmin):
        inlines = [
                   CellInline,
                   # LibraryInline,
                   # AnalyteInline,
                   # SequencingInfoInline,
                   ]
    

# class SampleAdmin(admin.ModelAdmin):
# #     fieldsets = [
# #                  ('Sample Information (required)', {'fields':['sample_id',
# #                                                               'pool_id',
# #                                                               'jira_ticket',
# #                                                               ]
# #                                                     }
# #                   ),
# #                  ]
    
#     list_display = ['sample_id', 'pool_id', 'jira_ticket']
#     list_filter = ['jira_ticket']
#     search_fields = ['sample_id']


class SampleAdmin(admin.ModelAdmin):
    list_display = ['sample_id']  

admin.site.register(Library, LibraryAdmin)
admin.site.register(Patient)
admin.site.register(Xenograft)
admin.site.register(CellLine)
admin.site.register(Sample, SampleAdmin)