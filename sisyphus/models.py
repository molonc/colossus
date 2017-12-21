"""
Created on July 6, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from __future__ import unicode_literals
#============================
# Django imports
#----------------------------
from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.postgres.fields import JSONField

#============================
# App imports
#----------------------------
from core.models import DlpSequencing
from core.helpers import *


class AnalysisVersion(models.Model):
    """
    Keeps track of the available analysis software versions.
    """
    version = create_chrfield(
        "Analysis Version",
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.version


class ReferenceGenome(models.Model):
    """
    The Reference genome to be used by the single cell pipeline
    """
    reference_genome = create_chrfield("reference_genome", blank=False, null=False)

    def __str__(self):
        return "Reference Genome {reference_genome}".format(reference_genome=self.reference_genome)


class AnalysisRun(models.Model):

    """
    Analysis/workflow details filled in or changed by database admin
    """

    # database relationships
    # analysis_information = models.OneToOneField(AnalysisInformation)

    # choices
    run_status_choices = (
        ('W', 'Waiting to be reviewed/submitted'),
        ('R', 'Running'),
        ('C', 'Completed successfully'),
        ('E', 'Error in run'),
        ('A', 'Archiving'),
    )

    last_updated = models.DateField(
        "Analysis last updated date/time",
        null=True,
        default=timezone.now
    )

    run_status = create_chrfield(
        "Run Status",
        blank=False,
        null=False,
        choices=run_status_choices,
        default="W"
    )

    log_file = create_chrfield("error_log", default=None, blank=True, null=True, max_length=1000)

    def get_absolute_url(self):
        return reverse("sisyphus:analysisrun_detail")

class AnalysisInformation(models.Model, FieldValue):

    """
    Analysis/workflow information, typical user sees this
    """
    fields_to_exclude=['ID']
    values_to_exclude=['id']

    # database relationships
    sequencings = models.ManyToManyField(DlpSequencing)

    analysis_run = models.OneToOneField(AnalysisRun, null=True)

    # choices
    priority_level_choices = (
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    )

    # fields
    priority_level = create_chrfield(
        "Priority Level",
        choices=priority_level_choices,
        default="L",
        blank=False,
        null=False,
    )

    analysis_jira_ticket = create_chrfield("Jira ticket", blank=False)

    version = models.ForeignKey(
        AnalysisVersion,
        verbose_name="Analysis Version",
        on_delete=models.CASCADE,
    )

    # fields
    analysis_submission_date = models.DateField(
        "Analysis submission date",
        null=True,
        default=timezone.now
    )

    reference_genome = models.ForeignKey(
        ReferenceGenome,
        verbose_name="ReferenceGenome",
        null=True,
    )

    sisyphus_options = JSONField(default={}, blank=True, null=True)

    def get_absolute_url(self):
        return reverse("sisyphus:analysisinformation_detail", kwargs={'pk':self.pk})

    def __str__(self):
        return "Analysis of {jira}".format(jira=self.analysis_jira_ticket)
