"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib import admin

from .models import Sample, AdditionalSampleInformation
from .models import DlpLibrary, SublibraryInformation, DlpLibrarySampleDetail
from .models import DlpLibraryConstructionInformation
from .models import DlpLibraryQuantificationAndStorage
from .models import DlpSequencing
from .models import TenxLibrary, TenxCondition, TenxLibrarySampleDetail
from .models import TenxLibraryConstructionInformation
from .models import TenxLibraryQuantificationAndStorage
from .models import ChipRegion, ChipRegionMetadata
from .models import MetadataField

# third-party apps
from simple_history.admin import SimpleHistoryAdmin
from taggit.models import Tag
from taggit.admin import TagAdmin


# Sample information
class AdditionalSampleInformationInline(admin.StackedInline):
    model = AdditionalSampleInformation

class SampleAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    inlines = [AdditionalSampleInformationInline]
    list_display = ['sample_id', 'sample_type']
    list_filter = ['sample_type']
    search_fields = ['sample_id']


# Library information
class SublibraryInformationInline(admin.TabularInline):
    model = SublibraryInformation
    extra = 3

class DlpLibrarySampleDetailInline(admin.StackedInline):
    model = DlpLibrarySampleDetail

class DlpLibraryConstructionInformationInline(admin.StackedInline):
    model = DlpLibraryConstructionInformation

class DlpLibraryQuantificationAndStorageInline(admin.StackedInline):
    model = DlpLibraryQuantificationAndStorage

class DlpLibraryAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    fieldsets = [
      (
        '',
        {'fields': [
          "sample",
          "pool_id",
          "jira_ticket",
          "description",
          "num_sublibraries",
          "projects"
        ]
        }
      ),
    ]
    inlines = [
      SublibraryInformationInline,
      DlpLibrarySampleDetailInline,
      DlpLibraryConstructionInformationInline,
      DlpLibraryQuantificationAndStorageInline
      ]
    list_display = ['sample', 'pool_id', 'jira_ticket']
    list_filter = ['jira_ticket']
    search_fields = ['pool_id']

class TenxLibrarySampleDetailInline(admin.StackedInline):
    model = TenxLibrarySampleDetail

class TenxLibraryConstructionInformationInline(admin.StackedInline):
    model = TenxLibraryConstructionInformation

class TenxLibraryQuantificationAndStorageInline(admin.StackedInline):
    model = TenxLibraryQuantificationAndStorage

class TenxLibraryConditionsInline(admin.StackedInline):
    model = TenxCondition

class TenxLibraryAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    fieldsets = [
      (
        '',
        {'fields': [
          "sample",
          "jira_ticket",
          "description",
          "projects"
        ]
        }
      ),
    ]
    inlines = [
      TenxLibrarySampleDetailInline,
      TenxLibraryConstructionInformationInline,
      TenxLibraryQuantificationAndStorageInline,
      TenxLibraryConditionsInline,
      ]
    list_display = ['id', 'sample',  'jira_ticket']
    list_filter = ['jira_ticket']


class DlpSequencingAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
  pass



# Tag information (Project information)
class CustomTagAdmin(SimpleHistoryAdmin, TagAdmin):
    list_display = ['name', 'slug']


admin.site.register(Sample, SampleAdmin)
admin.site.register(DlpLibrary, DlpLibraryAdmin)
admin.site.register(TenxLibrary, TenxLibraryAdmin)
admin.site.register(DlpSequencing, DlpSequencingAdmin)

# extra admin only information
admin.site.register(AdditionalSampleInformation)
admin.site.register(SublibraryInformation)
admin.site.register(DlpLibrarySampleDetail)
admin.site.register(DlpLibraryConstructionInformation)
admin.site.register(DlpLibraryQuantificationAndStorage)
admin.site.register(ChipRegion)
admin.site.register(ChipRegionMetadata)
admin.site.register(MetadataField)

# register Taggit
admin.site.unregister(Tag)
admin.site.register(Tag, CustomTagAdmin)
