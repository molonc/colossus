"""
Created on June 6, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)
"""

import os, sys
import pandas as pd 
import yaml
from string import Template
from collections import OrderedDict
from datetime import date

#===============
# Django imports
#---------------
from .models import Sequencing, SublibraryInformation
from django.conf import settings
from django.shortcuts import get_object_or_404

#==================================================
# upload, parse and populate Sublibrary Information
#--------------------------------------------------
def parse_smartchipapp_file(csv_infile):
    """parse the result file of SmartChipApp."""
    df = pd.read_excel(csv_infile, sheetname=0)
    ## filter out the cells whose Spot_Well value is not NaN
    df = df[~df['Spot_Well'].isnull()]
    df = df.sort_values(by='Sample')
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
def generate_samplesheet(pk):
    """generate samplesheet for the given Sequencing using template in SC-180."""
    samplesheet = SampleSheet(pk)
    sheet_name = samplesheet.sheet_name
    ofilename = os.path.join(settings.MEDIA_ROOT, sheet_name)
    samplesheet.write_header(ofilename)
    samplesheet.write_data(ofilename)
    return sheet_name, os.path.abspath(ofilename)

class SampleSheet(object):

    """
    Sequencing SampleSheet.
    """

    def __init__(self, pk):
        self._sequencing = get_object_or_404(Sequencing, pk=pk)
        self._header = os.path.join(settings.BASE_DIR,
            "templates/template_samplesheet_header.html")
        self._colnames = [
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

    @property
    def sequencing(self):
        return self._sequencing

    @property
    def sheet_name(self):
        fc_id = self._sequencing.sequencingdetail.flow_cell_id
        sheet_name = 'SampleSheet_%s.csv' % fc_id
        return sheet_name

    def write_header(self, ofilename):
        """write the header section of the sequencing SampleSheet."""
        with open(self._header, 'r') as tempstr:
            s = Template(tempstr.read())
            d = {
            'sequencing_instrument': self._sequencing.get_sequencing_instrument_display(),
            'submission_date': self._sequencing.submission_date,
            'pool_id': self._sequencing.library.pool_id,
            'read1_length': self._sequencing.read1_length,
            'read2_length': self._sequencing.read2_length,
            }

            # Sequencing may have no SequencingDetail
            try:
                d['flow_cell_id'] = self._sequencing.sequencingdetail.flow_cell_id
            except:
                d['flow_cell_id'] = None

            s = s.safe_substitute(**d)
            ofile = open(ofilename, 'w')
            ofile.write(s)
            ofile.close()

    def write_data(self, ofilename):
        """write the data section of the sequencing SampleSheet."""
        data_table = self._mk_data_table()

        # reorder the columns
        data_table = data_table[self._colnames]
        data_table.to_csv(ofilename, mode='a', index=False)

    def _mk_data_table(self):
        """make data table for data section of the samplesheet template."""
        def _map_to_template(s):
            d = s.to_dict()
            # This is the relation between columns in the template samplesheet
            # and the actual columns in df from LIMS.
            res = {
            'Sample_ID': '-'.join([
            str(self._sequencing.library.sample),
            str(self._sequencing.library.pool_id),
            'R'+ str(d['row']),
            'C'+ str(d['column'])
            ]),
            'Sample_Name': '',
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

        sample_project = '' #','.join(sequencing.library.projects.names())
        newl = []
        oldl = list(self._sequencing.library.sublibraryinformation_set.values())
        df = pd.DataFrame(oldl)
        for d in df.apply(_map_to_template, axis=1):
            d['Sample_Project'] = sample_project
            newl.append(d)
        return pd.DataFrame(newl)


#=============================
# generate GSC submission form
#-----------------------------
def generate_gsc_form(pk, metadata):
    """generate the GSC submission form for the given library."""
    gsc_form = GSCForm(pk)
    pool_df = gsc_form.meta_df
    sample_df = gsc_form.data_df
    header1 = gsc_form.meta_header
    header2 = gsc_form.data_header
    form_name = gsc_form.get_form_name(metadata["sow"])
    ofilename = os.path.join(settings.MEDIA_ROOT, form_name)

    workbook = Submission(pool_df, sample_df, ofilename)
    workbook.set_column_width()
    workbook.write_address_box(metadata)
    workbook.write_pool_header(header1)
    workbook.write_sample_header(header2)
    workbook.close()
    return form_name, os.path.abspath(ofilename)

class GSCForm(object):

    """
    GSC sequencing submission form.
    """

    def __init__(self, pk):
        self._sequencing = get_object_or_404(Sequencing, pk=pk)
        self._library = self._sequencing.library
        self._libconst = self._library.libraryconstructioninformation
        self._libquant = self._library.libraryquantificationandstorage
        self._sample = self._library.sample
        self._sample_addinfo = self._sample.additionalsampleinformation
        self._meta_header = os.path.join(settings.BASE_DIR,
            "templates/template_gsc_meta_header.html")
        self._data_header = os.path.join(settings.BASE_DIR,
            "templates/template_gsc_data_header.html")
        self._meta_colnames = [
        'POOL ID',
        'Tube Label',
        'Taxonomy ID',
        'DNA Volume (uL)',
        'DNA Concentration (nM)',
        'Storage Medium',
        'Quantification Method',
        'Library Type',
        'Library Construction Method',
        'Size Range (bp)',
        'Average Size (bp)',
        'Number of libraries in pool',
        'Read Type',
        'Read Length',
        'Sequencing Goal',
        'Reference genome for alignment',
        'Format for data dissemination',
        'Additional comments',
        ]
        self._data_colnames = [
        'Sub-Library ID',
        'Tube Label',
        'Taxonomy ID',
        'Anonymous Patient ID',
        'Strain',
        'Disease Condition/Health Status',
        'Sex',
        'Sample Collection Date',
        'Anatomic Site',
        'Anatomic Sub-Site',
        'Developmental Stage',
        'Tissue Type',
        'Cell Type',
        'Cell Line ID',
        'Pathology/Disease Name (for diseased sample only)',
        'Additional Pathology Information',
        'Grade',
        'Stage',
        'Tumor content (%)',
        'Pathology Occurrence',
        'Treatment Status',
        'Family Information',
        'DNA Volume (uL)',
        'DNA Concentration (nM)',
        'Storage Medium',
        'Quantification Method',
        'Library Type',
        'Library Construction Method',
        'Size Range (bp)',
        'Average Size (bp)',
        "Indexed? If the libraries are indexed, provide the index sequence from 5' to 3'",
        'Index Read Type (select from drop down list)',
        'Dual Indices for LIMS Upload',
        'No. of cells/IP',
        'Crosslinking Method',
        'Crosslinking Time',
        'Sonication Time',
        'Antibody Used',
        'Antibody catalogue #',
        'Antibody Vendor',
        'Amount of Antibody Used',
        'I7_Index_ID',
        'index',
        'I5_Index_ID',
        'index2'
        ]
        self._meta_df = self._get_meta_df()
        self._data_df = self._get_data_df()

    @property
    def sequencing(self):
        return self._sequencing

    @property
    def meta_header(self):
        return yaml.load(open(self._meta_header), Loader = YODLoader)

    @property
    def data_header(self):
        return yaml.load(open(self._data_header), Loader = YODLoader)

    @property
    def meta_df(self):
        return self._meta_df

    @property
    def data_df(self):
        return self._data_df

    def get_form_name(self, statement_of_work):
        "create the proper name for the form."
        form_name = '_'.join([
            'Aparicio',
            statement_of_work,
            'Constructed_Library-Submission',
            date.today().strftime("%d%B%Y"),
            self._sample.sample_id,
            self._library.pool_id,
            ]) + '.xlsx'
        return form_name

    def _get_meta_df(self):
        """return a dataframe of metadata information for self._sequencing."""
        # it's ordered based on the self._meta_colnames.
        values = [
        '_'.join([self._library.sample.sample_id, self._library.pool_id]),
        ' '.join([self._library.pool_id, self._library.sample.sample_id]),
        self._library.sample.taxonomy_id,
        self._libquant.dna_volume,
        self._libquant.dna_concentration_nm,
        self._libquant.storage_medium,
        self._libquant.quantification_method,
        self._libconst.library_type,
        self._libconst.library_construction_method,
        self._libquant.size_range,
        self._libquant.average_size,
        self._library.num_sublibraries,
        self._sequencing.get_read_type_display(),
        self._sequencing.read1_length,
        self._sequencing.sequencing_goal,
        "N/A",
        self._sequencing.format_for_data_submission,
        "",
        ]

        # to avoid the "ValueError: If using all scalar values,
        # you must must pass an index".
        data = {k:[v] for k, v in zip(self._meta_colnames, values)}
        df = pd.DataFrame(data)

        # reorder the columns
        df = df[self._meta_colnames]
        return df

    def _get_data_df(self):
        """return a dataframe of sublibrary information for the given library."""
        sample_columns = {
        'Taxonomy ID': self._sample.taxonomy_id,
        'Anonymous Patient ID': self._sample.anonymous_patient_id,
        'Strain': self._sample.strain,
        'Disease Condition/Health Status': self._sample_addinfo.disease_condition_health_status,
        'Sex': self._sample_addinfo.get_sex_display(),
        'Anatomic Site': self._sample_addinfo.anatomic_site,
        'Anatomic Sub-Site': self._sample_addinfo.anatomic_sub_site,
        'Developmental Stage':self._sample_addinfo.developmental_stage,
        'Tissue Type': self._sample_addinfo.get_tissue_type_display(),
        'Cell Type': self._sample_addinfo.cell_type,
        'Cell Line ID': self._sample.cell_line_id,
        'Pathology/Disease Name (for diseased sample only)': self._sample_addinfo.pathology_disease_name,
        'Additional Pathology Information': self._sample_addinfo.additional_pathology_info,
        'Grade': self._sample_addinfo.grade,
        'Stage': self._sample_addinfo.stage,
        'Tumor content (%)': self._sample_addinfo.tumour_content,
        'Pathology Occurrence': self._sample_addinfo.get_pathology_occurrence_display(),
        'Treatment Status': self._sample_addinfo.get_treatment_status_display(),
        'Family Information': self._sample_addinfo.family_information,
        }

        library_columns = {
        'Tube Label': 'NA', #self.library.library_tube_label,
        'Sample Collection Date': self._library.librarysampledetail.sample_spot_date,
        'DNA Volume (uL)': "", #self._libquant.dna_volume,
        'DNA Concentration (nM)': "", #self._libquant.dna_concentration_nm,
        'Storage Medium': "", #self._libquant.storage_medium,
        'Quantification Method': "", #self._libquant.quantification_method,
        'Library Type': self._libconst.library_type,
        'Library Construction Method': self._libconst.library_construction_method,
        'Size Range (bp)': self._libquant.size_range,
        'Average Size (bp)': self._libquant.average_size,
        }

        sequencing_columns = {
        'Index Read Type (select from drop down list)': self._sequencing.index_read_type,
        }

        other_columns = {
        'No. of cells/IP': None,
        'Crosslinking Method': None,
        'Crosslinking Time': None,
        'Sonication Time': None,
        'Antibody Used': None,
        'Antibody catalogue #': None,
        'Antibody Vendor': None,
        'Amount of Antibody Used': None,
        }

        res = []
        sublib_set = self._library.sublibraryinformation_set.all()
        index = lambda sl: sl.primer_i7 + sl.primer_i5 
        dual_index = lambda sl: sl.primer_i7 + '-' + sl.primer_i5
        for sl in sublib_set:
            d = {
            'Sub-Library ID': sl.get_sublibrary_id(),
            "Indexed? If the libraries are indexed, provide the index sequence from 5' to 3'": index(sl),
            'Dual Indices for LIMS Upload': dual_index(sl),
            'I7_Index_ID': sl.index_i7,
            'index': sl.primer_i7,
            'I5_Index_ID': sl.index_i5,
            'index2': sl.primer_i5,
            }
            d.update(sample_columns)
            d.update(library_columns)
            d.update(sequencing_columns)
            d.update(other_columns)
            res.append(d)

        df = pd.DataFrame(res)
        # reorder the columns
        df = df[self._data_colnames]
        return pd.DataFrame(df)


class YODLoader(yaml.Loader):

    """
    @author: Jamie Xu
    A YAML loader that loads mappings into ordered dictionaries.
    (http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts)
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)
        self.add_constructor(
            'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(
            'tag:yaml.org,2002:omap', type(self).construct_yaml_map)


    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)


    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructError(None, None,
                'expected a mapping node, but found %s' % node.id,
                node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as err:
                raise yaml.constructor.ConstructError(
                    'while constructing a mapping', node.start_mark,
                    'found unacceptable key (%s)' % err, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

class Submission(object):

    """
    @author: Jamie Xu
    """

    def __init__(self, df_pool, df_samples, output):

        self.pool_start = 58
        self.sample_start = self.pool_start + len(df_pool) + 10

        self.writer = pd.ExcelWriter(output, engine='xlsxwriter')



        df_pool.to_excel(self.writer, sheet_name='Submission Info', startrow=self.pool_start, startcol=0, header=False, index=False)
        df_samples.to_excel(self.writer, sheet_name='Submission Info', startrow=self.sample_start, startcol=0, header=False, index=False)



        self.workbook = self.writer.book
        self.worksheet = self.writer.sheets['Submission Info']


        self.columns = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                        'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ']

    def close(self):
        '''
        Saves the workbook
        '''
        self.workbook.close()

    def set_column_width(self):
        self.worksheet.set_column('A:A', 45)
        self.worksheet.set_column('B:B', 45)
        self.worksheet.set_column('C:AS', 15)
        return self.worksheet

    def write_address_box(self, info_dict):
        ## updated by jtaghiyar
        HEADER = ["Deliver/ship samples on dry ice or ice pack to:",
                  "%s" % info_dict['name'],
                  "%s" % info_dict['org'],
                  "%s" % info_dict['addr'],
                  "",
                  "",
                  "Email: %s" % info_dict['email'],
                  "Tel: %s" % info_dict['tel']
                  ]

        row = len(HEADER) + 2
        column_span = 7

        input_cell = "{column}{row}"
        nextera_compatible = "Yes" if info_dict.get('nextera_compatible') else "No"
        truseq_compatible = "Yes" if info_dict.get('truseq_compatible') else "No"
        custom = "Yes" if info_dict.get('custom') else "No"
        pbal_library = "Yes" if info_dict.get('is_this_pbal_library') else "No"
        at_completion = "Return unused sample" if info_dict['at_completion']=="R" else "Destroy unused sample"

        # FORMATS
        bold = self.workbook.add_format({'bold':True})
        red = self.workbook.add_format({'bold':True, 'font_color':'red'})
        blue = self.workbook.add_format({'bold':True, 'font_color':'blue'})
        yellow_fill = self.workbook.add_format({'pattern':True, 'bg_color':'yellow'})
        header = self.workbook.add_format({'font_color':'blue', 'pattern': True, 'bg_color':'white', 'font_size':14, 'bold':True})
        text = self.workbook.add_format({'font_color':'black', 'pattern': True, 'bg_color':'white'})
        lower_border = self.workbook.add_format({'font_color':'black', 'pattern': True, 'bg_color':'white', 'bottom':6})
        right_border = self.workbook.add_format({'font_color':'black', 'pattern': True, 'bg_color':'white', 'right':6})
        lower_right_border = self.workbook.add_format({'font_color':'black', 'pattern': True, 'bg_color':'white', 'bottom':6, 'right':6})
        inner_format = self.workbook.add_format({'font_color':'black', 'pattern':True, 'bg_color':'white'})
        right_align = self.workbook.add_format({'align':'right', 'bold':True})
        left_align = self.workbook.add_format({'align':'left', 'bold':True})
        yellow = self.workbook.add_format({'pattern':True, 'bg_color':'yellow', 'bold': True, 'border':2})
        light_green = self.workbook.add_format({'pattern':True, 'bold':True, 'align':'right','bg_color':'#E5F6D9', 'border':1})
        dark_green = self.workbook.add_format({'pattern':True, 'bold':True, 'bg_color':'#73A94F','border':2})
        peach = self.workbook.add_format({'pattern':True, 'bold':True, 'align':'right','bg_color':'#F7C876', 'border':2})

        for x in range(0,column_span):
            for y in range(1,row):
                if x == column_span - 1 and y == row - 1:
                    self.worksheet.write(input_cell.format(column=self.columns[x], row=y), "", lower_right_border)
                elif x == column_span - 1:
                    self.worksheet.write(input_cell.format(column=self.columns[x], row=y), "", right_border)
                elif y == row - 1:
                    self.worksheet.write(input_cell.format(column=self.columns[x], row=y), "", lower_border)
                else:
                    self.worksheet.write(input_cell.format(column=self.columns[x], row=y), "", inner_format)

        for x in range(0,len(HEADER)):
            if x == 0:
                self.worksheet.write(input_cell.format(column="A", row=x+1), HEADER[x], header)
            else:
                self.worksheet.write(input_cell.format(column="A", row=x+1), HEADER[x], text)


        self.worksheet.write(input_cell.format(column="A", row=row+2), "PLEASE PROVIDE COMPLETE INFORMATION FOR YOUR SAMPLES IN THE FIELDS BELOW.  ENTER \"N/A\" IN FIELDS THAT DO NOT APPLY TO YOUR SAMPLES.", red)

        self.worksheet.write(input_cell.format(column="A", row=row+4), "Submitting Organization:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+4), info_dict['submitting_org'], left_align)

        self.worksheet.write(input_cell.format(column="A", row=row+5), "Name of Principal Investigator:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+5), info_dict['pi_name'], left_align)

        self.worksheet.write(input_cell.format(column="A", row=row+6), "Principal Investigator's email:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+6), info_dict['pi_email'], left_align)

        self.worksheet.write(input_cell.format(column="A", row=row+7), "Name of Submitter:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+7), info_dict['submitter_name'], left_align)

        self.worksheet.write(input_cell.format(column="A", row=row+8), "Submitter's email:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+8), info_dict['submitter_email'], left_align)

        self.worksheet.write(input_cell.format(column="A", row=row+9), "Submission Date:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+9), info_dict['submission_date'], left_align)

        self.worksheet.write(input_cell.format(column="A", row=row+10), "Project Name:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+10), info_dict['project_name'], left_align)

        self.worksheet.write(input_cell.format(column="A", row=row+11), "Statement of Work (SOW) #:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+11), info_dict['sow'], left_align)

        self.worksheet.write(input_cell.format(column="A", row=row+14), "**Mandatory** Library Info:", yellow)

        self.worksheet.write(input_cell.format(column="A", row=row+15), "Nextera Compatible", light_green)
        self.worksheet.write(input_cell.format(column="B", row=row+15), nextera_compatible)
        # self.worksheet.data_validation(input_cell.format(column="B", row=row+15), {'validate':'list', 'source':['YES','NO']})

        self.worksheet.write(input_cell.format(column="A", row=row+16), "TruSeq Compatible", light_green)
        self.worksheet.write(input_cell.format(column="B", row=row+16), truseq_compatible)
        # self.worksheet.data_validation(input_cell.format(column="B", row=row+16), {'validate':'list', 'source':['YES','NO']})

        self.worksheet.write(input_cell.format(column="A", row=row+17), "Custom", light_green)
        self.worksheet.write(input_cell.format(column="B", row=row+17), custom)
        # self.worksheet.data_validation(input_cell.format(column="B", row=row+17), {'validate':'list', 'source':['YES','NO']})

        self.worksheet.write(input_cell.format(column="A", row=row+19), "Is this is PBAL Library?", peach)
        self.worksheet.write(input_cell.format(column="B", row=row+19), pbal_library)
        # self.worksheet.data_validation(input_cell.format(column="B", row=row+19), {'validate':'list', 'source':['YES','NO']})

        self.worksheet.write(input_cell.format(column="A", row=row+21), "For Custom Library Info only:", dark_green)
        self.worksheet.write(input_cell.format(column="A", row=row+22), "Primer 1 Name:", light_green)
        self.worksheet.write(input_cell.format(column="A", row=row+23), "Primer 1 Sequence (with 5' and 3'):", light_green)
        self.worksheet.write(input_cell.format(column="A", row=row+24), "Primer 2 Name:", light_green)
        self.worksheet.write(input_cell.format(column="A", row=row+25), "Primer 2 Sequence (with 5' and 3'):", light_green)
        self.worksheet.write(input_cell.format(column="A", row=row+26), "Adaptor 1 Name:", light_green)
        self.worksheet.write(input_cell.format(column="A", row=row+27), "Adaptor 1 Sequence (with 5' and 3'):", light_green)
        self.worksheet.write(input_cell.format(column="A", row=row+28), "Adaptor 2 Name:", light_green)
        self.worksheet.write(input_cell.format(column="A", row=row+29), "Adaptor 2 Sequence (with 5' and 3'):", light_green)

        self.worksheet.write(input_cell.format(column="A", row=row+31), "At completion of project (choose one):", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+31), at_completion)
        # self.worksheet.data_validation(input_cell.format(column="B", row=row+31), {'validate':'list', 'source':['Return Unused Sample', 'Destroy Unused Sample']})

        self.worksheet.write(input_cell.format(column="C", row=row+31), "=IF(EXACT(B45, \"Destroy Unused Sample\"), \"GSC will destroy any remaining sample at completion of project\", IF(EXACT(B45,\"Return Unused Sample\"), \"GSC will return any residual sample at Submitter's expense\",\"\"))", bold)
        #self.worksheet.conditional_format(input_cell.format(column="C", row=row+31), {'type':'text', 'criteria':'containsText'})


        self.worksheet.write(input_cell.format(column="A", row=row+34), "Sample Requirements (Volume & Amounts):", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+34), "http://www.bcgsc.ca/services/sequencing-libraries-faq")

        self.worksheet.write(input_cell.format(column="A", row=row+35), "*NCBI Taxonomy link:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row+35), "http://www.ncbi.nlm.nih.gov/Taxonomy/")

        self.worksheet.write(input_cell.format(column="A", row=row+37), "PLEASE NOTE", self.workbook.add_format({'bold':True, 'font_color':'red', 'pattern':True, 'bg_color':'#F7C876'}))
        self.worksheet.write(input_cell.format(column="B", row=row+37), "If indices are supplied, the reads will automatically be split by index.", bold)
        self.worksheet.write(input_cell.format(column="A", row=row+38), "", self.workbook.add_format({'bold':True, 'font_color':'red', 'pattern':True, 'bg_color':'#F7C876'}))
        self.worksheet.write(input_cell.format(column="B", row=row+38), "If the reads require splitting by index, but indices are not supplied or are incorrect, there will be a 1-2 week delay in the data processing.", bold)

        self.worksheet.write_rich_string(input_cell.format(column="A", row=row+40),
                                         bold, 'Mandatory Fields in ',
                                         red, 'RED',
                                         bold, ', Optional Fields in ',
                                         blue, 'BLUE',
                                         yellow_fill)

        self.worksheet.write_rich_string(input_cell.format(column="A", row=row+41),
                                         bold, 'Enter POOL details below',
                                         yellow_fill)


    def write_pool_header(self, headers):
        #Formats
        header_format_light = self.workbook.add_format({'align':'center', 'pattern':True, 'fg_color':'#DCE6F1',
                                                        'bold':1,'border':1, 'align':'center', 'valign':'vcenter',
                                                        'font_size':12, 'text_wrap': True})

        header_format_dark = self.workbook.add_format({'align':'center', 'pattern':True, 'fg_color':'#B9CDE3','bold':1,
                                                       'border':1, 'align':'center', 'valign':'vcenter','font_size':12,
                                                       'text_wrap': True})

        subheader_format_light = self.workbook.add_format({'align':'center', 'pattern':True, 'fg_color':'#DCE6F1',
                                                           'bold':1, 'border':1, 'align':'center', 'valign':'bottom',
                                                           'font_size':10, 'font_color':'red', 'text_wrap': True})

        subheader_format_dark = self.workbook.add_format({'align':'center', 'pattern':True, 'fg_color':'#B9CDE3',
                                                          'bold':1, 'border':1, 'align':'center', 'valign':'bottom',
                                                          'font_size':10, 'font_color':'red', 'text_wrap': True})

        comment_format = self.workbook.add_format({'align':'center', 'pattern':True, 'fg_color':'#D89595', 'bold':1,
                                                   'right':1, 'left':1, 'bottom':6, 'align':'center',
                                                   'valign':'vcenter', 'font_size':10, 'font_color':'black'})

        comment_box = {'x_scale':2, 'y_scale':2}
        span = "{column}{row}:{column_end}{row_end}"


        row_num = self.pool_start - 2
        self.worksheet.set_row(row_num, 85)

        column_count = 0
        header_count = 0

        for k,v in headers.iteritems():
            # Catch the "Additional Comments" column and make it span 2 rows
            if k == "Additional Comments":
                input_cell = span.format(column=self.columns[column_count], row=row_num,
                                         column_end=self.columns[column_count+len(v) - 1], row_end=(row_num+1))
                comment_cell = span.format(column=self.columns[column_count], row=row_num+2,
                                         column_end=self.columns[column_count+len(v) - 1], row_end=(row_num+2))
                if header_count %2 == 0:
                    self.worksheet.merge_range(input_cell, k, header_format_light)
                else:
                    self.worksheet.merge_range(input_cell, k, header_format_dark)

                self.worksheet.write(comment_cell, "", comment_format)

            else:
                input_cell = span.format(column=self.columns[column_count], row=row_num,
                                         column_end=self.columns[column_count+len(v) - 1], row_end=row_num)

                if header_count %2 == 0:
                    self.worksheet.merge_range(input_cell, k, header_format_light)
                else:
                    self.worksheet.merge_range(input_cell, k, header_format_dark)


                subheader_count = column_count
                for k2,v2 in v.iteritems():
                    input_cell = span.format(column=self.columns[subheader_count], row=row_num+1,
                                             column_end=self.columns[subheader_count], row_end=row_num+1)
                    if header_count %2 == 0:
                        self.worksheet.write(input_cell, k2, subheader_format_light)
                    else:
                        self.worksheet.write(input_cell, k2, subheader_format_dark)

                    if v2[0] != "None":
                        comment_cell = span.format(column=self.columns[subheader_count], row=row_num+2,
                                                   column_end=self.columns[subheader_count], row_end=row_num+2)
                        self.worksheet.write(comment_cell, "?", comment_format)
                        self.worksheet.write_comment(comment_cell, v2[0], comment_box)

                    else:
                        comment_cell = span.format(column=self.columns[subheader_count], row=row_num+2,
                                                   column_end=self.columns[subheader_count], row_end=row_num+2)
                        self.worksheet.write(comment_cell, "", comment_format)

                    subheader_count += 1

            header_count += 1
            column_count = column_count + len(v)


    def write_sample_header(self, headers):
        #Formats
        header_format_light = self.workbook.add_format({'pattern':True, 'fg_color':'#EBF1DF', 'bold':1,'border':1,
                                                        'align':'center', 'valign':'vcenter', 'font_size':12,
                                                        'text_wrap': True})

        header_format_dark = self.workbook.add_format({'pattern':True, 'fg_color':'#D8E3BD', 'bold':1, 'border':1,
                                                       'align':'center', 'valign':'vcenter','font_size':12, 'text_wrap': True})

        subheader_format_light_blue = self.workbook.add_format({'pattern':True, 'fg_color':'#EBF1DF', 'bold':1,
                                                                'border':1, 'align':'center', 'valign':'bottom',
                                                                'font_size':10, 'font_color':'03158A', 'text_wrap': True})

        subheader_format_dark_blue = self.workbook.add_format({'pattern':True, 'fg_color':'#D8E3BD', 'bold':1,
                                                               'border':1, 'align':'center', 'valign':'bottom',
                                                               'font_size':10, 'font_color':'03158A', 'text_wrap': True})

        subheader_format_light_red = self.workbook.add_format({'pattern':True, 'fg_color':'#EBF1DF', 'bold':1,
                                                               'border':1, 'align':'center', 'valign':'bottom',
                                                               'font_size':10, 'font_color':'red', 'text_wrap': True})

        subheader_format_dark_red = self.workbook.add_format({'pattern':True, 'fg_color':'#D8E3BD', 'bold':1,
                                                              'border':1, 'align':'center', 'valign':'bottom',
                                                              'font_size':10, 'font_color':'red', 'text_wrap': True})

        comment_format = self.workbook.add_format({'pattern':True, 'fg_color':'#D89595','bold':1, 'right':1, 'left':1,
                                                   'bottom':6, 'align':'center', 'font_size':10, 'font_color':'black'})

        comment_box = {'x_scale':2, 'y_scale':2}
        span = "{column}{row}:{column_end}{row_end}"

        row_num = self.sample_start - 2
        self.worksheet.set_row(row_num, 85)


        column_count = 0
        header_count = 0
        for k,v in headers.iteritems():
            input_cell = span.format(column=self.columns[column_count], row=row_num,
                                     column_end=self.columns[column_count+len(v) - 1], row_end=row_num)

            if len(v) == 1:
                if header_count %2 == 0:
                    self.worksheet.write(input_cell, k, header_format_light)
                else:
                    self.worksheet.write(input_cell, k, header_format_dark)
            else:
                if header_count %2 == 0:
                    self.worksheet.merge_range(input_cell, k, header_format_light)
                else:
                    self.worksheet.merge_range(input_cell, k, header_format_dark)

            subheader_count = column_count
            for k2,v2 in v.iteritems():
                input_cell = span.format(column=self.columns[subheader_count], row=row_num+1,
                                         column_end=self.columns[subheader_count], row_end=row_num+1)

                if header_count %2 == 0:
                    if v2[1] == True:
                        self.worksheet.write(input_cell, k2, subheader_format_light_red)
                    else:
                        self.worksheet.write(input_cell, k2, subheader_format_light_blue)
                else:
                    if v2[1] == True:
                        self.worksheet.write(input_cell, k2, subheader_format_dark_red)
                    else:
                        self.worksheet.write(input_cell, k2, subheader_format_dark_blue)


                if v2[0] != "None":
                    comment_cell = span.format(column=self.columns[subheader_count], row=row_num+2,
                                               column_end=self.columns[subheader_count], row_end=row_num+2)
                    self.worksheet.write(comment_cell, "?", comment_format)
                    self.worksheet.write_comment(comment_cell, v2[0], comment_box)

                else:
                    comment_cell = span.format(column=self.columns[subheader_count], row=row_num+2,
                                               column_end=self.columns[subheader_count], row_end=row_num+2)
                    self.worksheet.write(comment_cell, "", comment_format)

                subheader_count += 1
            header_count += 1
            column_count = column_count + len(v)
