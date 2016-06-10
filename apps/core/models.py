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
# 3rd-party app imports
#----------------------------
from taggit.managers import TaggableManager


#============================
# helpers
#----------------------------
def create_chrfield(name, max_length=50, blank=True, null=True, **kwargs):
    """wrap models.CharField for ease of use."""
    return models.CharField(
        name,
        max_length=max_length,
        blank=blank,
        null=null,
        **kwargs
        )



def create_textfield(name, max_length=200, blank=True, null=True, **kwargs):
    """wrap models.TextField for ease of use."""
    return models.TextField(
        name,
        max_length=max_length,
        blank=blank,
        null=null,
        **kwargs
        )


def create_intfield(name, blank=True, null=True, **kwargs):
    """wrap models.IntegerField for ease of use."""
    return models.IntegerField(
        name,
        blank=blank,
        null=null,
        **kwargs
        )


class FieldValue(object):
    fields_to_exclude = ['ID']
    values_to_exclude = ['id']
    model = models.Model

    def get_fields(self):
        """get verbose names of all the fields."""
        field_names = [f.verbose_name for f in self._meta.fields
                       if f.verbose_name not in self.fields_to_exclude]
        return field_names

    def get_values(self):
        """get values of all the fields."""
        fields = [field.name for field in self._meta.fields]
        values = []
        for f in fields:
            if f not in self.values_to_exclude:
                a = "get_%s_display" % (f)
                if hasattr(self, a):
                    values.append(getattr(self, a)())
                else:
                    values.append(getattr(self, f))
        return values


#============================
# Sample models
#----------------------------
class Sample(models.Model, FieldValue):

    """
    Base class of different sample types.
    """

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
        "Sample Type",
        choices=sample_type_choices
        )
    anonymous_patient_id = create_chrfield("Anonymous Patient ID")
    cell_line_id = create_chrfield("Cell Line ID")
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

    ## database relationships
    sample = models.OneToOneField(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    ## choices 
    disease_condition_health_status_choices = (
        ('H','Healthy'),
        ('C','Cystic Fibrosis'),
        ('B','Breast Cancer'),
        )

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
        "Disease Condition/Health Status",
        choices=disease_condition_health_status_choices,
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
    anatomic_site = create_chrfield("Anatomic Site")
    anatomic_sub_site = create_chrfield("Anatomic Sub-Site")
    developmental_stage = create_chrfield("Developmental Stage")
    tissue_type = create_chrfield(
        "Tissue Type",
        choices=tissue_type_choises
        )
    cell_type = create_chrfield("Cell Type")
    pathology_disease_name = create_chrfield("Pathology/Disease Name")
    additional_pathology_info = create_chrfield(
        "Additional Pathology Information"
        )
    grade = create_chrfield("Grade")
    stage = create_chrfield("Stage")
    tumour_content = create_chrfield("Tumor content (%)")
    pathology_occurrence = create_chrfield(
        "Pathology Occurrence",
        choices=pathology_occurrence_choices
        )
    treatment_status = create_chrfield(
        "Treatment Status",
        choices=treatment_status_choices
        )
    family_information = create_chrfield("Family Information")

    def __str__(self):
        res = '_'.join([
            self.sample.sample_id,
            'additional_information'
            ])
        return res


#============================
# Library models
#----------------------------
class Library(models.Model, FieldValue):

    """
    Library contains several Cell objects.
    """

    fields_to_exclude = ['ID', 'Sample']
    values_to_exclude = ['id', 'sample']

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
    pool_id = create_chrfield("Pool ID", blank=False)
    jira_ticket = create_chrfield("Jira Ticket", blank=False)
    num_sublibraries = create_intfield("Number of Sublibraries", default=0)
    description = create_textfield("Description")

    def has_library_sample_detail(self):
        return hasattr(self,
            'librarysampledetail')

    def has_library_construction_information(self):
        return hasattr(self,
            'libraryconstructioninformation'
            )

    def has_library_quantification_and_storage(self):
        return hasattr(self,
            'libraryquantificationandstorage'
            )

    def get_absolute_url(self):
        return reverse("core:library_detail", kwargs={"pk": self.pk})

    def get_library_id(self):
        return '_'.join([self.sample.sample_id, self.pool_id])

    def __str__(self):
        return self.get_library_id()


class SublibraryInformation(models.Model, FieldValue):

    """
    Sublibrary Information from the SmartChipApp output file.
    It's technically a table of cell information.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

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
        res = '_'.join(
            [
                self.library.sample.sample_id,
                self.library.pool_id,
                str(self.row) + str(self.column),
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
    passage_of_cell_line  = create_intfield("Passage of cell line")
    sample_notes = create_textfield("Sample notes")
    sample_preparation_method = create_textfield(
        "Sample preparation method"
        )
    sample_preservation_method = create_chrfield("Sample preservation method")


class LibraryConstructionInformation(models.Model, FieldValue):

    """
    Library construction information.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

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

    ## fields
    chip_format = create_chrfield(
        "Chip format",
        choices=chip_format_choices,
        default="W"
        )
    library_construction_method = create_chrfield(
        "Library Construction Method",
        default="Nextera (Illumina)"
        )
    library_type = create_chrfield(
        "Library Type",
        default="genome"
        )
    library_notes = create_textfield("Library notes")
    library_prep_date = models.DateField(
        "Library prep date",
        null=True,
        blank=True,
        )
    number_of_pcr_cycles = create_intfield(
        "Number of PCR cycles",
        default=11
        )
    protocol = create_textfield("Protocol")
    sample_spot_date = models.DateField(
        "Sample spot date",
        null=True,
        blank=True,
        )


class LibraryQuantificationAndStorage(models.Model, FieldValue):

    """
    Library quantification and storage.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

    ## database relationships
    library = models.OneToOneField(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    ## fields
    average_size = create_intfield("Average size (bp)")
    dna_concentration_nm = create_intfield("DNA concentration (nM)")
    dna_concentration_ngul = create_intfield("DNA concentration (ng/uL)")
    dna_volumne = create_chrfield("DNA volume (uL)")
    library_location = create_chrfield("Library location")
    library_tube_label = create_chrfield("Library tube label")
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


#============================
# Sequencing models
#----------------------------
class Sequencing(models.Model, FieldValue):

    """
    Sequencing information.
    """

    fields_to_exclude = ['ID', 'Library']
    values_to_exclude = ['id', 'library']

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

    read_type_choices = (
        ('P', 'PET'),
        ('S', 'SET')
        )

    ## fields
    pool_id = create_chrfield("Pool ID")

    adapter = create_chrfield(
        "Adapter",
        default="CTGTCTCTTATACACATCT"
        )
    format_for_data_submission = create_chrfield(
        "Format for data dissemination",
        default="fastq"
        )
    index_read_type = create_chrfield(
        "Index Read Type",
        default="on 2nd and 3rd index-specific read"
        )
    index_read1_length = create_intfield(
        "Index Read1 Length",
        default=6
        )
    index_read2_length = create_intfield(
        "Index Read2 Length",
        default=6
        )
    read_type = create_chrfield(
        "Read type",
        choices=read_type_choices,
        default="P"
        )
    read1_length = create_intfield(
        "Read1 Length",
        default=125,
        )
    read2_length = create_intfield(
        "Read2 Length",
        default=125
        )
    sequencing_goal = create_chrfield("Sequencing Goal (# lanes)")
    sequencing_instrument = create_chrfield(
        "Sequencing instrument",
        choices=sequencing_instrument_choices,
        default="H2500"
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

    def has_sequencing_detail(self):
        return hasattr(self,
            'sequencingdetail')

    def get_absolute_url(self):
        return reverse("core:sequencing_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.library.get_library_id()


class SequencingDetail(models.Model, FieldValue):

    """
    Sequencing details.
    """

    fields_to_exclude = ['ID', 'Sequencing']
    values_to_exclude = ['id', 'sequencing']

    ## database relationships
    sequencing = models.OneToOneField(
        Sequencing,
        verbose_name="Sequencing",
        on_delete=models.CASCADE,
        null=True,
        )

    ## fields
    flow_cell_id = create_chrfield("Flow cell ID")
    gsc_library_id = create_chrfield("GSC library ID")
    lane_id = create_chrfield("Lane ID")
    path_to_archive = create_chrfield("Path to archive")
    sequencer_id = create_chrfield("Sequencer ID")
    sequencing_center = create_chrfield(
        "Sequencing center",
        default="BCCAGSC"
        )
    sequencer_notes = create_textfield("Sequencing notes")


#============================
# Project tag model
#----------------------------
# class Project(models.Model, FieldValue):

#     """
#     Project tag.
#     """

#     ## database relationships
#     libraries = models.ManyToManyField(
#         Library,
#         verbose_name="Library",
#         related_name="projects"
#         )

#     ## fields
#     project_name = create_chrfield("Project")

#     # def get_absolute_url(self):
#     #     return reverse("core:project_detail", kwargs={"pk": self.pk})

#     def __str__(self):
#         return self.project_name


#============================
# Other models
#----------------------------
# class Patient(models.Model, FieldValue):

#     """
#     Patient sample type.
#     """

#     # database relationships
#     sample = models.ForeignKey(
#         Sample,
#         verbose_name="Sample",
#         on_delete=models.CASCADE
#         )

#     library = models.OneToOneField(
#         Library,
#         verbose_name="Library",
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True
#         )

#     additional_pathology_info = create_chrfield(
#         "Additional Pathology Information"
#         )
#     pathology_occurrence = create_chrfield("Pathology Occurrence")
#     pathology_disease_name = create_chrfield("Pathology/Disease Name")
#     stage = create_chrfield("Stage")
#     grade = create_chrfield("Grade")
#     tumour_content = create_chrfield("Tumor content (%)")

#     def __str__(self):
#         return self.sample.sample_id


# class CellLine(models.Model, FieldValue):

#     """
#     CellLine sample type.
#     """

#     # database relationships
#     sample = models.ForeignKey(
#         Sample,
#         verbose_name="Sample",
#         on_delete=models.CASCADE
#         )

#     additional_pathology_info = create_chrfield(
#         "Additional Pathology Information"
#         )
#     pathology_occurrence = create_chrfield("Pathology Occurrence")
#     pathology_disease_name = create_chrfield("Pathology/Disease Name")
#     stage = create_chrfield("Stage")
#     grade = create_chrfield("Grade")
#     tumour_content = create_chrfield("Tumor content (%)")

#     def __str__(self):
#         return self.sample.sample_id

# class Xenograft(models.Model, FieldValue):

#     """
#     Xenograft sample type.
#     """

#     # database relationships
#     sample = models.ForeignKey(
#         Sample,
#         verbose_name="Sample",
#         on_delete=models.CASCADE
#         )

#     def __str__(self):
#         return self.sample.sample_id

# class UST(models.Model, FieldValue):

#     """
#     Undefined Sample type.
#     """

#     # database relationships
#     sample = models.ForeignKey(
#         Sample,
#         verbose_name="Sample",
#         on_delete=models.CASCADE
#         )

#     def __str__(self):
#         return self.samle.sample_id

