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

    def has_additional_sample_information(self):
        return hasattr(self, 'additionalsampleinformation')

    def get_absolute_url(self):
        return reverse("core:sample_detail", kwargs={"pk": self.pk})

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


class Analysis(models.Model, FieldValue):
    class Meta:
        ordering = ['id']

    input_type = create_chrfield("Input Type", choices=INPUT_TYPE, null=False)

    version = create_chrfield("Analysis Version", blank=False)

    jira_ticket =  create_chrfield("Analysis Jira Ticket", blank=False)

    run_status = create_chrfield(
        "Run Status",
        blank=False,
        null=False,
        default=IDLE,
        choices=RUN_STATUS_CHOICES
    )

    last_updated_date = models.DateTimeField("Last Updated Date", auto_now=True)

    submission_date = models.DateField(
        "Analysis Submission Date",
        default=datetime.date.today, # this needs to be a date (not datetime)
    )

    description = create_textfield("Description")

    #Avoid using GenericForeignKey
    #All are set to None but one
    dlp_library = models.ForeignKey('core.DlpLibrary', null=True)
    pbal_library = models.ForeignKey('pbal.PbalLibrary', null=True)
    tenx_library = models.ForeignKey('core.TenxLibrary', null=True)

    tenx_lanes =  models.ManyToManyField('core.TenxLane', blank=True)

    def __str__(self):
        res = str(self.id).zfill(3) + "_ANALYSIS_" + self.input_type
        return res

    def get_absolute_url(self):
        return reverse("core:analysis_detail" , kwargs={"pk": self.pk})

class DlpLibrary(models.Model, FieldValue, LibraryAssistant):

    """
    DLP library contains several Cell objects.
    """

    class Meta:
        ordering = ('sample', 'pool_id')

    library_type = 'dlp'

    # track history
    history = HistoricalRecords(table_name='dlp_history_library')

    # fields
    pool_id = create_chrfield(
        "Chip ID",
        blank=False,
    )
    jira_ticket = create_chrfield(
        "Jira ticket",
        blank=True,
    )
    num_sublibraries = create_intfield(
        "Number of sublibraries",
        default=0,
    )

    exclude_from_analysis = models.BooleanField(
        default=False,
        null=False,
    )

    title = create_textfield("Title")
    quality = models.DecimalField("Quality", max_digits=10, decimal_places=2, default=0.75)

    def get_library_id(self):
        return '_'.join([self.sample.sample_id, self.pool_id])

    def has_sublibrary_info(self):
        return self.sublibraryinformation_set.exists()

    def get_last_analysis_status(self):
        last_analysis = self.dlpanalysisinformation_set.order_by('analysis_submission_date').last()
        if(last_analysis is None):
            return False
        if(str(last_analysis.analysis_run.run_status) == 'hmmcopy_complete' or str(last_analysis.analysis_run.run_status) == 'complete'):
            return True
        return False
    fields_to_exclude = ['ID', 'Primary Sample']
    values_to_exclude = ['id', 'primary sample']

    projects = models.ManyToManyField(
        Project,
        verbose_name="Project",
        blank=True
    )

    # related sample
    sample = models.ForeignKey(
        Sample,
        verbose_name="Primary Sample",
        on_delete=models.CASCADE,
    )

    # related libraries
    relates_to_dlp = models.ManyToManyField(
        'DlpLibrary',   # DlpLibrary hasn't been seen yet
        verbose_name="Relates to (DLP)",
        blank=True,
    )
    relates_to_tenx = models.ManyToManyField(
        'TenxLibrary',   # TenxLibrary hasn't been seen yet
        verbose_name="Relates to (Tenx)",
        blank=True,
    )

    # fields
    description = create_textfield("Description")
    result = create_textfield("Result")

    failed = models.BooleanField(
        "Failed",
        default=False,
        blank=False
    )

    def __str__(self):
        return 'LIB_' + self.get_library_id()

    def get_absolute_url(self):
        return reverse(self.library_type + ":library_detail", kwargs={"pk": self.pk})

class TenxChip(models.Model, FieldValue):

    # Chip Model for TenX Libraries
    history = HistoricalRecords(table_name='tenx_history_chip')

    LAB_NAMES = (
        ("SA", "Sam Aparicio"),
        ("DH", "David Huntsman"),
    )

    lab_name = create_chrfield(
        "Lab Name",
        default = "SA",
        choices=LAB_NAMES,
        blank = True
    )

    #TenXLibrary name depend on below methods, so please be mindful when making changes
    def get_id(self):
        return "CHIP" + format(self.id, "04")

    def __str__(self):
        return self.get_id() +"_" + self.lab_name

    def get_absolute_url(self):
        return reverse("tenx" + ":chip_detail", kwargs={"pk": self.pk})



class TenxLibrary(models.Model, FieldValue, LibraryAssistant):
    """
    10x library contains several Cell objects.
    """
    class Meta:
        ordering = ['sample']

    name = create_chrfield(
        "Library Name",
        blank=True,
    )

    library_type = 'tenx'

    # track history
    history = HistoricalRecords(table_name='tenx_history_library')

    # fields
    jira_ticket = create_chrfield(
        "Jira ticket",
        blank=True,
    )

    experimental_condition = create_chrfield(
        "Experimental condition",
        max_length=1025,
        blank=True,
        null=True,
    )

    num_sublibraries = create_intfield(
        "Number of sublibraries",
        default=0,
    )

    chips = models.ForeignKey(
        TenxChip,
        verbose_name="Chip",
        on_delete=models.CASCADE,
        null=True
    )

    chip_well = models.IntegerField(
        default=0,
        choices=CHIP_WELL
    )

    condition = create_chrfield(
        "Condition",
        blank=True,
    )

    google_sheet = create_chrfield(
        "Google Sheet Link",
        null=True,
        blank=True,
        max_length=255,
    )

    def get_library_id(self):
        return '_'.join([self.sample.sample_id])

    def get_id(self):
        return self.name
    fields_to_exclude = ['ID', 'Primary Sample']
    values_to_exclude = ['id', 'primary sample']

    projects = models.ManyToManyField(
        Project,
        verbose_name="Project",
        blank=True
    )

    # related sample
    sample = models.ForeignKey(
        Sample,
        verbose_name="Primary Sample",
        on_delete=models.CASCADE,
    )

    # related libraries
    relates_to_dlp = models.ManyToManyField(
        'DlpLibrary',   # DlpLibrary hasn't been seen yet
        verbose_name="Relates to (DLP)",
        blank=True,
    )
    relates_to_tenx = models.ManyToManyField(
        'TenxLibrary',   # TenxLibrary hasn't been seen yet
        verbose_name="Relates to (Tenx)",
        blank=True,
    )

    # fields
    description = create_textfield("Description", max_length=1024)
    result = create_textfield("Result")

    failed = models.BooleanField(
        "Failed",
        default=False,
        blank=False
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse(self.library_type + ":library_detail", kwargs={"pk": self.pk})

class TenxPool(models.Model, FieldValue):
    LOCATION = (
        ('BCCAGSC', 'GSC'),
        ('UBCBRC', 'UBC'),
    )

    pool_name = create_chrfield("Pool Name", null=True, blank=True)
    gsc_pool_name = create_chrfield("GSC Pool Name", null=True, blank=True)
    construction_location = create_chrfield("Construction Location", choices=LOCATION, null=True, blank=True)
    constructed_by = create_chrfield("Constructed By", null=True, blank=True)
    constructed_date =models.DateField("Construction Date", null=True, blank=True)
    libraries = models.ManyToManyField(TenxLibrary)

    def __str__(self):
        return self.pool_name



    def get_library_ids(self):
        return [l.id for l in self.liraries.all()]

    def jira_tickets(self):
        jira_tickets =[]
        sample_ids =[]
        for l in self.libraries.all():
            if l.jira_ticket:
                jira_tickets.append(l.jira_ticket)
                sample_ids.append(l.sample.sample_id)
        return jira_tickets, sample_ids

    def get_absolute_url(self):
        return reverse("tenx" + ":pool_detail", kwargs={"pk": self.pk})

class ChipRegion(models.Model, FieldValue):

    """
    Region code for a sublibrary. DLP only.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    # database relationships
    library = models.ForeignKey(
        DlpLibrary,
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
        DlpLibrary,
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
        # add leading zero to one digit row/col
        row = str(self.row) if self.row > 9 else '0' + str(self.row)
        col = str(self.column) if self.column > 9 else '0' + str(self.column)
        res = '_'.join(
            [self.sample_id.sample_id, self.library.pool_id, 'R' + row, 'C' + col]
        )
        return res

    def __str__(self):
        return self.get_sublibrary_id()


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



class DlpLibrarySampleDetail(models.Model, FieldValue):

    """
    DLP library sample details.
    """

    history = HistoricalRecords(table_name='dlp_history_library_sample_detail')

    # database relationships
    library = models.OneToOneField(
        DlpLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # fields
    sample_spot_date = models.DateField(
        "Sample spot date",
        default=datetime.date.today
    )
    spotting_location = create_chrfield(
        "Spotting location",
        choices=spotting_location_choices,
    )

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    # fields
    cell_state = create_chrfield(
        "Cell state",
        choices=cell_state_choices,
    )
    estimated_percent_viability = create_intfield("Estimated percent viability")
    label_of_original_sample_vial = create_chrfield("Label of original sample vial")
    lims_vial_barcode = create_chrfield("LIMS vial barcode")
    original_storage_temperature = create_intfield("Original storage temperature (C)")
    passage_of_cell_line  = create_intfield("Passage")
    sample_notes = create_textfield("Sample notes")
    sample_preparation_method = create_textfield("Sample preparation method")
    sample_preservation_method = create_chrfield("Sample preservation method")

class TenxLibrarySampleDetail(models.Model, FieldValue):

    """
    10x library sample details.
    """
    history = HistoricalRecords(table_name='tenx_history_library_sample_detail')

    # database relationships
    library = models.OneToOneField(
        TenxLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # fields
    sample_prep_date = models.DateField(
        "Sample prep date",
        null=True,
        blank=True,
    )
    sorting_location = create_chrfield(
        "Sorting location",
        default="TFL flow facility",
    )
    num_cells_targeted = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Number of cells targeted",
    )

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']


    # fields
    cell_state = create_chrfield(
        "Cell state",
        choices=cell_state_choices,
    )
    estimated_percent_viability = create_intfield("Estimated percent viability")
    label_of_original_sample_vial = create_chrfield("Label of original sample vial")
    lims_vial_barcode = create_chrfield("LIMS vial barcode")
    original_storage_temperature = create_intfield("Original storage temperature (C)")
    passage_of_cell_line  = create_intfield("Passage")
    sample_notes = create_textfield("Sample notes")
    sample_preparation_method = create_textfield("Sample preparation method")
    sample_preservation_method = create_chrfield("Sample preservation method")

class DlpLibraryConstructionInformation(models.Model, FieldValue):

    """
    DLP library construction information.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    history = HistoricalRecords(table_name='dlp_history_library_construction_information')

    # database relationships
    library = models.OneToOneField(
        DlpLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # fields
    chip_format = create_chrfield(
        "Chip format",
        choices=chip_format_choices,
        default="W",
    )
    library_construction_method = create_chrfield(
        "Library construction method",
        default="Nextera (Illumina)",
    )
    library_type = create_chrfield(
        "Library type",
        default="genome",
    )
    library_notes = create_textfield("Library notes")
    library_prep_date = models.DateField(
        "Library prep date",
        null=True,
        blank=True,
    )
    number_of_pcr_cycles = create_intfield("Number of PCR cycles")
    protocol = create_textfield("Protocol")
    spotting_location = create_chrfield(
        "Spotting location",
        choices=spotting_location_choices,
    )

class TenxLibraryConstructionInformation(models.Model, FieldValue):

    """
    10x library construction information.
    """


    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']
    history = HistoricalRecords(table_name='tenx_history_library_construction_information')

    # database relationships
    library = models.OneToOneField(
        TenxLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # fields
    library_construction_method = create_chrfield(
        "Library construction method",
        default="10x Genomics",
    )
    library_type = create_chrfield(
        "Library type",
        default="transciptome",
    )
    submission_date = models.DateField(
        "Submission date",
        null=True,
        blank=True,
    )
    library_prep_location = create_chrfield(
        "Library prep location",
        default="UBC-BRC",
    )
    chip_lot_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Chip lot number",
    )
    reagent_lot_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Reagent lot number",
    )
    library_type = models.CharField(
        null=True,
        blank=True,
        choices=TENX_LIBRARY_TYPE_CHOICES,
        max_length=20,
        verbose_name="Library type",
    )
    index_used = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        choices=TENX_INDEX_CHOICES,
        verbose_name="Index used",
    )
    pool = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Pool",
    )
    concentration = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="DNA concentration (nM)",
    )

    chemistry_version = models.CharField(
        null=True,
        choices=CHEMISTRY_VERSION_CHOICES,
        verbose_name="Chemistry Version",
        max_length=150,
        default="VERSION_2"
    )

class DlpLibraryQuantificationAndStorage(models.Model, FieldValue):

    """
    DLP library quantification and storage.
    """
    history = HistoricalRecords(table_name='dlp_history_library_q_and_s')

    fields_to_exclude = [
        'ID',
        'Library',
        'Freezer',
        'Rack',
        'Shelf',
        'Box',
        'Position in box',
    ]

    values_to_exclude = [
        'id',
        'library',
        'freezer',
        'rack',
        'shelf',
        'box',
        'position_in_box',
    ]

    library = models.OneToOneField(
        DlpLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # fields
    average_size = create_intfield("Average size (bp)")
    dna_concentration_nm = models.DecimalField(
        "DNA concentration (nM)",
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
    )
    dna_concentration_ngul = models.DecimalField(
        "DNA concentration (ng/uL)",
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
    )
    dna_volume = create_chrfield("DNA volume (uL)")
    freezer = create_chrfield("Freezer")
    rack = create_intfield("Rack")
    shelf = create_intfield("Shelf")
    box = create_intfield("Box")
    position_in_box = create_intfield("Position in box")
    library_tube_label = create_chrfield("Library tube label")
    quantification_method = create_chrfield(
        "Quantification method",
        default="Bioanalyzer",
    )
    size_range = create_chrfield("Size range (bp)")
    size_selection_method = create_chrfield(
        "Size selection method",
        default="AmpureXP",
    )
    storage_medium = create_chrfield(
        "Storage medium",
        default="TE 10:0.1",
    )
    agilent_bioanalyzer_xad = models.FileField(
        "Agilent bioanalyzer xad file",
        upload_to=upload_dlp_library_path,
        max_length=200,
        null=True,
        blank=True,
    )
    agilent_bioanalyzer_image = models.FileField(
        "Agilent bioanalyzer image file",
        upload_to=upload_dlp_library_path,
        max_length=200,
        null=True,
        blank=True,
    )

    # fields
    qc_check = create_chrfield(
        "QC check",
        choices=qc_check_choices,
    )
    qc_notes = create_textfield("QC notes")

    def library_location(self):
        loc = None
        if self.freezer:
            loc = '_'.join([
                'CRC',
                self.freezer,
                str(self.rack) + ':' + str(self.shelf),
                str(self.box) + ':' + str(self.position_in_box),
            ])
        return loc

class TenxLibraryQuantificationAndStorage(models.Model, FieldValue):

    """
    10x library quantification and storage.
    """
    history = HistoricalRecords(table_name='tenx_history_library_q_and_s')

    fields_to_exclude = ['ID', 'Library']

    values_to_exclude = ['id', 'library']

    # database relationships
    library = models.OneToOneField(
        TenxLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    agilent_bioanalyzer_xad = models.FileField(
        "Agilent bioanalyzer xad file",
        upload_to=upload_tenx_library_path,
        max_length=200,
        null=True,
        blank=True,
    )
    agilent_bioanalyzer_image = models.FileField(
        "Agilent bioanalyzer image file",
        upload_to=upload_tenx_library_path,
        max_length=200,
        null=True,
        blank=True,
    )


    # fields
    qc_check = create_chrfield(
        "QC check",
        choices=qc_check_choices,
    )
    qc_notes = create_textfield("QC notes")

class DlpSequencing(models.Model, FieldValue):

    """
    DLP sequencing information.
    """

    library_type = 'dlp'

    # track history
    history = HistoricalRecords(table_name='dlp_history_sequencing')

    # database relationships
    library = models.ForeignKey(
        DlpLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
    )

    rev_comp_override = create_chrfield(
        "Reverse Complement Override",
        choices=rev_comp_override_choices,
        default=None,
        null=True,
    )

    """
    Sequencing information base class.
    """

    class Meta:
        unique_together = ('library', 'sequencing_center', 'sequencing_instrument')

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']


    # fields
    adapter = create_chrfield(
        "Adapter",
        default="CTGTCTCTTATACACATCT",
    )
    format_for_data_submission = create_chrfield(
        "Format for data dissemination",
        default="fastq",
    )
    index_read_type = create_chrfield(
        "Index read type",
        default="Dual Index (i7 and i5)",
    )
    index_read1_length = create_intfield(
        "Index read1 length",
        default=6,
    )
    index_read2_length = create_intfield(
        "Index read2 length",
        default=6,
    )
    read_type = create_chrfield(
        "Read type",
        choices=read_type_choices,
        default="P",
    )
    read1_length = create_intfield(
        "Read1 length",
        default=150,
    )
    read2_length = create_intfield(
        "Read2 length",
        default=150,
    )

    sequencing_instrument = create_chrfield(
        "Sequencing instrument",
        choices=sequencing_instrument_choices,
        default="HX",
    )
    sequencing_output_mode = create_chrfield(
        "Sequencing output mode",
        choices=sequencing_output_mode_choices,
    )
    short_description_of_submission = create_chrfield(
        "Short description of submission",
        max_length=150,
    )
    submission_date = models.DateField(
        "Submission date",
        default= datetime.date.today
        )
    relates_to = models.ManyToManyField(
        "self",
        verbose_name="Relates to",
        blank=True,
    )

    number_of_lanes_requested = models.PositiveIntegerField(
        default=0,
        verbose_name="Sequencing Goal"
    )

    #Set to the last time number_of_lanes_requested was updated
    lane_requested_date = models.DateField(
        null=True,
    )

    gsc_library_id = create_chrfield("GSC library ID")
    sequencer_id = create_chrfield("Sequencer ID")
    sequencing_center = create_chrfield(
        "Sequencing center",
        choices=SEQ_CENTER,
        default='BCCAGSC',
        blank=False
    )
    sequencer_notes = create_textfield("Sequencing notes")

    objects = SequencingManager()

    analysis = models.ManyToManyField(
        Analysis,
        verbose_name="Analysis",
        blank=True
    )

    def __init__(self, *args, **kwargs):
        super(DlpSequencing, self).__init__(*args, **kwargs)
        self.old_number_of_lanes_requested = self.number_of_lanes_requested

    def __str__(self):
        return 'SEQ_' + self.library.get_library_id() +"_" + str(self.id)

    def has_sequencing_detail(self):
        return hasattr(self, self.library_type + 'sequencingdetail')

    def get_absolute_url(self):
        return reverse(self.library_type + ":sequencing_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.number_of_lanes_requested != self.old_number_of_lanes_requested:
            self.old_number_of_lanes_requested = self.number_of_lanes_requested
            self.lane_requested_date = datetime.date.today()
        super(DlpSequencing, self).save(*args,**kwargs)


class TenxSequencing(models.Model, FieldValue):

    """
    10x sequencing information.
    """

    library_type = 'tenx'

    # track history
    history = HistoricalRecords(table_name='tenx_history_sequencing')

    # database relationships
    library = models.ForeignKey(
        TenxLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    tenx_pool = models.ForeignKey(TenxPool, null=True, blank=True)

    """
    Sequencing information base class.
    """

    class Meta:
        unique_together = ('library', 'sequencing_center', 'sequencing_instrument')

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    sequencing_instrument = create_chrfield(
        "Sequencing instrument",
        choices=sequencing_instrument_choices,
        default="HX",
    )

    submission_date = models.DateField(
        "Submission date",
        default= datetime.date.today
        )

    sequencer_id = create_chrfield("Sequencer ID")
    sequencing_center = create_chrfield(
        "Sequencing center",
        choices=SEQ_CENTER,
        default='BCCAGSC',
        blank=False
    )
    sequencer_notes = create_textfield("Sequencing notes")


    analysis = models.ManyToManyField(
        Analysis,
        verbose_name="Analysis",
        blank=True
    )

    number_of_lanes_requested = models.PositiveIntegerField(
        default=0,
        verbose_name="Sequencing Goal"
    )

    # Set to the last time number_of_lanes_requested was updated
    lane_requested_date = models.DateField(
        null=True,
    )

    def __str__(self):
        return 'SEQ_' + str(self.id)

    def has_sequencing_detail(self):
        return hasattr(self, self.library_type + 'sequencingdetail')

    def get_absolute_url(self):
        return reverse(self.library_type + ":sequencing_detail", kwargs={"pk": self.pk})

    def __init__(self, *args, **kwargs):
        super(TenxSequencing, self).__init__(*args, **kwargs)
        self.old_number_of_lanes_requested = self.number_of_lanes_requested

    def save(self, *args, **kwargs):
        if self.number_of_lanes_requested != self.old_number_of_lanes_requested:
            self.old_number_of_lanes_requested = self.number_of_lanes_requested
            self.lane_requested_date = datetime.date.today()
        super(TenxSequencing, self).save(*args, **kwargs)


class DlpLane(models.Model, FieldValue):

    """
    Dlp lane information.
    """
    history = HistoricalRecords(table_name='dlp_history_lane')

    # database relationships
    sequencing = models.ForeignKey(
        DlpSequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
    )

    fields_to_exclude = ['ID', 'Lane']
    values_to_exclude = ['id', 'lane']

    flow_cell_id = create_chrfield(
        "Flow cell/Lane ID",
        null=False,
        blank=False,
    )

    path_to_archive = create_chrfield(
        "Path to archive",
        max_length=150,
        null=True,
        blank=True,
    )

    sequencing_date = models.DateTimeField(
        null=True
    )

    def __str__(self):
        return self.flow_cell_id


class TenxLane(models.Model, FieldValue):

    """
    10x lane information.
    """
    history = HistoricalRecords(table_name='tenx_history_lane')
    # database relationships
    sequencing = models.ForeignKey(
        TenxSequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
    )

    fields_to_exclude = ['ID', 'Lane']
    values_to_exclude = ['id', 'lane']

    flow_cell_id = create_chrfield(
        "Flow cell/Lane ID",
        null=False,
        blank=False,
    )

    path_to_archive = create_chrfield(
        "Path to archive",
        max_length=150,
        null=True,
        blank=True,
    )

    tantalus_datasets = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)

    sequencing_date = models.DateTimeField(
        null=True
    )

    def __str__(self):
        return self.flow_cell_id


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
