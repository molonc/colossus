"""
Created on July 6, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from django.contrib import admin
from .models import AnalysisVersion, AnalysisRun, AnalysisInformation

admin.site.register(AnalysisVersion)
admin.site.register(AnalysisRun)
admin.site.register(AnalysisInformation)
