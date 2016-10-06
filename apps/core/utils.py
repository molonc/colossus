"""
Created on June 6, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os, sys
import pandas as pd 
from string import Template
from .models import SublibraryInformation
from django.conf import settings

#==================================================
# upload, parse and populate Sublibrary Information
#--------------------------------------------------
def parse_smartchipapp_file(csv_infile):
    """parse the result file of SmartChipApp."""
    df = pd.read_excel(csv_infile, sheetname=0)
    ## filter out the cells whose Spot_Well value is not NaN
    df = df[~df['Spot_Well'].isnull()]
    ## change the column names to match the filed names of the model
    df.columns = [c.lower() for c in df.columns]
    return df


def create_sublibrary_information(s):
    """create SublibraryInformation instance from given pandas Series."""
    d = s.to_dict()
    instance = SublibraryInformation(**d)
    return instance


def bulk_create_sublibrary(library, df):
    """add sublirary information in df for given library instance."""
    num_sublibraries = df.size/len(df.columns)

    ## delete previous sublibraryinformation_set
    library.sublibraryinformation_set.all().delete()

    instances = []
    for instance in df.apply(create_sublibrary_information, axis=1):
        instance.library_id = library.pk
        instances.append(instance)

    library.sublibraryinformation_set.bulk_create(instances)
    return num_sublibraries


#=================
# history manager
#-----------------
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

#======================
# generate sample sheet
#----------------------
def generate_samplesheet(sequencing, ofilename):
    """generate samplesheet for the given Sequencing using template in SC-180."""
    # generate header section
    template_samplesheet = os.path.join(
        settings.BASE_DIR, "templates/template_samplesheet.html")
    ofilename = os.path.join(settings.MEDIA_ROOT, ofilename)
    with open(template_samplesheet, 'r') as tempstr:
        s = Template(tempstr.read())
        d = {
        'sequencing_instrument': sequencing.get_sequencing_instrument_display(),
        'submission_date': sequencing.submission_date,
        'pool_id': sequencing.library.pool_id,
        'read1_length': sequencing.read1_length,
        'read2_length': sequencing.read2_length,
        }

        # Sequencing may have no SequencingDetail
        try:
            d['flow_cell_id'] = sequencing.sequencingdetail.flow_cell_id
        except:
            d['flow_cell_id'] = None

        s = s.safe_substitute(**d)
        ofile = open(ofilename, 'w')
        ofile.write(s)
        ofile.close()

    # generate [Data] section
    data_table = reorder_colnames(mk_data_table(sequencing))
    data_table.to_csv(ofilename, mode='a', index=False)
    return os.path.abspath(ofilename)

def mk_data_table(sequencing):
    """make [Data] section of the samplesheet template."""
    def _map_to_template(s):
        d = s.to_dict()
        # This is the relation between columns in the template samplesheet
        # and the actual columns in df from LIMS.
        res = {
        'Sample_ID': '-'.join([
        str(sequencing.library.sample),
        str(sequencing.library.pool_id),
        'R'+ str(d['row']),
        'C'+ str(d['column'])
        ]),
        'Sample_Name': d['sample'],
        'Sample_Plate': 'R' + str(d['row']) + '_C' + str(d['column']),
        'Sample_Well': 'R' + str(d['row']) + '_C' + str(d['img_col']),
        'I7_Index_ID': d['index_i7'],
        'index': d['primer_i7'],
        'I5_Index_ID': d['index_i5'],
        'index2': d['primer_i5'],
        #'Description': 'CC=<cell call number>;EC=<experimental condition letter>',
        'Description': 'CC=' + d['pick_met'] + ';' + 'EC=' + d['spot_class'],
        }
        return res

    sample_project = ','.join(sequencing.library.projects.names())
    newl = []
    oldl = list(sequencing.library.sublibraryinformation_set.values())
    df = pd.DataFrame(oldl)
    for d in df.apply(_map_to_template, axis=1):
        d['Sample_Project'] = sample_project
        newl.append(d)
    return pd.DataFrame(newl)

def reorder_colnames(df):
    # reorder the columns to match those of samplesheet template.
    if df.empty:
        return df
    colnames = [
    'Sample_ID',
    'Sample_Name',
    'Sample_Plate',
    'Sample_Well',
    'I7_Index_ID',
    'index',
    'I5_Index_ID',
    'index2',
    'Sample_Project',
    'Description'
    ]
    return df[colnames]
