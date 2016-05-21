"""
Created on May 20, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import unicode_literals

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
#     verbose_name = "Core"

    def ready(self):
        import core.signals
    