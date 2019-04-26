
#============================
# Django imports
#----------------------------
from django.db import models
from django.core.urlresolvers import reverse

#============================
# Core imports
#----------------------------
from core.constants import *
from core.helpers import *
from core.models import (
    Project,
    Sample,
    SequencingManager,
    DlpLibrary,
    Analysis)

from tenx.models import *

#============================
# etc
#----------------------------
from simple_history.models import HistoricalRecords
import datetime

class PbalLibrary(models.Model, FieldValue, LibraryAssistant):

    """
    PBAL library contains several Cell objects.
    """

    class Meta:
        ordering = ['sample']

    library_type = 'pbal'

    # track history
    history = HistoricalRecords(table_name='pbal_history_library')

    def get_library_id(self):
        return '_'.join([self.sample.sample_id])

    fields_to_exclude = ['ID', 'Primary Sample']
    values_to_exclude = ['id', 'primary sample']

    projects = models.ManyToManyField(
        Project,
        related_name="pballibrary_projects",
        verbose_name="Project",
        blank=True
    )

    # related sample
    sample = models.ForeignKey(
        Sample,
        related_name="pballibrary_sample",
        verbose_name="Primary Sample",
        on_delete=models.CASCADE,
    )

    # related libraries
    relates_to_dlp = models.ManyToManyField(
        DlpLibrary,   # DlpLibrary hasn't been seen yet
        related_name="pballibrary_relates_to_dlp",
        verbose_name="Relates to (DLP)",
        blank=True,
    )
    relates_to_tenx = models.ManyToManyField(
        TenxLibrary,   # TenxLibrary hasn't been seen yet
        related_name="pballibrary_relates_to_tenx",
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

class PbalLibrarySampleDetail(models.Model, FieldValue):

    """
    PBAL library sample details.
    """
    spotting_location_choices = (
        ('AD','Aparicio Lab - Deckard'),
        ('AR','Aparicio Lab - Rachael'),
        ('H','Hansen Lab'),
        ('G','GSC'),
        ('T', 'TFL flow facility'),
    )
    history = HistoricalRecords(table_name='pbal_history_library_sample_detail')

    # database relationships
    library = models.OneToOneField(
        PbalLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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

class PbalLibraryConstructionInformation(models.Model, FieldValue):

    """
    PBAL library construction information.
    """


    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    history = HistoricalRecords(table_name='pbal_history_library_construction_information')

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

class PbalLibraryQuantificationAndStorage(models.Model, FieldValue):

    """
    PBAL library quantification and storage.
    """
    history = HistoricalRecords(table_name='pbal_history_library_q_and_s')

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


    # fields
    qc_check = create_chrfield(
        "QC check",
        choices=qc_check_choices,
    )
    qc_notes = create_textfield("QC notes")

class PbalSequencing(models.Model, FieldValue):

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
        super(PbalSequencing, self).__init__(*args, **kwargs)
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
        super(PbalSequencing, self).save(*args,**kwargs)

class PbalLane(models.Model, FieldValue):

    """
    PBAL lane information.
    """
    history = HistoricalRecords(table_name='pbal_history_lane')
    # database relationships
    sequencing = models.ForeignKey(
        PbalSequencing,
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

class Plate(models.Model, FieldValue):

    """
    PBAL plate information.
    """

    history = HistoricalRecords(table_name='pbal_plate_history')

    fields_to_exclude = ['ID', 'Plate']
    values_to_exclude = ['id', 'plate']

    # database relationships
    library = models.ForeignKey(
        PbalLibrary,
        verbose_name="Library",
        on_delete=models.CASCADE,
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