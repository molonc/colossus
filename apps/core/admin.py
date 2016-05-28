"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib import admin
from .models import Sample, Patient, Xenograft, CellLine
from .models import Library, SublibraryInformation, LibrarySampleDetail
from .models import LibraryConstructionInformation, LibraryQuantificationAndStorage

class SublibraryInformationInline(admin.TabularInline):
    model = SublibraryInformation
    extra = 3

class LibrarySampleDetailInline(admin.StackedInline):
    model = LibrarySampleDetail

class LibraryConstructionInformationInline(admin.StackedInline):
    model = LibraryConstructionInformation

class LibraryQuantificationAndStorageInline(admin.StackedInline):
    model = LibraryQuantificationAndStorage

class LibraryAdmin(admin.ModelAdmin):
    fieldsets = [
      (
        '',
        {'fields': [
          "sample_id",
          "pool_id",
          "jira_ticket",
          "description",
        ]
        }
      ),
    ]
    inlines = [
      SublibraryInformationInline,
      LibrarySampleDetailInline,
      LibraryConstructionInformationInline,
      LibraryQuantificationAndStorageInline
      ]
    list_display = ['sample_id', 'pool_id', 'jira_ticket']
    list_filter = ['jira_ticket']
    search_fields = ['sample_id', 'pool_id']


class SampleAdmin(admin.ModelAdmin):
    # fieldsets = [
    #   ('', {
    #     'fields': [
    #       'sample_id',
    #     ]        
    #     }
    #   ),
    #   ('Additional Sample Information', 
    #     {'fields':[
    #       'sex',
    #       # 'pool_id',
    #       # 'jira_ticket'

    #       ]
    #     }
    #   ),
    #  ]

    list_display = ['sample_id']
    list_filter = ['sample_type']
    search_fields = ['sample_id']


admin.site.register(Library, LibraryAdmin)
admin.site.register(Patient)
admin.site.register(Xenograft)
admin.site.register(CellLine)
admin.site.register(Sample, SampleAdmin)