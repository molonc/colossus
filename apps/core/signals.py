"""
Created on May 20, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
# from .models import Sample, CellTable

# ## Update num_sublibraries of the Sample instance
# @receiver(post_save, sender=CellTable)
# def update_num_sublibraries(sender, instance, **kwargs):
#     print '>' * 40, instance
#     sample = instance.sample
#     sample.num_sublibraries = len(instance.cell_set.all())
#     sample.save()
