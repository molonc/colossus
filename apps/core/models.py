"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import unicode_literals
from django.db import models
# import functools

# import django.db.models.options as options
# from django.conf import settings
# from django.core.validators import MinValueValidator, MaxValueValidator

#===============================
# helpers
#-------------------------------
def create_chrfield(name, max_length=20, blank=True, **kwargs):
    """wrap models.CharField for ease of use."""
    return models.CharField(name, max_length=max_length, blank=blank, **kwargs)


def create_textfield(name, max_length=200, blank=True, **kwargs):
    """wrap models.TextField for ease of use."""
    return models.TextField(name, max_length=max_length, blank=blank, **kwargs)

def create_intfield(name, blank=True, **kwargs):
    """wrap models.IntegerField for ease of use."""
    return models.IntegerField(name, blank=blank, **kwargs)


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
        values = [getattr(self, f) for f in fields
                  if f not in self.values_to_exclude]
        return values


#===============================
# models
#-------------------------------
class Library(models.Model, FieldValue):

    """
    Library contains several Cell objects.
    """

    sample_id = create_chrfield("Sample ID", blank=False)
    pool_id = create_chrfield("Pool ID", blank=False)
    jira_ticket = create_chrfield("Jira Ticket", blank=False)
    description = create_textfield("Description")
    num_libraries = create_intfield("Number of Libraries", null=True)

    ## fixme: use hasattr() instead.
    def has_sublibrary(self):
        res = True
        try:
            _ = self.sublibrary_information
        except SublibraryInformation.DoesNotExist:
            res = False
        return res

    def get_library_id(self):
        return '_'.join([self.sample_id, self.pool_id])

    def __str__(self):
        return self.get_library_id()

class SublibraryInformation(models.Model, FieldValue):

    """
    Sublibrary Information from the SmartChipApp output file.
    It's technically a table of cell information.
    """

    # fields_to_exclude = ['ID', 'Sublibrary Information']
    # values_to_exclude = ['id', 'sublibrary_info']

    ## database relationships
    library = models.ForeignKey(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE
        )

    ## Character field
    sample_cellcaller = create_chrfield("Sample")
    
    ## Integer fields
    row = create_intfield("Row", null=True)
    col = create_intfield("Column", null=True)
    img_col = create_intfield("Image Column", null=True)
    num_live = create_intfield("Num_Live", null=True)
    num_dead = create_intfield("Num_Dead", null=True)
    num_other = create_intfield("Num_Other", null=True)
    rev_live = create_intfield("Rev_Live", null=True)
    rev_dead = create_intfield("Rev_Dead", null=True)
    rev_other = create_intfield("Rev_Other", null=True)
        
    ## Character fields
    file_ch1 = create_chrfield("File_Ch1")
    file_ch2 = create_chrfield("File_Ch2")
    index_i7 = create_chrfield("Index_I7")
    primer_i7 = create_chrfield("Primer_I7")
    index_i5 = create_chrfield("Index_I5")
    primer_I5 = create_chrfield("Primer_I5")
    pick_met = create_chrfield("Pick_Met")

    def get_sublibrary_id(self):
        res = '_'.join(
            [
                self.library.sample_id,
                self.library.pool_id,
                str(self.row) + str(self.col),
            ]
            )
        return res

    def __str__(self):
        return self.get_sublibrary_id()

class LibrarySampleDetail(models.Model, FieldValue):

    """
    Library sample details.
    """

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
    cell_state = create_chrfield("Cell state", choices=cell_state_choices)
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
    chip_format = create_chrfield("Chip format")
    library_construction_method = create_chrfield(
        "Library Construction Method"
        )
    library_type = create_chrfield("Library Type")
    library_notes = create_textfield("Library notes")
    library_prep_date = models.DateField(
        "Library prep date",
        null=True,
        blank=True,
        )
    number_of_pcr_cycles = create_intfield("Number of PCR cycles")
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
    dna_concentration_ngul = create_chrfield("DNA concentration (ng/uL)")
    dna_volumne = create_chrfield("DNA volume (uL)")
    library_location = create_chrfield("Library location")
    library_tube_label = create_chrfield("Library tube label")
    qc_notes = create_textfield("QC notes")
    quantification_method = create_chrfield("Quantification method")
    size_range = create_chrfield("Size range (bp)")
    size_selection_method = create_chrfield("Size selection method")
    storage_medium = create_chrfield("Storage medium")


class Sequencing(models.Model, FieldValue):

    """
    Sequencing Information.
    """

    ## database relationships
    library = models.OneToOneField(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True
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
    adapter = create_chrfield("Adapter")
    format_for_data_submission = create_chrfield(
        "Format for data dissemination"
        )
    index_read_type = create_chrfield("Index Read Type")
    index_read1_length = create_chrfield("Index Read1 Length")
    index_read2_length = create_chrfield("Index Read2 Length")
    pool_id = create_chrfield("Pool ID")
    read_type = create_chrfield("Read type", choices=read_type_choices)
    read1_length = create_chrfield("Read1 Length")
    read2_length = create_chrfield("Read2 Length")
    sequencing_goal = create_chrfield("Sequencing Goal (# lanes)")
    sequencing_instrument = create_chrfield(
        "Sequencing instrument",
        choices=sequencing_instrument_choices
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

class Sample(models.Model, FieldValue):

    """
    Base class of different sample types.
    """

    # sample_type = None

    ## choices
    sample_type_choices = (
        ('P','Patient'),
        ('C','Cell Line'),
        ('X','Xenograft'),
        ('O','Other'),
        )

    sex_choices = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('mixed', 'Mixed'),
        ('unknown', 'Unknown')
        )

    tissue_type_choises = (
        ('normal', 'Normal'),
        ('benign', 'Benign'),
        ('pre_malignant', 'Pre-malignant'),
        ('malignant', 'Malignant'),
        ('non_neoplastic_disease', 'Non-neoplastic Disease'),
        ('undetermined', 'Undetermined'),
        ('hyperplasia', 'Hyperplasia'),
        ('metaplasia', 'Metaplasia'),
        ('dysplasia', 'Dysplasia'),
        )

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

    ## required fields
    sample_id = create_chrfield("Sample ID", blank=False)

    ## other fields in alphabetical order
    additional_pathology_info = create_chrfield(
        "Additional Pathology Information"
        )
    anatomic_site = create_chrfield("Anatomic Site")
    anatomic_sub_site = create_chrfield("Anatomic Sub-Site")
    anonymou_patient_id = create_chrfield("Anonymous Patient ID")
    cell_line_id = create_chrfield("Cell Line ID")
    cell_type = create_chrfield("Cell Type")
    developmenta_stage = create_chrfield("Developmental Stage")
    disease_condition_health_status = create_chrfield(
        "Disease Condition/Health Status",
        choices=disease_condition_health_status_choices,
        )
    family_information = create_chrfield("Family Information")
    grade = create_chrfield("Grade")
    pathology_occurrence = create_chrfield("Pathology Occurrence")
    pathology_disease_name = create_chrfield("Pathology/Disease Name")
    sample_type = create_chrfield("Sample Type", choices=sample_type_choices)
    sex = create_chrfield("Sex", choices=sex_choices)
    stage = create_chrfield("Stage")
    strain = create_chrfield("Strain")
    taxonomy_id = create_chrfield("Taxonomy ID")
    tissue_type = create_chrfield("Tissue Type", choices=tissue_type_choises)
    treatment_status = create_chrfield("Treatment Status")
    tumour_content = create_chrfield("Tumor content (%)")
    xenograft_id = create_chrfield("Xenograft ID")
    xenograft_biopst_date = models.DateField(
        "Xenograft biopsy date",
        null=True,
        blank=True,
        )
    xenograft_recipient_taxonomy_id = create_chrfield(
        "Xenograft recipient taxonomy ID"
        )

    ## fields in GSC form only
    # amount_of_antibody_used = create_chrfield("Amount of Antibody Used")
    # antibody_use = create_chrfield("Antibody Used")
    # antibody_vendor = create_chrfield("Antibody Vendor")
    # antibody_catalogue = create_chrfield("Antibody catalogue #")
    # average_size = create_chrfield("Average Size (bp)")
    # crosslinking_method = create_chrfield("Crosslinking Method")
    # crosslinking_time = create_chrfield("Crosslinking Time")
    # dna_concentratino = create_chrfield("DNA Concentration (nM)")
    # dna_volumne = create_chrfield("DNA Volume (uL)")
    # index_read_type = create_chrfield(
    #     "Index Read Type",
    #     choices=index_read_type_choices,
    #     )
    # indexed = create_chrfield("Indexed?")
    # library_construction_method = create_chrfield(
    #     "Library Construction Method"
    #     )
    # library_type = create_chrfield("Library Type")
    # no_of_cells_ip = create_chrfield("No. of cells/IP")
    # quantification_method = create_chrfield("Quantification Method")
    # size_range = create_chrfield("Size Range (bp)")
    # sonication_time = create_chrfield("Sonication Time")
    # storage_medium = create_chrfield("Storage Medium")
    # sublibrary_id = create_chrfield("Sub-Library ID")
    # tube_label = create_chrfield("Tube Label")

    def __str__(self):
        return self.sample_id

class Patient(models.Model, FieldValue):

    """
    Patient sample type.
    """

    # database relationships
    sample = models.ForeignKey(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    library = models.OneToOneField(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )

    additional_pathology_info = create_chrfield(
        "Additional Pathology Information"
        )
    pathology_occurrence = create_chrfield("Pathology Occurrence")
    pathology_disease_name = create_chrfield("Pathology/Disease Name")
    stage = create_chrfield("Stage")
    grade = create_chrfield("Grade")
    tumour_content = create_chrfield("Tumor content (%)")

    def __str__(self):
        return self.sample.sample_id


class CellLine(models.Model, FieldValue):

    """
    CellLine sample type.
    """

    # database relationships
    sample = models.ForeignKey(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    additional_pathology_info = create_chrfield(
        "Additional Pathology Information"
        )
    pathology_occurrence = create_chrfield("Pathology Occurrence")
    pathology_disease_name = create_chrfield("Pathology/Disease Name")
    stage = create_chrfield("Stage")
    grade = create_chrfield("Grade")
    tumour_content = create_chrfield("Tumor content (%)")

    def __str__(self):
        return self.sample.sample_id

class Xenograft(models.Model, FieldValue):

    """
    Xenograft sample type.
    """

    # database relationships
    sample = models.ForeignKey(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    def __str__(self):
        return self.sample.sample_id

class UST(models.Model, FieldValue):

    """
    Undefined Sample type.
    """

    # database relationships
    sample = models.ForeignKey(
        Sample,
        verbose_name="Sample",
        on_delete=models.CASCADE
        )

    def __str__(self):
        return self.samle.sample_id


# class Sample(models.Model, FieldValue):

#     """
#     Sample Information.
#     """

#     # Character fields
#     # SA ID's
#     sample_id = create_chrfield("Sample ID", blank=False)
#         # pool information, unique wafergen chip number
#     pool_id = create_chrfield("Pool ID", blank=False)
#         # Jira Ticket
#     jira_ticket = create_chrfield("Jira Ticket", blank=False)
#         # most likely same as pool ID
#     tube_label = create_chrfield("Original sample label")

#     # database relationships
#     # patient = models.OneToOneField(
#     #                                Patient,
#     #                                null=True,
#     #                                blank=True,
#     #                                verbose_name="Patient",
#     #                                on_delete=models.CASCADE
#     #                                )
        
#     # Integer fields
#     # number of libraries in pool (could be pulled from input file)
#     num_libraries = models.IntegerField(
#                                         "Number of libraries", 
#                                         default=0,
#                                         editable=False
#                                         )
    
#     # DateTime fields
#     # collect_date = models.DateTimeField("Date sample collected", 
#     #                                     blank=True, null=True)
    
#     # sample description
#     description = models.TextField(
#         "Description",
#         blank=True,
#         null=True,
#         max_length=200
#         )
       
#     def __str__(self):
#         return '_'.join([
#                          self.sample_id,
#                          self.pool_id,
#                          ])

#     def has_celltable(self):
#         res = True
#         ## use hasattr() instead
#         try:
#             _ = self.celltable
#         except CellTable.DoesNotExist:
#             res = False
#         return res
    
# #     def clean(self):
# #         if self.has_celltable:
# #             self.num_libraries = len(self.celltable.cell_set.all())
            
    
# class CellTable(models.Model, FieldValue):
    
#     """
#     Cell table containing info for each chip.
#     """
    
#     # database relationships
#     sample = models.OneToOneField(
#                                   Sample,
#                                   null=True,
#                                   verbose_name="Sample",
#                                   on_delete=models.CASCADE
#                                   )
    
    
#     def __str__(self):
#         res = '_'.join([
#                         self.sample.sample_id,
#                         self.sample.pool_id,
# #                         str(self.row) + str(self.col)
#                         ])
#         return res
   
        
# class Cell(models.Model, FieldValue):
    
#     """
#     A Row in the CellTable containing info for one cell.
#     """
    
#     fields_to_exclude = ['ID', 'Cell Table']
#     values_to_exclude = ['id', 'cell_table']
    
#     # database relationships
#     cell_table = models.ForeignKey(
#                                    CellTable,
#                                    verbose_name="Cell Table",
#                                    on_delete=models.CASCADE
#                                    )

#     #Character field
#     sample_cellcaller = create_chrfield("Sample")
    
#     # Integer fields
#     row = models.IntegerField("Row", null=True)
#     col = models.IntegerField("Column", null=True)
#     img_col = models.IntegerField("Image Column", null=True)
#     num_live = models.IntegerField("Num_Live", null=True)
#     num_dead = models.IntegerField("Num_Dead", null=True)
#     num_other = models.IntegerField("Num_Other", null=True)
#     rev_live = models.IntegerField("Rev_Live", null=True)
#     rev_dead = models.IntegerField("Rev_Dead", null=True)
#     rev_other = models.IntegerField("Rev_Other", null=True)
        
#     # Character fields
#     file_ch1 = create_chrfield("File_Ch1")
#     file_ch2 = create_chrfield("File_Ch2")
#     index_i7 = create_chrfield("Index_I7")
#     primer_i7 = create_chrfield("Primer_I7")
#     index_i5 = create_chrfield("Index_I5")
#     primer_I5 = create_chrfield("Primer_I5")
#     pick_met = create_chrfield("Pick_Met")

    
#     def __str__(self):
#         res = '_'.join([
#                         self.cell_table.sample.sample_id,
#                         self.cell_table.sample.pool_id,
#                         str(self.row) + str(self.col),
#                         ])
#         return res


# class Library(models.Model, FieldValue):
    
#     """
#     Library information.
#     """
    
#     fields_to_exclude = ['ID', 'Cell Table']
#     values_to_exclude = ['id', 'cell_table']
    
#     # database relationships
#     cell_table = models.OneToOneField(
#                                       CellTable,
#                                       null=True,
#                                       verbose_name="Cell Table",
#                                       on_delete=models.CASCADE
#                                       )
    
#     # Character fields    
#     protocol = create_chrfield("Protocol") # wafergen, microfluidic, targeted, etc.
#     lib_type = create_chrfield("Library Type")
#     chip_format = create_chrfield("Chip-format")
#     construction_method = create_chrfield("Library construction method") 
#     trans_concentration = create_chrfield("Transposase concentration")
#     size_range = create_chrfield("Size range")
#     i7_index_id = create_chrfield("I7_Index_ID")
#     index = create_chrfield("Index")
#     i5_index_id = create_chrfield("I5_Index_ID")
#     index2 = create_chrfield("Index2")
#     library_location = create_chrfield("Library location")

#     # Integer fields
#     num_pcr_cycles = models.IntegerField("Number of PCR cycles", 
#                                          blank=True, null=True)
#     average_size = models.IntegerField("Average size",
#                                        blank=True, null=True)
#     chip_inlet = models.IntegerField("Chip inlet",
#                                      blank=True, null=True)
    
#     # DateTime fileds
#     spot_date = models.DateTimeField("Sample spot date",
#                                      blank=True, null=True)
#     prep_date = models.DateTimeField("Library preparation date",
#                                  blank=True, null=True)
    
# #     def __str__(self):
# #         return ()
        

# class Analyte(models.Model, FieldValue):
    
#     """
#     Analyte information.
#     """
    
#     fields_to_exclude = ['ID', 'Cell Table']
#     values_to_exclude = ['id', 'cell_table']
    
#     # database relationships
#     cell_table = models.OneToOneField(
#                                       CellTable,
#                                       null=True,
#                                       verbose_name="Cell Table",
#                                       on_delete=models.CASCADE
#                                       )
    
#     # Character fields
#     dna_volume = create_chrfield("DNA volume")
#     dna_concentration = create_chrfield("DNA Concentration")
#     storage_medium = create_chrfield("Storage Medium")
#     q_method = create_chrfield("Quantification method")
#     size_selection_method = create_chrfield("Size selection method")

#     def __str__(self):
#         return self.cell_table.sample.sample_id

    
# class SequencingInfo(models.Model, FieldValue):
    
#     """
#     Sequencing information from GSC.
#     """
    
#     fields_to_exclude = ['ID', 'Cell Table']
#     values_to_exclude = ['id', 'cell_table']
    
#     # database relationships
#     cell_table = models.OneToOneField(
#                                       CellTable,
#                                       null=True,
#                                       verbose_name="Cell Table",
#                                       on_delete=models.CASCADE
#                                       )

#     # Character fields
#     sequencing_id = create_chrfield("Sequencing ID")
#     sequencer_id = create_chrfield("Sequencer ID")
#     flow_cell_id = create_chrfield("Flow cell ID")
#     lane_id = create_chrfield("Lane ID")
#     gsc_lib_id = create_chrfield("GSC library ID")
#     read_length = create_chrfield("Read length")
#     paired_end = create_chrfield("Paired-end (yes/no)")
#     output_mode = create_chrfield("Output mode")
#     archive_path = create_chrfield("Path to data in archive")
#     notes = create_chrfield("Notes", max_length=200)

#     # DateTime fields
#     submission_date = models.DateTimeField("Sequencing submission date",
#                                            blank=True, null=True)
#     sequencing_date = models.DateTimeField("Sequencing date",
#                                            blank=True, null=True)
    
# #     def __str__(self):
# #         return ()
