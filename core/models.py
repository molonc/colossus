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
from django.core.urlresolvers import reverse
from django.db import models
from django.core.validators import RegexValidator


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

# register taggit for tracking its history
register(Tag)


#============================
# helpers
#----------------------------
class SequencingManager(models.Manager):
    def with_data(self):
        return [obj for obj in self.get_queryset() if obj.library.is_sequenced()]


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
        ('U', 'Unknown'),
    )

    tissue_type_choices = (
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

    # fields
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

    def __str__(self):
        res = '_'.join([self.sample.sample_id, 'additional_information'])
        return res


#============================
# Library models
#----------------------------
class Library(models.Model, FieldValue, LibraryAssistant):

    """
    Library base class.
    """

    class Meta:
        abstract = True

    fields_to_exclude = ['ID', 'Primary Sample']
    values_to_exclude = ['id', 'primary sample']

    # taggit
    projects = TaggableManager(
        verbose_name="Project",
        help_text="A comma-separated list of project names.",
        blank=True,
    )

    # database relationships
    sample = models.ForeignKey(
        Sample,
        verbose_name="Primary Sample",
        on_delete=models.CASCADE,
    )

    # fields
    description = create_textfield("Description")
    result = create_textfield("Result")

    def __str__(self):
        return 'LIB_' + self.get_library_id()

    def get_absolute_url(self):
        return reverse(self.library_type + ":library_detail", kwargs={"pk": self.pk})


class DlpLibrary(Library):

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
        blank=False,
    )
    num_sublibraries = create_intfield(
        "Number of sublibraries",
        default=0,
    )
    relates_to = models.ManyToManyField(
        "self",
        verbose_name="Relates to",
        blank=True,
    )
    title = create_textfield("Title")
    quality = models.DecimalField("Quality", max_digits=10, decimal_places=2, default=0.75)

    def get_library_id(self):
        return '_'.join([self.sample.sample_id, self.pool_id])

    def has_sublibrary_info(self):
        return self.sublibraryinformation_set.exists()


class PbalLibrary(Library):

    """
    PBAL library contains several Cell objects.
    """

    class Meta:
        ordering = ['sample']

    library_type = 'pbal'

    # track history
    history = HistoricalRecords(table_name='pbal_history_library')

    # fields
    relates_to = models.ManyToManyField(
        DlpLibrary,
        verbose_name="Relates to",
        blank=True,
    )

    def get_library_id(self):
        return '_'.join([self.sample.sample_id])


class TenxLibrary(Library):

    """
    10x library contains several Cell objects.
    """

    class Meta:
        ordering = ['sample']

    library_type = 'tenx'

    # track history
    history = HistoricalRecords(table_name='tenx_history_library')

    # fields
    jira_ticket = create_chrfield(
        "Jira ticket",
        blank=False,
    )
    num_sublibraries = create_intfield(
        "Number of sublibraries",
        default=0,
    )
    relates_to = models.ManyToManyField(
        DlpLibrary,
        verbose_name="Relates to",
        blank=True,
    )

    def get_library_id(self):
        return '_'.join([self.sample.sample_id])


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

    def __str__(self):
        return "{}".format(self.region_code)


class SublibraryInformation(models.Model, FieldValue):

    """
    Sublibrary Information from the SmartChipApp output file.
    It's technically a table of cell information. DLP only.
    """

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


class LibrarySampleDetail(models.Model, FieldValue):

    """
    Library sample detail base class.
    """

    class Meta:
        abstract = True

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    # choices
    cell_state_choices = (
        ('C','Cells'),
        ('N','Nuclei'),
        ('M','Mixed'),
        ('U','Unknown'),
    )

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


class DlpLibrarySampleDetail(LibrarySampleDetail):

    """
    DLP library sample details.
    """

    # database relationships
    library = models.OneToOneField(
        DlpLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    spotting_location_choices = (
        ('AD','Aparicio Lab - Deckard'),
        ('AR','Aparicio Lab - Rachael'),
        ('H','Hansen Lab'),
        ('G','GSC'),
    )

    # fields
    sample_spot_date = models.DateField(
        "Sample spot date",
        null=True,
        blank=True,
    )
    spotting_location = create_chrfield(
        "Spotting location",
        choices=spotting_location_choices,
    )


class PbalLibrarySampleDetail(LibrarySampleDetail):

    """
    PBAL library sample details.
    """

    # database relationships
    library = models.OneToOneField(
        PbalLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    spotting_location_choices = (
        ('AD','Aparicio Lab - Deckard'),
        ('AR','Aparicio Lab - Rachael'),
        ('H','Hansen Lab'),
        ('G','GSC'),
        ('T', 'TFL flow facility'),
    )

    # fields
    sample_spot_date = models.DateField(
        "Sample spot date",
        null=True,
        blank=True,
    )
    spotting_location = create_chrfield(
        "Spotting location",
        choices=spotting_location_choices,
    )


class TenxLibrarySampleDetail(LibrarySampleDetail):

    """
    10x library sample details.
    """

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


class LibraryConstructionInformation(models.Model, FieldValue):

    """
    Library construction information base class.
    """

    class Meta:
        abstract = True

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']


class DlpLibraryConstructionInformation(LibraryConstructionInformation):

    """
    DLP library construction information.
    """

    # database relationships
    library = models.OneToOneField(
        DlpLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # choices
    chip_format_choices = (
        ('W','Wafergen'),
        ('M','Microfluidic'),
        ('B','Bulk'),
        ('O','Other'),
    )

    spotting_location_choices = (
        ('AD','Aparicio Lab - Deckard'),
        ('AR','Aparicio Lab - Rachael'),
        ('H','Hansen Lab'),
        ('G','GSC'),
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


class PbalLibraryConstructionInformation(LibraryConstructionInformation):

    """
    PBAL library construction information.
    """

    # database relationships
    library = models.OneToOneField(
        PbalLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # fields
    format = create_chrfield(
        "Format",
        default="384-well plate",
    )
    library_construction_method = create_chrfield(
        "Library construction method",
        default="pbal",
    )
    library_type = create_chrfield(
        "Library type",
        default="methylome",
    )
    submission_date = models.DateField(
        "Submission date",
        null=True,
        blank=True,
    )
    library_prep_location = create_chrfield(
        "Library prep location",
        default="Hirst Lab",
    )


class TenxLibraryConstructionInformation(LibraryConstructionInformation):

    """
    10x library construction information.
    """

    # database relationships
    library = models.OneToOneField(
        TenxLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # choices
    chip_format_choices = (
        ('W','Wafergen'),
        ('M','Microfluidic'),
        ('B','Bulk'),
        ('O','Other'),
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


class LibraryQuantificationAndStorage(models.Model, FieldValue):

    """
    Library quantification and storage base class.
    """

    class Meta:
        abstract = True

    # choices
    qc_check_choices = (
        ('P','Will sequence'),
        ('N','Will not sequence'),
    )

    # fields
    qc_check = create_chrfield(
        "QC check",
        choices=qc_check_choices,
    )
    qc_notes = create_textfield("QC notes")


class DlpLibraryQuantificationAndStorage(LibraryQuantificationAndStorage):

    """
    DLP library quantification and storage.
    """

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
        upload_to=upload_path,
        max_length=200,
        null=True,
        blank=True,
    )
    agilent_bioanalyzer_image = models.FileField(
        "Agilent bioanalyzer image file",
        upload_to=upload_path,
        max_length=200,
        null=True,
        blank=True,
    )

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


class PbalLibraryQuantificationAndStorage(LibraryQuantificationAndStorage):

    """
    PBAL library quantification and storage.
    """

    fields_to_exclude = ['ID', 'Library']

    values_to_exclude = ['id', 'library']

    # database relationships
    library = models.OneToOneField(
        PbalLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )


class TenxLibraryQuantificationAndStorage(LibraryQuantificationAndStorage):

    """
    10x library quantification and storage.
    """

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


#============================
# Sequencing models
#----------------------------
class Sequencing(models.Model, FieldValue):

    """
    Sequencing information base class.
    """

    class Meta:
        abstract = True

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    # choices
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
        ('S', 'SET'),
    )

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
    sequencing_goal = create_chrfield("Sequencing goal (# lanes)")
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

    objects = SequencingManager()

    def __str__(self):
        return 'SEQ_' + self.library.get_library_id() +"_" + str(self.id)

    def has_sequencing_detail(self):
        return hasattr(self, self.library_type + 'sequencingdetail')

    def get_absolute_url(self):
        return reverse(self.library_type + ":sequencing_detail", kwargs={"pk": self.pk})


class DlpSequencing(Sequencing):

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


class PbalSequencing(Sequencing):

    """
    PBAL sequencing information.
    """

    library_type = 'pbal'

    # track history
    history = HistoricalRecords(table_name='pbal_history_sequencing')

    # database relationships
    library = models.ForeignKey(
        PbalLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
    )

class TenxSequencing(Sequencing):

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
    )


class SequencingDetail(models.Model, FieldValue):

    """
    Sequencing details base class.
    """

    class Meta:
        abstract = True

    fields_to_exclude = ['ID', 'Sequencing']
    values_to_exclude = ['id', 'sequencing']
    SEQ_CENTER = (
        ('BCCAGSC', 'BCCAGSC'),
        ('UBCBRC', 'UBCBRC'),
    )

    # fields
    gsc_library_id = create_chrfield("GSC library ID")
    sequencer_id = create_chrfield("Sequencer ID")
    sequencing_center = create_chrfield(
        "Sequencing center",
        choices=SEQ_CENTER,
        default='BCCAGSC',
        blank=False
    )
    sequencer_notes = create_textfield("Sequencing notes")


class DlpSequencingDetail(SequencingDetail):

    """
    DLP sequencing details.
    """

    # database relationships
    sequencing = models.OneToOneField(
        DlpSequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
        null=True,
    )

    # fields
    rev_comp_override_choices = (
        ('i7,i5', 'No Reverse Complement'),
        ('i7,rev(i5)', 'Reverse Complement i5'),
        ('rev(i7),i5', 'Reverse Complement i7'),
        ('rev(i7),rev(i5)', 'Reverse Complement i7 and i5'),
    )

    rev_comp_override = create_chrfield(
        "Reverse Complement Override",
        choices=rev_comp_override_choices,
        default=None,
        null=True,
    )


class PbalSequencingDetail(SequencingDetail):

    """
    PBAL sequencing details.
    """

    # database relationships
    sequencing = models.OneToOneField(
        PbalSequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
        null=True,
    )


class TenxSequencingDetail(SequencingDetail):

    """
    10x sequencing details.
    """

    # database relationships
    sequencing = models.OneToOneField(
        TenxSequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
        null=True,
    )


class Lane(models.Model, FieldValue):

    """
    Lane information base class.
    """

    class Meta:
        abstract = True

    fields_to_exclude = ['ID', 'Lane']
    values_to_exclude = ['id', 'lane']

    flow_cell_id = create_chrfield(
        "Flow cell/Lane ID",
        null=False,
        blank=False,
    )

    path_to_archive = create_chrfield(
        "Path to archive",
        blank=False,
        max_length=150
    )

    def __str__(self):
        return self.flow_cell_id


class DlpLane(Lane):

    """
    Dlp lane information.
    """

    # database relationships
    sequencing = models.ForeignKey(
        DlpSequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
    )


class PbalLane(Lane):

    """
    PBAL lane information.
    """

    # database relationships
    sequencing = models.ForeignKey(
        PbalSequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
    )


class TenxLane(Lane):

    """
    10x lane information.
    """

    # database relationships
    sequencing = models.ForeignKey(
        TenxSequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
    )


class Plate(models.Model, FieldValue):

    """
    PBAL plate information.
    """

    fields_to_exclude = ['ID', 'Plate']
    values_to_exclude = ['id', 'plate']

    # database relationships
    library = models.ForeignKey(
        PbalLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
    )

    # choices
    plate_type_choices = (
        ('submitted', 'submitted'),
        ('sequenced', 'sequenced'),
        ('stored', 'stored'),
    )

    # fields
    jira_ticket = create_chrfield(
        "Jira ticket",
        null=False,
        blank=False,
    )
    plate_number = create_intfield("Plate number")
    plate_status = create_chrfield(
        "Plate status",
        choices=plate_type_choices,
    )
    plate_location = create_textfield("Plate location")
