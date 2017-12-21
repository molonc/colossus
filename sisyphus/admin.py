"""
Created on July 6, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from django.contrib import admin
from .models import AnalysisVersion, AnalysisInformation, AnalysisRun, ReferenceGenome

admin.site.register(AnalysisVersion)
admin.site.register(AnalysisInformation)
admin.site.register(AnalysisRun)
admin.site.register(ReferenceGenome)
