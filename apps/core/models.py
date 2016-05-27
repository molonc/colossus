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
def create_chrfield(name, max_length=50, blank=True, **kwargs):
    """wrap models.CharField for ease of use."""

    return models.CharField(name, max_length=max_length, blank=blank, **kwargs)


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
    description = models.TextField(
        "Description",
        null=True,
        blank=True,
        max_length=300
        )

    def __str__(self):
        return '_'.join([self.sample_id, self.pool_id])


class Cell(models.Model, FieldValue):

    """
    Information of one single cell.
    """

    # fields_to_exclude = ['ID', 'Cell Table']
    # values_to_exclude = ['id', 'cell_table']
    
    ## database relationships
    library = models.ForeignKey(
        Library,
        verbose_name="Library",
        on_delete=models.CASCADE
        )

    #Character field
    sample_cellcaller = create_chrfield("Sample")
    
    # Integer fields
    row = models.IntegerField("Row", null=True)
    col = models.IntegerField("Column", null=True)
    img_col = models.IntegerField("Image Column", null=True)
    num_live = models.IntegerField("Num_Live", null=True)
    num_dead = models.IntegerField("Num_Dead", null=True)
    num_other = models.IntegerField("Num_Other", null=True)
    rev_live = models.IntegerField("Rev_Live", null=True)
    rev_dead = models.IntegerField("Rev_Dead", null=True)
    rev_other = models.IntegerField("Rev_Other", null=True)
        
    # Character fields
    file_ch1 = create_chrfield("File_Ch1")
    file_ch2 = create_chrfield("File_Ch2")
    index_i7 = create_chrfield("Index_I7")
    primer_i7 = create_chrfield("Primer_I7")
    index_i5 = create_chrfield("Index_I5")
    primer_I5 = create_chrfield("Primer_I5")
    pick_met = create_chrfield("Pick_Met")

    
    def __str__(self):
        res = '_'.join([
                        self.library.sample_id,
                        self.library.pool_id,
                        str(self.row) + str(self.col),
                        ])
        return res


class Sample(models.Model, FieldValue):

    """
    Base class of different sample types.
    """

    # sample_type = None

    ## Choices
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

    index_read_type_choices = (
        ('on_3rd_read','On 3rd (index-specific) read'),
        ('on_forward_read','On forward read'),
        ('on_reverse_read','On reverse read'),
        )

    ## required fields
    sample_id = create_chrfield("Sample ID", blank=False)

    ## other fields in alphabetical order
    # additional_pathology_info = create_chrfield(
    #     "Additional Pathology Information"
    #     )
    # amount_of_antibody_used = create_chrfield("Amount of Antibody Used")
    anatomic_site = create_chrfield("Anatomic Site")
    anatomic_sub_site = create_chrfield("Anatomic Sub-Site")
    # anonymou_patient_id = create_chrfield("Anonymous Patient ID")
    # antibody_use = create_chrfield("Antibody Used")
    # antibody_vendor = create_chrfield("Antibody Vendor")
    # antibody_catalogue = create_chrfield("Antibody catalogue #")
    # average_size = create_chrfield("Average Size (bp)")
    # cell_line_id = create_chrfield("Cell Line ID")
    # cell_type = create_chrfield("Cell Type")
    # crosslinking_method = create_chrfield("Crosslinking Method")
    # crosslinking_time = create_chrfield("Crosslinking Time")
    # dna_concentratino = create_chrfield("DNA Concentration (nM)")
    # dna_volumne = create_chrfield("DNA Volume (uL)")
    # developmenta_stage = create_chrfield("Developmental Stage")
    disease_condition_health_status = create_chrfield(
        "Disease Condition/Health Status"
        )
    # family_information = create_chrfield("Family Information")
    # grade = create_chrfield("Grade")
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
    # pathology_occurrence = create_chrfield("Pathology Occurrence")
    # pathology_disease_name = create_chrfield("Pathology/Disease Name")
    # quantification_method = create_chrfield("Quantification Method")
    sex = create_chrfield("Sex", choices=sex_choices)
    # size_range = create_chrfield("Size Range (bp)")
    # sonication_time = create_chrfield("Sonication Time")
    # stage = create_chrfield("Stage")
    # storage_medium = create_chrfield("Storage Medium")
    # strain = create_chrfield("Strain")
    # sub_library_id = create_chrfield("Sub-Library ID")
    taxonomy_id = create_chrfield("Taxonomy ID")
    # tissue_type = create_chrfield("Tissue Type", choices=tissue_type_choises)
    # treatment_status = create_chrfield("Treatment Status")
    # tube_label = create_chrfield("Tube Label")
    # tumour_content = create_chrfield("Tumor content (%)")

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
