import datetime

from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.db import models

from core.helpers import *
from core.constants import *
from core.models import Sample, Project


class TenxChip(models.Model, FieldValue):

    # Chip Model for TenX Libraries
    history = HistoricalRecords(table_name='tenx_history_chip')

    class Meta:
        ordering = ['-id']

    LAB_NAMES = (
        ("SA", "Sam Aparicio"),
        ("DH", "David Huntsman"),
    )

    lab_name = create_chrfield(
        "Lab Name",
        default="SA",
        choices=LAB_NAMES,
        blank=True,
    )

    #TenXLibrary name depend on below methods, so please be mindful when making changes
    def get_id(self):
        return "CHIP" + format(self.id, "04")

    def __str__(self):
        return self.get_id() + "_" + self.lab_name

    def get_absolute_url(self):
        return reverse("tenx" + ":chip_detail", kwargs={"pk": self.pk})

    def get_sample_list(self):
        return set(t.sample.sample_id for t in self.tenxlibrary_set.all()) if self.tenxlibrary_set.all() else []


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
        null=True,
    )

    chip_well = models.IntegerField(default=0, choices=CHIP_WELL)

    google_sheet = create_chrfield(
        "Google Sheet Link",
        null=True,
        blank=True,
        max_length=255,
    )

    gsc_library_id = create_chrfield(
        "GSC Library ID",
        blank=True,
        null=True,
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
        blank=True,
    )

    # related sample
    sample = models.ForeignKey(
        Sample,
        verbose_name="Primary Sample",
        on_delete=models.CASCADE,
    )

    # related libraries
    relates_to_dlp = models.ManyToManyField(
        'dlp.DlpLibrary', # DlpLibrary hasn't been seen yet
        verbose_name="Relates to (DLP)",
        blank=True,
    )
    relates_to_tenx = models.ManyToManyField(
        'TenxLibrary', # TenxLibrary hasn't been seen yet
        verbose_name="Relates to (Tenx)",
        blank=True,
    )

    # fields
    description = create_textfield("Description", max_length=1024)
    result = create_textfield("Result")

    failed = models.BooleanField("Failed", default=False, blank=False)

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse(self.library_type + ":library_detail", kwargs={"pk": self.pk})


class TenxPool(models.Model, FieldValue):
    LOCATION = (
        ('BCCAGSC', 'GSC'),
        ('UBCBRC', 'UBC'),
    )

    pool_name = create_chrfield(
        "Pool Name",
        null=True,
        blank=True,
    )
    gsc_pool_name = create_chrfield(
        "GSC Pool Name",
        null=True,
        blank=True,
    )
    construction_location = create_chrfield(
        "Construction Location",
        choices=LOCATION,
        null=True,
        blank=True,
    )
    constructed_by = create_chrfield(
        "Constructed By",
        null=True,
        blank=True,
    )
    constructed_date = models.DateField(
        "Construction Date",
        null=True,
        blank=True,
    )
    libraries = models.ManyToManyField(TenxLibrary)

    def __str__(self):
        return self.pool_name

    def get_sample_list(self):
        return set(t.sample.sample_id for t in self.libraries.all()) if self.libraries.all() else []

    def get_library_ids(self):
        return [l.id for l in self.libraries.all()]

    def jira_tickets(self):
        jira_tickets = []
        sample_ids = []
        for l in self.libraries.all():
            if l.jira_ticket:
                jira_tickets.append(l.jira_ticket)
                sample_ids.append(l.sample.sample_id)
        return jira_tickets, sample_ids

    def get_absolute_url(self):
        return reverse("tenx" + ":pool_detail", kwargs={"pk": self.pk})


class TenxAnalysis(models.Model, FieldValue):
    class Meta:
        ordering = ['id']

    input_type = create_chrfield(
        "Input Type",
        choices=INPUT_TYPE,
        null=False,
    )
    version = create_chrfield(
        "Analysis Version",
        blank=False,
    )
    jira_ticket = create_chrfield(
        "Analysis Jira Ticket",
        blank=False,
    )
    run_status = create_chrfield(
        "Run Status",
        blank=False,
        null=False,
        default=IDLE,
        choices=RUN_STATUS_CHOICES,
    )

    last_updated_date = models.DateTimeField("Last Updated Date", auto_now=True)
    submission_date = models.DateField(
        "Analysis Submission Date",
        default=datetime.date.today, # this needs to be a date (not datetime)
    )

    description = create_textfield("Description")
    tenx_library = models.ForeignKey('tenx.TenxLibrary', null=True)
    tenx_lanes = models.ManyToManyField('tenx.TenxLane', blank=True)

    def __str__(self):
        res = str(self.id).zfill(3) + "_ANALYSIS"
        return res

    def get_absolute_url(self):
        return reverse("tenx:tenxanalysis_detail", kwargs={"pk": self.pk})


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
        default=datetime.date.today,
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
    passage_of_cell_line = create_intfield("Passage")
    sample_notes = create_textfield("Sample notes")
    sample_preparation_method = create_textfield("Sample preparation method")
    sample_preservation_method = create_chrfield("Sample preservation method")


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
    submission_date = models.DateField(
        "Library Prep Date",
        null=True,
        blank=True,
    )
    library_prep_location = create_chrfield(
        "Library prep location",
        default="BCCRC",
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
        default="3'",
        verbose_name="Library type",
    )

    index_used = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        choices=TENX_INDEX_CHOICES,
        verbose_name="Index used",
    )

    chemistry_version = models.CharField(
        null=True,
        choices=CHEMISTRY_VERSION_CHOICES,
        verbose_name="Chemistry Version",
        max_length=150,
        default="VERSION_3",
    )


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
        null=True,
        blank=True,
    )

    tenx_pool = models.ForeignKey(
        TenxPool,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
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
        default=datetime.date.today,
    )

    sequencer_id = create_chrfield("Sequencer ID")
    sequencing_center = create_chrfield(
        "Sequencing center",
        choices=SEQ_CENTER,
        default='BCCAGSC',
        blank=False,
    )
    sequencer_notes = create_textfield("Sequencing notes", )

    tenx_analysis = models.ManyToManyField(
        TenxAnalysis,
        verbose_name="Tenx Analysis",
        blank=True,
    )

    gsc_library_id = create_chrfield(
        "GSC Library ID",
        blank=True,
        null=True,
    )

    number_of_lanes_requested = models.PositiveIntegerField(
        default=1,
        verbose_name="Sequencing Goal",
    )

    # Set to the last time number_of_lanes_requested was updated
    lane_requested_date = models.DateField(null=True, )

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

    tantalus_datasets = ArrayField(
        models.IntegerField(null=True, blank=True),
        null=True,
        blank=True,
    )

    gsc_sublibrary_names = ArrayField(models.CharField(
        null=True,
        blank=True,
        max_length=10,
    ), null=True, blank=True)

    sequencing_date = models.DateTimeField(null=True)

    def get_library_from_sublibrary(self):
        sublib_to_lib_map = dict()
        if self.gsc_sublibrary_names:
            for sublib in self.gsc_sublibrary_names:
                try:
                    library = TenxLibrary.objects.get(gsc_library_id=sublib)
                except:
                    library = None

                sublib_to_lib_map[sublib] = library

        return sublib_to_lib_map

    def __str__(self):
        return self.flow_cell_id


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

    dna_concentration_nm = models.IntegerField(
        "DNA Concentration(nM)",
        null=True,
        blank=True,
    )
    dna_concentration_ng = models.IntegerField(
        "DNA Concentration(ng/uL)",
        null=True,
        blank=True,
    )
    dna_concentration_bp = models.IntegerField(
        "DNA Concentration(bp)",
        null=True,
        blank=True,
    )
