"""
Created on July 6, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from __future__ import unicode_literals
import datetime
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
from simple_history.models import HistoricalRecords

from core.models import DlpSequencing,DlpLibrary,DlpLane
from tenx.models import *
from core.helpers import *
from core.constants import *
from pbal.models import PbalSequencing


class DlpAnalysisVersion(models.Model):
    """
    Keeps track of the available analysis software versions.
    """
    history = HistoricalRecords(table_name='dlp_history_analysis_version')
    version = create_chrfield(
        "DlpAnalysis Version",
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.version

class ReferenceGenome(models.Model):
    """
    The Reference genome to be used by the single cell pipeline
    """
    history = HistoricalRecords(table_name='ref_genome_history')

    reference_genome = create_chrfield("reference_genome", blank=False, null=False)

    def __str__(self):
        return "Reference Genome {reference_genome}".format(reference_genome=self.reference_genome)


class AnalysisRun(models.Model):
    """
    Analysis/workflow details filled in or changed by database admin
    """

    history = HistoricalRecords(table_name='analysis_run_history')

    last_updated = models.DateTimeField(
        "Analysis last updated date/time",
        null=True,
        default=timezone.now
    )

    run_status = create_chrfield(
        "Run Status",
        blank=False,
        null=False,
        default=IDLE,
        choices=RUN_STATUS_CHOICES
    )

    log_file = create_chrfield("error_log", default=None, blank=True, null=True, max_length=1000)

    sftp_path = create_chrfield(
        "sftp path",
        null=True,
        blank=True,
    )

    blob_path = create_chrfield(
        "Blob path",
        null=True,
        blank=True,
    )

    def __str__(self):
        return 'Run Status: %s, Last Updated  %s' % (self.run_status, self.last_updated)

    def get_absolute_url(self):
        return reverse("sisyphus:analysisrun_detail")


class DlpAnalysisInformation(models.Model):
    history = HistoricalRecords(table_name='dlp_analysis_info_history')

    library = models.ForeignKey(
        DlpLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
    )

    sequencings = models.ManyToManyField(DlpSequencing)

    version = models.ForeignKey(
        DlpAnalysisVersion,
        verbose_name="Analysis Version",
        on_delete=models.CASCADE,
    )

    lanes = models.ManyToManyField(DlpLane, blank=True)
    fields_to_exclude = ['ID']
    values_to_exclude = ['id']

    analysis_jira_ticket = create_chrfield("Analysis Jira ticket", blank=False)

    # database relationships
    analysis_run = models.OneToOneField(AnalysisRun, blank=True, null=True)


    # fields
    priority_level = create_chrfield(
        "Priority Level",
        choices=priority_level_choices,
        default="L",
        blank=False,
        null=False,
    )

    aligner = create_chrfield(
        "Aligner",
        choices=aligner_choices,
        default="A",
        blank=False,
        null=False,
    )

    smoothing = create_chrfield(
        "Smoothing",
        choices=smoothing_choices,
        default="M",
        blank=False,
        null=False,
    )

    # fields
    analysis_submission_date = models.DateField(
        "Analysis submission date",
        null=True,
        default=datetime.date.today, # this needs to be a date (not datetime)
    )

    reference_genome = models.ForeignKey(
        ReferenceGenome,
        verbose_name="ReferenceGenome",
        null=True,
    )

    verified = create_chrfield(
        "Verified",
        choices=verified_choices,
        default="F",
    )

    def get_absolute_url(self):
        return reverse("sisyphus:analysisinformation_detail", kwargs={'pk':self.pk})

    def __str__(self):
        return "Analysis of {jira}".format(jira=self.analysis_jira_ticket)

    class Meta:
        ordering = ['pk']
