"""
Created on July 6, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from django.contrib import admin
from .models import DlpAnalysisVersion, DlpAnalysisInformation, AnalysisRun, ReferenceGenome

admin.site.register(DlpAnalysisVersion)
admin.site.register(DlpAnalysisInformation)
admin.site.register(AnalysisRun)
admin.site.register(ReferenceGenome)
