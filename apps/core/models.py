"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import unicode_literals
from django.db import models

# import django.db.models.options as options
# from django.conf import settings
# from django.core.validators import MinValueValidator, MaxValueValidator

def create_chrfield(name, max_length=50, blank=True, **kwargs):
    """wrap models.CharField for ease of use."""
    
    return models.CharField(name, max_length=max_length, blank=blank, **kwargs) 

class Sample(models.Model):
    
    """
    Sample Information.
    """  
    
    # Character fields
    # SA ID's
    sample_id = create_chrfield("Sample ID", blank=False)
        # pool information, unique wafergen chip number
    pool_id = create_chrfield("Pool ID", blank=False)
        # Jira Ticket
    jira_ticket = create_chrfield("Jira Ticket", blank=False)
        # most likely same as pool ID
    tube_label = create_chrfield("Tube label")

    # sub-library ID which is "sample_id"+"pool_id"+"cell_location"
#     sub_library_id =  None
    
    # Integer fields
    # number of libraries in pool (could be pulled from input file)
    num_libraries = models.IntegerField("Number of libraries", default=0)
    
    # not sure if it's different than num_libraries,
    # got it from old LIMS excel file
    num_cells = models.IntegerField("Number of cells", default=0)
    
    
    # DateTime fields
    collect_date = models.DateTimeField("Date sample collected", 
                                        blank=True, null=True)
    

    # sample description
    description = create_chrfield("Description", max_length = 200)
    
    def __str__(self):
        return '_'.join([
                         self.sample_id,
                         self.pool_id,
                         ])


class Patient(models.Model):
    
    """
    Patient information.
    """
    
    # database relationships
    sample = models.OneToOneField(Sample, null=True,
                                  on_delete=models.CASCADE)
    
    # Character fields
    patient_id = create_chrfield("Patient ID")
    tissue_state = create_chrfield("Tissue State")
    sample_state = create_chrfield("Sample State")
    taxonomy_id = create_chrfield("Taxonomy ID")
    receipient_id = create_chrfield("Recipient ID")
    
    def __str__(self):
        return self.patient_id
 
class CellTable(models.Model):
    
    """
    Cell table containing info for each chip.
    """
    
    # database relationships
    sample = models.OneToOneField(Sample, null=True,
                                  on_delete=models.CASCADE)
    
    
    def __str__(self):
        res = '_'.join([
                        self.sample.sample_id,
                        self.sample.pool_id,
#                         str(self.row) + str(self.col)
                        ])
        return res
   
   
class Cell(models.Model):
    
    """
    A Row in the CellTable containing info for one cell.
    """
    
    # database relationships
    cell_table = models.ForeignKey(CellTable, on_delete=models.CASCADE)

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
    sample_cellcaller = create_chrfield("Sample")
    file_ch1 = create_chrfield("File_Ch1")
    file_ch2 = create_chrfield("File_Ch2")
    index_i7 = create_chrfield("Index_I7")
    primer_i7 = create_chrfield("Primer_I7")
    index_i5 = create_chrfield("Index_I5")
    primer_I5 = create_chrfield("Primer_I5")
    pick_met = create_chrfield("Pick_Met")

    
#     def __str__(self):
#         pass

        
class Library(models.Model):
    
    """
    Library information.
    """
    
    # database relationships
    cell_table = models.OneToOneField(CellTable, null=True,
                                       on_delete=models.CASCADE)
    
    # Character fields    
    protocol = create_chrfield("Protocol") # wafergen, microfluidic, targeted, etc.
    lib_type = create_chrfield("Library Type")
    chip_format = create_chrfield("Chip-format")
    construction_method = create_chrfield("Library construction method") 
    trans_concentration = create_chrfield("Transposase concentration")
    size_range = create_chrfield("Size range")
    i7_index_id = create_chrfield("I7_Index_ID")
    index = create_chrfield("Index")
    i5_index_id = create_chrfield("I5_Index_ID")
    index2 = create_chrfield("Index2")
    library_location = create_chrfield("Library location")

    # Integer fields
    num_pcr_cycles = models.IntegerField("Number of PCR cycles", 
                                         blank=True, null=True)
    average_size = models.IntegerField("Average size",
                                       blank=True, null=True)
    chip_inlet = models.IntegerField("Chip inlet",
                                     blank=True, null=True)
    
    # DateTime fileds
    spot_date = models.DateTimeField("Sample spot date",
                                     blank=True, null=True)
    prep_date = models.DateTimeField("Library preparation date",
                                 blank=True, null=True)
    
#     def __str__(self):
#         return ()
        

class Analyte(models.Model):
    
    """
    Analyte information.
    """
    
    # database relationships
    cell_table = models.OneToOneField(CellTable, null=True,
                                      on_delete=models.CASCADE)
    
    # Character fields
    dna_volume = create_chrfield("DNA volume")
    dna_concentration = create_chrfield("DNA Concentration")
    storage_medium = create_chrfield("Storage Medium")
    q_method = create_chrfield("Quantification method")
    size_selection_method = create_chrfield("Size selection method")

    def __str__(self):
        return self.sample.sample_id

    
class SequencingInfo(models.Model):
    
    """
    Sequencing information from GSC.
    """
    
    # database relationships
    cell_table = models.OneToOneField(CellTable, null=True,
                                      on_delete=models.CASCADE)

    # Character fields
    sequencing_id = create_chrfield("Sequencing ID")
    sequencer_id = create_chrfield("Sequencer ID")
    flow_cell_id = create_chrfield("Flow cell ID")
    lane_id = create_chrfield("Lane ID")
    gsc_lib_id = create_chrfield("GSC library ID")
    read_length = create_chrfield("Read length")
    paired_end = create_chrfield("Paired-end (yes/no)")
    output_mode = create_chrfield("Output mode")
    archive_path = create_chrfield("Path to data in archive")
    notes = create_chrfield("Notes", max_length=200)

    # DateTime fields
    submission_date = models.DateTimeField("Sequencing submission date",
                                           blank=True, null=True)
    sequencing_date = models.DateTimeField("Sequencing date",
                                           blank=True, null=True)
    
#     def __str__(self):
#         return ()
