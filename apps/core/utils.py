"""
Created on June 6, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os, sys
import pandas as pd 
from .models import SublibraryInformation

def parse_smartchipapp_file(csv_infile):
    """parse the result file of SmartChipApp."""
    df = pd.read_excel(csv_infile, sheetname=4)
    return df


def create_sublibrary_information(s):
    """create SublibraryInformation instance from given pandas Series."""
    d = s.to_dict()

    ## keys should be proper fileds from SublibraryInformation model
    keys_map = {
        'Sample': 'sample_cellcaller',
        'Row': 'row',
        'Column': 'col',
        'Img_Col': 'img_col',
        'Num_Live': 'num_live',
        'Num_Dead':'num_dead',
        'Num_Other':'num_other',
        'Rev_Live':'rev_live',
        'Rev_Dead':'rev_dead',
        'Rev_Other':'rev_other',
        'File_Ch1':'file_ch1',
        'File_Ch2':'file_ch2',
        'Index_I7':'index_i7',
        'Index_I5':'index_i5',
        'Primer_I7':'primer_i7',
        'Primer_I5':'primer_i5',
        'Pick_Met':'pick_met',
        }
    d = dict((keys_map[k],v) for k,v in d.iteritems())

    instance = SublibraryInformation(**d)
    return instance


def bulk_create_sublibrary(library, csv_infile):
    """add sublirary information in df for given library instance."""
    df = parse_smartchipapp_file(csv_infile)
    num_sublibraries = df.size/17
    ## first delete previous sublibraryinformation_set
    library.sublibraryinformation_set.all().delete()
    instances = []
    for instance in df.apply(create_sublibrary_information, axis=1):
        instance.library_id = library.pk
        instances.append(instance)

    library.sublibraryinformation_set.bulk_create(instances)
    return num_sublibraries
