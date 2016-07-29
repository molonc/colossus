"""
Created on June 6, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os, sys
import pandas as pd 
from .models import SublibraryInformation

def parse_smartchipapp_file(csv_infile):
    """parse the result file of SmartChipApp."""
    df = pd.read_excel(csv_infile, sheetname=0)
    
    ## filter out the cells whose Pick_Met value is not NaN
    df = df[~df['Pick_Met'].isnull()]

    ## change the column names to match the filed names of the model
    df.columns = [c.lower() for c in df.columns]
    return df


def create_sublibrary_information(s):
    """create SublibraryInformation instance from given pandas Series."""
    d = s.to_dict()
    instance = SublibraryInformation(**d)
    return instance


def bulk_create_sublibrary(library, csv_infile):
    """add sublirary information in df for given library instance."""
    df = parse_smartchipapp_file(csv_infile)
    num_sublibraries = df.size/len(df.columns)

    ## delete previous sublibraryinformation_set
    library.sublibraryinformation_set.all().delete()

    instances = []
    for instance in df.apply(create_sublibrary_information, axis=1):
        instance.library_id = library.pk
        instances.append(instance)

    library.sublibraryinformation_set.bulk_create(instances)
    return num_sublibraries


class HistoryManager(object):

    """
    An api for simple_history app.
    """

    @staticmethod
    def print_history(object, history_type=None):
        print '=' * 100
        print "Object\tID\tDate\tAction\tUser"
        print '=' * 100
        if history_type is None:
            histories = object.history.all()
        else:
            histories = object.history.filter(history_type=history_type)

        for h in histories:
            print "\t".join([
                str(h.instance),
                str(h.instance.id),
                str(h.history_date),
                h.get_history_type_display(),
                str(h.history_user),
                ])
            print '-' * 100
