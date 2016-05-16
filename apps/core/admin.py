"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.contrib import admin
from .models import Sample

class SampleAdmin(admin.ModelAdmin):
    fieldsets = [
                 ('Sample Information', {'fields':['sample_id',
                                                   'pool_id',
                                                   'jira_ticket',
                                                   'tube_label']}),
                 ('Date Information', {'fields': ['create_date'],
                                        'classes': ['collapse']}),
                 ]
    
    list_display = ['sample_id', 'pool_id', 'jira_ticket']
    list_filter = ['create_date']
    search_fields = ['sample_id']
    
admin.site.register(Sample, SampleAdmin)