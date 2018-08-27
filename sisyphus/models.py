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
    reference_genome = create_chrfield("reference_genome", blank=False, null=False)

    def __str__(self):
        return "Reference Genome {reference_genome}".format(reference_genome=self.reference_genome)


class AnalysisRun(models.Model):
    """
    Analysis/workflow details filled in or changed by database admin
    """

    last_updated = models.DateTimeField(
        "Analysis last updated date/time",
        null=True,
        default=timezone.now
    )

    run_status = create_chrfield(
        "Run Status",
        blank=False,
        null=False,
        default="Unknown"
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

    analysis_jira_ticket = create_chrfield("Jira ticket", blank=False)

    # database relationships
    analysis_run = models.OneToOneField(AnalysisRun, null=True)

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
        default=timezone.now
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

# TODO(matt): clean me up!
import os
import json
import requests

SALTANT_SERVER_API_BASE_URL = 'https://shahlabjobs.ca/api'
SALTANT_SERVER_API_INSTANCE_CREATE_URL = (
    SALTANT_SERVER_API_BASE_URL
    + '/taskinstances/')
SALTANT_SERVER_API_INSTANCE_CLONE_URL_TEMPLATE = (
    SALTANT_SERVER_API_BASE_URL
    + '/taskinstances/{uuid}/clone/')
SALTANT_SERVER_API_INSTANCE_TERMINATE_URL_TEMPLATE = (
    SALTANT_SERVER_API_BASE_URL
    + '/taskinstances/{uuid}/terminate/')

SALTANT_TASK_TYPE = 9
SALTANT_TASK_QUEUE = 1
os.environ['SALTANT_AUTH_TOKEN'] = '3339553a38072521bc25c89ab8c8fe9cfffa37b0'


class DlpAnalysisInformation(AbstractAnalysisInformation):
    # TODO(matt): clean me up!

    # Shahlab Jobs stuff
    saltant_job_uuid = models.CharField(max_length=36,
                                        editable=False,
                                        null=True)

    def start_analysis_run(self):
        r = requests.post(
            SALTANT_SERVER_API_INSTANCE_CREATE_URL,
            headers={
                'Authorization': 'Token ' + os.environ['SALTANT_AUTH_TOKEN']},
            data={
                "name": self.analysis_jira_ticket,
                "arguments": json.dumps(
                    {"analysis_id": self.id}),
                "task_type": SALTANT_TASK_TYPE,
                "task_queue": SALTANT_TASK_QUEUE,})

        assert 200 <= r.status_code < 300

        self.saltant_job_uuid = r.json()['uuid']
        self.save()

    def restart_analysis_run(self):
        r = requests.post(
            SALTANT_SERVER_API_INSTANCE_CLONE_URL_TEMPLATE.format(uuid=self.saltant_job_uuid),
            headers={
                'Authorization': 'Token ' + os.environ['SALTANT_AUTH_TOKEN']},)

        assert 200 <= r.status_code < 300

        self.saltant_job_uuid = r.json()['uuid']
        self.save()

    def kill_analysis_run(self):
        r = requests.post(
            SALTANT_SERVER_API_INSTANCE_TERMINATE_URL_TEMPLATE.format(uuid=self.saltant_job_uuid),
            headers={
                'Authorization': 'Token ' + os.environ['SALTANT_AUTH_TOKEN']},)

        assert 200 <= r.status_code < 300

        self.saltant_job_uuid = r.json()['uuid']
        self.save()


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

    lanes = models.ManyToManyField(DlpLane)


class PbalAnalysisInformation(AbstractAnalysisInformation):
    sequencings = models.ManyToManyField(PbalSequencing)

    version = models.ForeignKey(
        PbalAnalysisVersion,
        verbose_name="Analysis Version",
        on_delete=models.CASCADE,
    )


class TenxAnalysisInformation(AbstractAnalysisInformation):
    sequencings = models.ManyToManyField(TenxSequencing)

    version = models.ForeignKey(
        TenxAnalysisVersion,
        verbose_name="Analysis Version",
        on_delete=models.CASCADE,
    )





