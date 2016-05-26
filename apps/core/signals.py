"""
Created on May 20, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sample, CellTable

## Update num_libraries of the Sample instance
@receiver(post_save, sender=CellTable)
def update_num_libraries(sender, instance, **kwargs):
    print '>' * 40, instance
    sample = instance.sample
    sample.num_libraries = len(instance.cell_set.all())
    sample.save()
