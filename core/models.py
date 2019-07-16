"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated Nov 27, 2017 by Spencer Vatrt-Watts (github.com/Spenca)
"""

from __future__ import unicode_literals

#============================
# Django imports
#----------------------------
import datetime

from django.contrib.postgres.fields import ArrayField
from django.core.urlresolvers import reverse
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, int_list_validator, \
    validate_comma_separated_integer_list

#============================
# App imports
#----------------------------
from .constants import *
from .helpers import *


#============================
# 3rd-party app imports
#----------------------------
from simple_history.models import HistoricalRecords



#============================
# helpers
#----------------------------
class SequencingManager(models.Manager):
    def with_data(self):
        return [obj for obj in self.get_queryset() if obj.library.is_sequenced()]

#============================
# Project models
#----------------------------
class Project(models.Model, FieldValue):

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:project_detail", kwargs={"pk": self.pk})

    def get_libraries(self):
        return list(self.dlplibrary_set.all()) + list(self.pballibrary_projects.all()) + list(self.tenxlibrary_set.all())

    class Meta:
        ordering = ['name']


class PipelineTag(models.Model):
    history = HistoricalRecords(table_name='pipeline_tag_history')
    title = models.CharField(max_length=150, unique=True)

#============================
# Sample models
#----------------------------
class Sample(models.Model, FieldValue):

    """
    Base class of different sample types.
    """

    class Meta:
        ordering = ['sample_id']

    # track history
    history = HistoricalRecords(table_name='history_sample')

    # choices
    sample_type_choices = (
        ('P','Patient'),
        ('C','Cell Line'),
        ('X','Xenograft'),
        ('Or', 'Organoid'),
        ('O','Other'),
    )

    # required fields
    sample_id = create_chrfield(
        "Sample ID",
        blank=False,
    )

    # other fields
    taxonomy_id = create_chrfield(
        "Taxonomy ID",
        default="9606",
    )
    sample_type = create_chrfield(
        "Sample type",
        choices=sample_type_choices,
    )
    anonymous_patient_id = create_chrfield("Anonymous patient ID")
    cell_line_id = create_chrfield("Cell line ID")
    xenograft_id = create_chrfield("Xenograft ID")
    xenograft_recipient_taxonomy_id = create_chrfield(
        "Xenograft recipient taxonomy ID",
        default="10090",
    )
    xenograft_treatment_status = create_chrfield(
        "Xenograft treatment status",
        default="",
        null=False,
    )
    strain = create_chrfield("Strain")
    xenograft_biopsy_date = models.DateField(
        "Xenograft biopsy date",
        null=True,
        blank=True,
    )
    notes = create_textfield("Notes")

    pipeline_tag = models.ForeignKey(PipelineTag, null=True)

    def has_additional_sample_information(self):
        return hasattr(self, 'additionalsampleinformation')

    def get_absolute_url(self):
        return reverse("core:sample_detail", kwargs={"pk": self.pk})

    def get_dlp_seq_count(self):
        count = 0
        for library in self.dlplibrary_set.all():
            count += library.dlpsequencing_set.count()
        return count

    def get_tenx_seq_count(self):
        count = 0
        for library in self.tenxlibrary_set.all():
            count += library.tenxsequencing_set.count()
        return count

    def __str__(self):
        return self.sample_id


class AdditionalSampleInformation(models.Model, FieldValue):

    """
    Additional sample information.
    """

    # database relationships
    sample = models.OneToOneField(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE,
    )

    # fields
    tissue_state = create_chrfield(
        "Tissue State",
        choices=TISSUE_STATES,
        default='NONE',
    )
    cancer_type = create_chrfield(
        "Cancer Type",
        blank=True
    )
    cancer_subtype = create_chrfield(
        "Cancer Subtype",
        blank=True
    )
    disease_condition_health_status = create_chrfield("Disease condition/health status")
    sex = create_chrfield(
        "Sex",
        choices=sex_choices,
    )
    patient_biopsy_date = models.DateField(
        "Patient biopsy date",
        null=True,
        blank=True,
    )
    anatomic_site = create_chrfield(
        "Anatomic site",
        blank=False,
    )
    anatomic_sub_site = create_chrfield("Anatomic sub-site")
    developmental_stage = create_chrfield("Developmental stage")
    tissue_type = create_chrfield(
        "Tissue type",
        choices=tissue_type_choices,
        blank=False,
    )
    cell_type = create_chrfield("Cell type")
    pathology_disease_name = create_chrfield("Pathology/disease name (for diseased samples only)")
    additional_pathology_info = create_chrfield("Additional pathology information")
    grade = create_chrfield("Grade")
    stage = create_chrfield("Stage")
    tumour_content = create_chrfield("Tumor content (%)")
    pathology_occurrence = create_chrfield(
        "Pathology occurrence",
        choices=pathology_occurrence_choices,
    )
    treatment_status = create_chrfield(
        "Treatment status",
        choices=treatment_status_choices,
    )
    family_information = create_chrfield("Family information")

    history = HistoricalRecords(table_name='additional_sample_information_history')

    def __str__(self):
        res = '_'.join([self.sample.sample_id, 'additional_information'])
        return res


class ChipRegion(models.Model, FieldValue):

    """
    Region code for a sublibrary. DLP only.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    # database relationships
    library = models.ForeignKey(
        'dlp.DlpLibrary',
        verbose_name='Library',
        on_delete=models.CASCADE,
    )

    region_code = create_chrfield("region_code")

    history = HistoricalRecords(table_name='chip_region_history')

    def __str__(self):
        return "{}".format(self.region_code)


class SublibraryInformation(models.Model, FieldValue):

    """
    Sublibrary Information from the SmartChipApp output file.
    It's technically a table of cell information. DLP only.
    """

    history = HistoricalRecords(table_name='sub_library_information_history')

    fields_to_exclude = ['ID', 'Library', 'Sample_ID', 'Chip_Region']
    values_to_exclude = ['id', 'library', 'sample_id', 'chip_region']

    # database relationships
    library = models.ForeignKey(
        'dlp.DlpLibrary',
        verbose_name="Library",
        on_delete=models.CASCADE,
    )

    chip_region = models.ForeignKey(
        ChipRegion,
        verbose_name="Chip_Region",
        null=True,
        on_delete=models.CASCADE,
    )

    sample_id = models.ForeignKey(
        Sample,
        verbose_name="Sample_ID",
        on_delete=models.CASCADE,
        null=True,
    )

    # fields
    sample = create_chrfield("Sample")
    row = create_intfield("Row")
    column = create_intfield("Column")
    img_col = create_intfield("Image Column")
    file_ch1 = create_chrfield("File_Ch1")
    file_ch2 = create_chrfield("File_Ch2")
    fld_section = create_chrfield("Fld_Section")
    fld_index = create_chrfield("Fld_Index")
    num_live = create_intfield("Num_Live")
    num_dead = create_intfield("Num_Dead")
    num_other = create_intfield("Num_Other")
    rev_live = create_intfield("Rev_Live")
    rev_dead = create_intfield("Rev_Dead")
    rev_other = create_intfield("Rev_Other")
    condition = create_chrfield("experimental_condition")
    index_i7 = create_chrfield("Index_I7")
    primer_i7 = create_chrfield("Primer_I7")
    index_i5 = create_chrfield("Index_I5")
    primer_i5 = create_chrfield("Primer_I5")
    pick_met = create_chrfield("cell_call")
    spot_well = create_chrfield("Spot_Well")
    num_drops = create_intfield("Num_Drops")

    def get_sublibrary_id(self):
        return '-'.join([
            self.sample_id.sample_id,
            self.library.pool_id,
            'R' + str(self.row).zfill(2),
            'C' + str(self.column).zfill(2)
        ])


    def __str__(self):
        return self.get_sublibrary_id()


class DoubletInformation(models.Model):

    history = HistoricalRecords(table_name='doublet_information_history')

    fields_to_exclude = ['Library']
    values_to_exclude = ['library']

    library = models.OneToOneField(
        'dlp.DlpLibrary',
        verbose_name="Library",
        on_delete=models.CASCADE,
    )

    live_single = create_intfield(
        "Number of live single cells",
        default=0,
    )

    dead_single = create_intfield(
        "Number of dead single cells",
        default=0,
    )

    other_single = create_intfield(
        "Number of other single cells",
        default=0,
    )

    live_doublet = create_intfield(
        "Number of live doublet cells",
        default=0,
    )

    dead_doublet = create_intfield(
        "Number of dead doublet cells",
        default=0,
    )
    
    other_doublet = create_intfield(
        "Number of mixed doublet cells",
        default=0,
    )

    live_gt_doublet = create_intfield(
        "More than two live cells",
        default=0,
    )

    dead_gt_doublet = create_intfield(
        "More than two dead cells",
        default=0,
    )
    
    other_gt_doublet = create_intfield(
        "More than two other cells",
        default=0,
    )

    def __str__(self):
        return self.library



class MetadataField(models.Model):

    """
    Keeps track of the metadata fields used, and allows ease of creating but still controlling
    added new fields in table. DLP only.
    """

    history = HistoricalRecords(table_name='metadata_history')

    field = create_chrfield(
        "Metadata key",
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.field


class ChipRegionMetadata(models.Model, FieldValue):

    """
    Library/Sublibrary Metadata. DLP only.
    """

    history = HistoricalRecords(table_name='chip_region_metadata_history')

    fields_to_exclude = ['ID', 'Chip_Region']
    values_to_exclude = ['id', 'chip_region']

    # database relationships
    chip_region = models.ForeignKey(
        ChipRegion,
        verbose_name="Chip_Region",
        null=True,
        on_delete=models.CASCADE,
    )
    metadata_field = models.ForeignKey(
        MetadataField,
        verbose_name="Metadata key",
        on_delete=models.CASCADE,
    )

    metadata_value = create_chrfield("Metadata value")

    def __str__(self):
        return "{chip_region_code} - {field}: {value}".format(
            chip_region_code = self.chip_region.region_code,
            field = self.metadata_field.field,
            value = self.metadata_value,
        )





class JiraUser(models.Model):
    history = HistoricalRecords(table_name='jira_user_history')
    username = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    choices = (
        ('dlp', 'DLP'),
        ('tenx', 'TenX'),
    )
    associated_with_dlp = models.BooleanField(default=True)
    associated_with_tenx = models.BooleanField(default=True)

    def __str__(self):
        return self.name

