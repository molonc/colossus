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

from core.models import DlpSequencing,PbalSequencing,TenxSequencing,DlpLibrary,PbalLibrary,TenxLibrary,DlpLane
from core.helpers import *


class AbstractVersion(models.Model):
    """
    Keeps track of the available analysis software versions.
    """

    class Meta:
        abstract = True


class DlpAnalysisVersion(AbstractVersion):
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


class PbalAnalysisVersion(AbstractVersion):
    """
    Keeps track of the available analysis software versions.
    """
    history = HistoricalRecords(table_name='pbal_history_analysis_version')
    version = create_chrfield(
        "PbalAnalysis Version",
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.version


class TenxAnalysisVersion(AbstractVersion):
    """
    Keeps track of the available analysis software versions.
    """
    history = HistoricalRecords(table_name='tenx_history_analysis_version')
    version = create_chrfield(
        "TenxAnalysis Version",
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
    # Choices for the run status
    IDLE = 'idle'
    ERROR = 'error'
    RUNNING = 'running'
    ARCHIVING = 'archiving'
    COMPLETE = 'complete'
    ALIGN_COMPLETE= 'align_complete'
    HMMCOPY_COMPLETE = 'hmmcopy_complete'
    
    RUN_STATUS_CHOICES = (
        (IDLE, 'Idle'),
        (ERROR, 'Error'),
        (RUNNING, 'Running'),
        (ARCHIVING, 'Archiving'),
        (COMPLETE, 'Complete'),
        (ALIGN_COMPLETE, 'Align Complete'),
        (HMMCOPY_COMPLETE, 'Hmmcopy Complete'),
    )

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


class AbstractAnalysisInformation(models.Model):
    """
    Analysis/workflow information, typical user sees this
    """
    fields_to_exclude = ['ID']
    values_to_exclude = ['id']

    # Aligner choices
    aligner_choices = (
        ('A','bwa-aln'),
        ('M','bwa-mem'),
    )

    # Smoothing choices
    smoothing_choices= (
        ('M','modal'),
        ('L','loess'),
    )

    analysis_jira_ticket = create_chrfield("Analysis Jira ticket", blank=False)

    # database relationships
    analysis_run = models.OneToOneField(AnalysisRun, blank=True, null=True)

    # choices
    priority_level_choices = (
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    )

    verified_choices = (
        ('T', 'True'),
        ('F', 'False'),
    )

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
        abstract = True
        ordering = ['pk']


class DlpAnalysisInformation(AbstractAnalysisInformation):
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


class PbalAnalysisInformation(AbstractAnalysisInformation):
    history = HistoricalRecords(table_name='pbal_analysis_info_history')

    sequencings = models.ManyToManyField(PbalSequencing)

    version = models.ForeignKey(
        PbalAnalysisVersion,
        verbose_name="Analysis Version",
        on_delete=models.CASCADE,
    )


class TenxAnalysisInformation(AbstractAnalysisInformation):
    history = HistoricalRecords(table_name='tenx_analysis_info_history')

    sequencings = models.ManyToManyField(TenxSequencing)

    genome = create_chrfield(
        "Genome",
        blank=True,
    )

    version = models.ForeignKey(
        TenxAnalysisVersion,
        verbose_name="Analysis Version",
        on_delete=models.CASCADE,
    )
