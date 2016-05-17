"""
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

from __future__ import unicode_literals
from django.db import models

# import django.db.models.options as options
# from django.conf import settings
# from django.core.validators import MinValueValidator, MaxValueValidator

def create_chrfield(name, max_length=25, blank=True, **kwargs):
    """wrap models.CharField for ease of use."""
    
    return models.CharField(name, max_length=max_length, blank=blank, **kwargs) 

class Sample(models.Model):
    
    """
    Sample Information.
    """  
    
    # SA ID's
    sample_id = create_chrfield("Sample ID", blank=False)
    
    # pool information, unique wafergen chip number
    pool_id = create_chrfield("Pool ID", blank=False)
    
    # Jira Ticket
    jira_ticket = create_chrfield("Jira Ticket", blank=False)
    
    # most likely same as pool ID
    tube_label = create_chrfield("Tube label")
    
    # number of libraries in pool (could be pulled from input file; see below)
    num_libraries = models.IntegerField("Number of libraries", default=0)
    
    # not sure if it's different than num_libraries, got this from old LIMS excel file
    num_cells = models.IntegerField("Number of cells", default=0)
    
    # sample collection date/passage number
    collect_date = models.DateTimeField("Date sample collected", 
                                        blank=True, null=True)
    
    # sub-library ID which is "sample_id"+"pool_id"+"cell_location"
#     sub_library_id =  None

    # sample description
    description = create_chrfield("Description", max_length = 200)
    
    def __str__(self):
        return self.sample_id
    
    
class Patient(models.Model):
    
    """
    Patient information.
    """
    
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    
    patient_id = create_chrfield("Patient ID")
    tissue_state = create_chrfield("Tissue State")
    sample_state = create_chrfield("Sample State")
    taxonomy_id = create_chrfield("Taxonomy ID")
    receipient_id = create_chrfield("Recipient ID")
    
    def __str__(self):
        return self.patient_id
        
class Library(object):
    
    """
    Library information.
    """
    
    protocol = None # Protocol (wafergen, microfluidic, targeted, etc.)
    spot_date = None # Sample spot date
    type = None # Library Type
    chip_format = None # Chip-format
    prep_date = None # Library preparation date
    construction_method = None # Library construction method 
    trans_concentration = None # Transposase concentration
    num_pcr_cycles = None # Number of PCR cycles
    size_range = None # Size range
    average_size = None # Average size
    chip_inlet = None # Chip inlet
    i7_index_id = None # I&_Index_ID
    index = None # index
    i5_index_id = None # I5_Index_ID
    index2 = None # index2
    library_location = None # Library location

class Analyte(object):
    
    """
    Analyte information.
    """
    
    def __init__(self):
        dna_volume = None # DNA volume
        dna_concentration = None # DNA Concentration
        storage_medium = None # Storage Medium
        q_method = None # Quantification method
        size_selection_method = None # Size selection method

class CellCaller(object):
    
    """
    Output information of the cell caller.
    """
    
    def __init__(self):
        sample = None # Sample
        row = None # Row
        col = None # Column
        img_col = None # Img_Col
        file_ch1 = None # File_Ch1
        file_ch2 = None # File_Ch2
        num_live = None # Num_Live
        num_dead = None # Num_Dead
        num_other = None # Num_Other
        rev_live = None # Rev_Live
        rev_dead = None # Rev_Dead
        rev_other = None # Rev_Other
        index_i7 = None # Index_I7
        primer_i7 = None # Primer_I7
        index_i5 = None # Index_I5
        primer_I5 = None # Primer_I5
        pick_met = None # Pick_Met


class Sequencing(object):
    
    """
    Sequencing information from GSC.
    """
    
    def __init__(self):
        sequencing_id = None # Sequencing ID
        submission_date = None # Sequencing submission date
        sequencing_date = None # Sequencing date
        sequencer_id = None # Sequencer ID
        flow_cell_id = None # Flow cell ID
        lane_id = None # Lane ID
        gsc_lib_id = None # GSC library ID
        read_length = None # Read length
        paired_end = None # Paired-end (yes/no)
        output_mode = None # Output mode
        archive_path = None # Path to data in archive
        notes = None # Notes

