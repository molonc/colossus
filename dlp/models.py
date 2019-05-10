import datetime

from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.db import models
from core.helpers import *
from core.constants import *
from core.models import SequencingManager


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
        'core.Project',
        verbose_name="Project",
        blank=True
    )

    # related sample
    sample = models.ForeignKey(
        'core.Sample',
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
        'tenx.TenxLibrary',   # TenxLibrary hasn't been seen yet
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
        'core.Analysis',
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