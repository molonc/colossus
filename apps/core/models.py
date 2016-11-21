"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import unicode_literals

#============================
# Django imports
#----------------------------
from django.core.urlresolvers import reverse
from django.db import models


#============================
# App imports
#----------------------------
from .helpers import *


#============================
# 3rd-party app imports
#----------------------------
from taggit.managers import TaggableManager
from taggit.models import Tag
from simple_history.models import HistoricalRecords
from simple_history import register

## register taggit for tracking its history
register(Tag)


#============================
# helpers
#----------------------------
# library_states = [
#     "not_ready",
#     "submission_ready",
#     "submitted",
#     "sequenced",
#     "resubmitted",
#     ]

class SequencingManager(models.Manager):
    def with_data(self):
        return [obj for obj in self.get_queryset()
        if obj.has_sequencing_detail() and
        obj.sequencingdetail.path_to_archive]


#============================
# Sample models
#----------------------------
class Sample(models.Model, FieldValue):

    """
    Base class of different sample types.
    """

    class Meta:
        ordering = ('sample_id',)

    ## track history
    history = HistoricalRecords(
        table_name='history_sample'
        )

    ## choices
    sample_type_choices = (
        ('P','Patient'),
        ('C','Cell Line'),
        ('X','Xenograft'),
        ('O','Other'),
        )

    ## required fields
    sample_id = create_chrfield("Sample ID", blank=False)

    ## other fields
    taxonomy_id = create_chrfield(
        "Taxonomy ID",
        default="9606"
        )
    sample_type = create_chrfield(
        "Sample type",
        choices=sample_type_choices
        )
    anonymous_patient_id = create_chrfield("Anonymous patient ID")
    cell_line_id = create_chrfield("Cell line ID")
    xenograft_id = create_chrfield("Xenograft ID")
    xenograft_recipient_taxonomy_id = create_chrfield(
        "Xenograft recipient taxonomy ID",
        default="10090"
        )
    strain = create_chrfield("Strain")
    xenograft_biopsy_date = models.DateField(
        "Xenograft biopsy date",
        null=True,
        blank=True,
        )

    def has_additional_sample_information(self):
        return hasattr(self,
            'additionalsampleinformation'
            )

    def get_absolute_url(self):
        return reverse("core:sample_detail", kwargs={"pk": self.pk})

    ## this is no longer needed since each sample can now have only one type.
    # def get_sample_types(self):
    #     """get all the sample types under the same sample_id."""
    #     samples = Sample.objects.filter(sample_id=self.sample_id)
    #     types = [getattr(s, "get_sample_type_display")()
    #         for s in samples
    #         ]
    #     return types

    def __str__(self):
        return self.sample_id


class AdditionalSampleInformation(models.Model, FieldValue):

    """
    Additional sample information.
    """

    ## track history
    # history = HistoricalRecords(
    #     table_name='history_additional_sample_information'
    #     )

    ## database relationships
    sample = models.OneToOneField(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    ## choices 
    # disease_condition_health_status_choices = (
    #     ('H','Healthy'),
    #     ('C','Cystic Fibrosis'),
    #     ('B','Breast Cancer'),
    #     )

    # index_read_type_choices = (
    #     ('on_3rd_read','On 3rd (index-specific) read'),
    #     ('on_forward_read','On forward read'),
    #     ('on_reverse_read','On reverse read'),
    #     )

    pathology_occurrence_choices = (
        ('PR','Primary'),
        ('RC','Recurrent or Relapse'),
        ('ME','Metastatic'),
        ('RM','Remission'),
        ('UN','Undetermined'),
        ('US','Unspecified'),
        )

    sex_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Mixed'),
        ('U', 'Unknown')
        )

    tissue_type_choises = (
        ('N', 'Normal'),
        ('B', 'Benign'),
        ('PM', 'Pre-malignant'),
        ('M', 'Malignant'),
        ('NNP', 'Non-neoplastic Disease'),
        ('U', 'Undetermined'),
        ('HP', 'Hyperplasia'),
        ('MP', 'Metaplasia'),
        ('DP', 'Dysplasia'),
        )

    treatment_status_choices = (
        ('PR','Pre-treatment'),
        ('IN','In-treatment'),
        ('PO','Post-treatment'),
        ('NA','N/A'),
        ('UN','Unknown'),
        )

    ## fields
    disease_condition_health_status = create_chrfield(
        "Disease condition/health status",
        # choices=disease_condition_health_status_choices,
        )
    sex = create_chrfield(
        "Sex",
        choices=sex_choices,
        )
    patient_biopsy_date = models.DateField(
        "Patient biopsy date",
        null=True,
        blank=True,
        )
    anatomic_site = create_chrfield("Anatomic site")
    anatomic_sub_site = create_chrfield("Anatomic sub-site")
    developmental_stage = create_chrfield("Developmental stage")
    tissue_type = create_chrfield(
        "Tissue type",
        choices=tissue_type_choises
        )
    cell_type = create_chrfield("Cell type")
    pathology_disease_name = create_chrfield("Pathology/disease name")
    additional_pathology_info = create_chrfield(
        "Additional pathology information"
        )
    grade = create_chrfield("Grade")
    stage = create_chrfield("Stage")
    tumour_content = create_chrfield("Tumor content (%)")
    pathology_occurrence = create_chrfield(
        "Pathology occurrence",
        choices=pathology_occurrence_choices
        )
    treatment_status = create_chrfield(
        "Treatment status",
        choices=treatment_status_choices
        )
    family_information = create_chrfield("Family information")

    def __str__(self):
        res = '_'.join([
            self.sample.sample_id,
            'additional_information'
            ])
        return res


#============================
# Library models
#----------------------------
class Library(models.Model, FieldValue, LibraryAssistant):

    """
    Library contains several Cell objects.
    """

    class Meta:
        ordering = ('sample', 'pool_id')

    fields_to_exclude = ['ID', 'Sample']
    values_to_exclude = ['id', 'sample']

    ## track history
    history = HistoricalRecords(
        table_name='history_library'
        )

    ## Taggit
    projects = TaggableManager(
        verbose_name="Project",
        help_text="A comma-separated list of project names.",
        blank=True
        )

    ## database relationships
    sample = models.ForeignKey(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    # sample_id = create_chrfield("Sample ID", blank=False)
    pool_id = create_chrfield("Chip ID", blank=False)
    jira_ticket = create_chrfield("Jira ticket", blank=False)
    num_sublibraries = create_intfield("Number of sublibraries", default=0)
    description = create_textfield("Description")
    relates_to = models.ManyToManyField(
        "self",
        verbose_name="Relates to",
        null=True,
        blank=True,
        )

    def get_absolute_url(self):
        return reverse("core:library_detail", kwargs={"pk": self.pk})

    def get_library_id(self):
        return '_'.join([self.sample.sample_id, self.pool_id])

    def __str__(self):
        return 'LIB_' + self.get_library_id()


class SublibraryInformation(models.Model, FieldValue):

    """
    Sublibrary Information from the SmartChipApp output file.
    It's technically a table of cell information.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    ## track history
    # history = HistoricalRecords(
    #     table_name='history_sublibrary_information'
    #     )

    ## database relationships
    library = models.ForeignKey(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE
        )

    ## fields
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
    spot_class = create_chrfield("Spot_Class")
    index_i7 = create_chrfield("Index_I7")
    primer_i7 = create_chrfield("Primer_I7")
    index_i5 = create_chrfield("Index_I5")
    primer_i5 = create_chrfield("Primer_I5")
    pick_met = create_chrfield("Pick_Met")
    spot_well = create_chrfield("Spot_Well")
    num_drops = create_intfield("Num_Drops")

    def get_sublibrary_id(self):
        #add leading zero to one digit row/col
        row = str(self.row) if self.row > 9 else '0' + str(self.row)
        col = str(self.column) if self.column > 9 else '0' + str(self.column)
        res = '_'.join(
            [
                self.library.sample.sample_id,
                self.library.pool_id,
                row + col,
            ]
            )
        return res

    def __str__(self):
        return self.get_sublibrary_id()


class LibrarySampleDetail(models.Model, FieldValue):

    """
    Library sample details.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    ## track history
    # history = HistoricalRecords(
    #     table_name='history_library_sample_detail'
    #     )

    ## database relationships
    library = models.OneToOneField(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    ## choices 
    cell_state_choices = (
        ('C','Cells'),
        ('N','Nuclei'),
        ('M','Mixed'),
        ('U','Unknown'),
        )

    spotting_location_choices = (
        ('A','Aparicio Lab'),
        ('H','Huntsman Lab'),
        ('G','GSC'),
        )

    ## fields
    cell_state = create_chrfield(
        "Cell state",
        choices=cell_state_choices
        )
    estimated_percent_viability = create_intfield(
        "Estimated percent viability",
        )
    label_of_original_sample_vial = create_chrfield(
        "Label of original sample vial"
        )
    original_storage_temperature = create_intfield(
        "Original storage temperature (C)",
        )
    passage_of_cell_line  = create_intfield("Passage")
    sample_notes = create_textfield(
        "Sample notes",
        max_length=1000
        )
    sample_preparation_method = create_textfield(
        "Sample preparation method",
        max_length=1000
        )
    sample_preservation_method = create_chrfield("Sample preservation method")
    sample_spot_date = models.DateField(
        "Sample spot date",
        null=True,
        blank=True,
        )
    spotting_location = create_chrfield(
        "Spotting location",
        choices=spotting_location_choices
        )


class LibraryConstructionInformation(models.Model, FieldValue):

    """
    Library construction information.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    ## track history
    # history = HistoricalRecords(
    #     table_name='history_library_construction_information'
    #     )

    ## database relationships
    library = models.OneToOneField(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    ## choices 
    chip_format_choices = (
        ('W','Wafergen'),
        ('M','Microfluidic'),
        ('B','Bulk'),
        ('O','Other'),
        )

    spotting_location_choices = (
        ('A','Aparicio Lab'),
        ('H','Huntsman Lab'),
        ('G','GSC'),
        )

    ## fields
    chip_format = create_chrfield(
        "Chip format",
        choices=chip_format_choices,
        default="W"
        )
    library_construction_method = create_chrfield(
        "Library construction method",
        default="Nextera (Illumina)"
        )
    library_type = create_chrfield(
        "Library type",
        default="genome"
        )
    library_notes = create_textfield(
        "Library notes",
        max_length=1000
        )
    library_prep_date = models.DateField(
        "Library prep date",
        null=True,
        blank=True,
        )
    number_of_pcr_cycles = create_intfield(
        "Number of PCR cycles",
        default=11
        )
    protocol = create_textfield(
        "Protocol",
        max_length=1000
        )
    spotting_location = create_chrfield(
        "Spotting location",
        choices=spotting_location_choices
        )


class LibraryQuantificationAndStorage(models.Model, FieldValue):

    """
    Library quantification and storage.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    ## track history
    # history = HistoricalRecords(
    #     table_name='history_library_quantification_and_storage'
    #     )

    ## database relationships
    library = models.OneToOneField(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    ## choices
    qc_check_choices = (
        ('P','Will sequence'),
        ('N','Will not sequence'),
        )

    library_location_choices = (
        ('C', 'CRC UL1 Rack 6-2'),
        ('G', 'GSC'),
        ('U', 'UBC')
        )

    ## fields
    average_size = create_intfield("Average size (bp)")
    dna_concentration_nm = models.DecimalField(
        "DNA concentration (nM)",
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True
        )
    dna_concentration_ngul = models.DecimalField(
        "DNA concentration (ng/uL)",
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True
        )
    dna_volumne = create_chrfield("DNA volume (uL)")
    library_location = create_chrfield(
        "Library location",
        choices=library_location_choices
        )
    box = create_intfield("Box")
    box_location = create_intfield("Box location")
    library_tube_label = create_chrfield("Library tube label")
    qc_check = create_chrfield(
        "QC check",
        choices=qc_check_choices
        )
    qc_notes = create_textfield("QC notes")
    quantification_method = create_chrfield(
        "Quantification method",
        default="Bioanalyzer"
        )
    size_range = create_chrfield("Size range (bp)")
    size_selection_method = create_chrfield(
        "Size selection method",
        default="AmpureXP"
        )
    storage_medium = create_chrfield(
        "Storage medium", 
        default="TE 10:0.1"
        )
    agilent_bioanalyzer_xad = models.FileField(
        "Agilent bioanalyzer xad file",
        upload_to=upload_path,
        max_length=200,
        null=True,
        blank=True
        )
    agilent_bioanalyzer_png = models.FileField(
        "Agilent bioanalyzer png file",
        upload_to=upload_path,
        max_length=200,
        null=True,
        blank=True
        )


#============================
# Sequencing models
#----------------------------
class Sequencing(models.Model, FieldValue):

    """
    Sequencing information.
    """

    fields_to_exclude = ['ID', 'Library', 'Chip ID']
    values_to_exclude = ['id', 'library', 'pool_id']

    ## track history
    history = HistoricalRecords(
        table_name='history_sequencing'
        )

    ## database relationships
    library = models.ForeignKey(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE,
        )

    ## choices 
    sequencing_instrument_choices = (
        ('HX','HiSeqX'),
        ('H2500','HiSeq2500'),
        ('N550','NextSeq550'),
        ('MI','MiSeq'),
        ('O','other'),
        )

    sequencing_output_mode_choices = (
        ('L','Low'),
        ('M','Medium'),
        ('H','High'),
        )

    read_type_choices = (
        ('P', 'PET'),
        ('S', 'SET')
        )

    ## fields
    pool_id = create_chrfield("Chip ID")

    adapter = create_chrfield(
        "Adapter",
        default="CTGTCTCTTATACACATCT"
        )
    format_for_data_submission = create_chrfield(
        "Format for data dissemination",
        default="fastq"
        )
    index_read_type = create_chrfield(
        "Index read type",
        default="on 2nd and 3rd index-specific read"
        )
    index_read1_length = create_intfield(
        "Index read1 length",
        default=6
        )
    index_read2_length = create_intfield(
        "Index read2 length",
        default=6
        )
    read_type = create_chrfield(
        "Read type",
        choices=read_type_choices,
        default="P"
        )
    read1_length = create_intfield(
        "Read1 length",
        default=125,
        )
    read2_length = create_intfield(
        "Read2 length",
        default=125
        )
    sequencing_goal = create_chrfield("Sequencing goal (# lanes)")
    sequencing_instrument = create_chrfield(
        "Sequencing instrument",
        choices=sequencing_instrument_choices,
        default="H2500"
        )
    sequencing_output_mode = create_chrfield(
        "Sequencing output mode",
        choices=sequencing_output_mode_choices,
        # default="Low"
        )
    short_description_of_submission = create_chrfield(
        "Short description of submission",
        max_length=150
        )
    submission_date = models.DateField(
        "Submission date",
        null=True,
        blank=True,
        )
    relates_to = models.ManyToManyField(
        "self",
        verbose_name="Relates to",
        null=True,
        blank=True,
        )

    objects = SequencingManager()

    def has_sequencing_detail(self):
        return hasattr(self,
            'sequencingdetail')

    def get_absolute_url(self):
        return reverse("core:sequencing_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return 'SEQ_' + self.library.get_library_id()


class SequencingDetail(models.Model, FieldValue):

    """
    Sequencing details.
    """

    fields_to_exclude = ['ID', 'Sequencing']
    values_to_exclude = ['id', 'sequencing']

    ## track history
    # history = HistoricalRecords(
    #     table_name='history_sequencing_detail'
    #     )

    ## database relationships
    sequencing = models.OneToOneField(
        Sequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
        null=True,
        )

    ## fields
    flow_cell_id = create_chrfield("Flow cell/Lane ID")
    gsc_library_id = create_chrfield("GSC library ID")
    # lane_id = create_chrfield("Lane ID")
    path_to_archive = create_chrfield(
        "Path to archive",
        max_length=150
        )
    sequencer_id = create_chrfield("Sequencer ID")
    sequencing_center = create_chrfield(
        "Sequencing center",
        default="BCCAGSC"
        )
    sequencer_notes = create_textfield("Sequencing notes")
