"""
Created on June 6, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated Nov 21, 2017 by Spencer Vatrt-Watts (github.com/Spenca)
"""
import csv
import os, sys, io
import re

import pandas as pd
import numpy as np
import requests
import yaml
from string import Template
from collections import OrderedDict
from datetime import date, datetime, timedelta

#===============
# Django imports
#---------------
from django.db.models import Count, Q, F
from django.http import HttpResponse

from sisyphus.models import DlpAnalysisInformation
from tenx.models import TenxPool
from .models import Sample, SublibraryInformation, ChipRegion, ChipRegionMetadata, MetadataField, DoubletInformation, \
    PipelineTag

from dlp.models import (
    DlpLane,
    DlpSequencing
)
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

#============================
# Pipeline Status
#----------------------------
def get_sequence_date_from_library(library):
    sequencing_set = library.dlpsequencing_set.all()
    return max([sequencing.submission_date for sequencing in sequencing_set]) if sequencing_set else  None

def analysis_info_dict(analysis):
    submission_date = get_sequence_date_from_library(analysis.library)

    return { "jira": analysis.analysis_jira_ticket,
            "lanes": analysis.lanes.count(),
            "version": analysis.version.version,
            "run_status": analysis.analysis_run.run_status,
            "aligner": "bwa-aln" if analysis.aligner is "A" else "bwa-mem",
            "submission": submission_date if submission_date else analysis.analysis_run.analysis_submission_date,
            "last_updated": analysis.analysis_run.last_updated.date() if analysis.analysis_run.last_updated else None}

def validate_imported(jira):
    analysis = DlpAnalysisInformation.objects.get(analysis_jira_ticket=jira)
    val = all([ a.imported() for a in analysis.library.dlpsequencing_set.all()])
    return val

def get_wetlab_analyses():
    sample_list = []
    analyses = DlpAnalysisInformation.objects.filter(analysis_run__last_updated__gte=datetime.now() - timedelta(days=14))
    sequencings = DlpSequencing.objects.annotate(lane_count=Count('dlplane')).filter(Q(lane_count=0)|Q(lane_count__lt=F('number_of_lanes_requested')))
    for s in sequencings.all():
        if not s.library.history.earliest().history_date.date() < date(2019, 1, 1):
            analysis_iter =  s.library.dlpanalysisinformation_set.all()
            if analysis_iter:
                for analysis in analysis_iter:
                    sample_list.append({**analysis_info_dict(analysis),
                        **{"id": s.library.sample.pk, "name": s.library.sample.sample_id, "library": s.library.pool_id}})
            else: sample_list.append({**{"submission" : get_sequence_date_from_library(s.library), 
                "id": s.library.sample.pk, "name": s.library.sample.sample_id, "library": s.library.pool_id}})
    for a in analyses.all():
        if not a.library.history.earliest().history_date.date() < date(2019, 1, 1):
            sample_list.append({**analysis_info_dict(a),
                                    **{"id": a.library.sample.pk, "name": a.library.sample.sample_id,
                                       "library": a.library.pool_id}})
    return sample_list

def fetch_montage():
    r = requests.get('https://52.235.35.201/_cat/indices', verify=False, auth=("guest", "shahlab!Montage")).text
    return [j.replace("sc","SC") for j in re.findall('sc-\d{4}', r)]

def get_sample_info(id):
    sample_list = []
    samples = PipelineTag.objects.get(id=id).sample_set.all()
    for s in samples:
        sample_dict = {"id": s.pk, "name": s.sample_id}
        sample_imported = True
        libraries = s.dlplibrary_set.all()
        if libraries:
            for d in libraries:
                analysis_set = d.dlpanalysisinformation_set.all()
                if analysis_set:
                    for analysis in analysis_set:
                        sample_list.append({**sample_dict, **{"library" : d.pool_id}, **analysis_info_dict(analysis)})
                else:
                    sample_list.append({**sample_dict, **{"library" : d.pool_id, "submission" : get_sequence_date_from_library(d)}})
        else: sample_list.append(sample_dict)
    return sample_list


#==================================================
# Upload, parse and populate Sublibrary Information
#--------------------------------------------------
def read_excel_sheets(filename, sheetnames):
    """ Read the excel sheet.
    """
    try:
        data = pd.read_excel(filename, sheet_name=None)
    except IOError:
        raise ValueError('unable to find file', filename)
    for sheetname in sheetnames:
        if sheetname not in data:
            raise ValueError('unable to read sheet(s)', sheetname)
        yield data[sheetname]


def check_smartchip_row(index, smartchip_row):
    row_sum = sum(smartchip_row)

    single_matrix = np.identity(3)
    doublet_matrix = np.identity(3)*2

    # Row does not have cells
    if smartchip_row == [0,0,0]:
        cell = None

    # TODO: Clean up code; use identity matrices
    # Row is singlet
    elif row_sum == 1:
        for row in range(len(smartchip_row)):
            if np.array_equal(smartchip_row, single_matrix[row]):
                cell = [row,0]

    # Row is doublet and is strictly live/dead/other
    elif row_sum == 2 and len(np.where(np.array(smartchip_row) == 0)[0]) == 2:
        for row in range(len(smartchip_row)):
            if np.array_equal(smartchip_row, doublet_matrix[row]):
                cell = [row,1]

    # Row is doublet but mixed
    elif row_sum == 2 and len(np.where(np.array(smartchip_row) == 0)[0]) != 2:
        cell = [2,1]

    # Greater than doublet row and row is multiple of unit vector
    elif row_sum > 2 and row_sum in smartchip_row:
        non_zero_index = np.where(smartchip_row != 0)
        cell = [non_zero_index[0][0],2]

    else:
        cell = [2,2]

    return cell


def generate_doublet_info(filename):
    """ Read SmartChipApp results and record doublet info
    """

    col_names = ["live", "dead", "other"]
    row_names = ["single", "doublet", "more_than_doublet"]

    data = np.zeros((3,3))
    doublet_table = pd.DataFrame(data, columns=col_names, index=row_names, dtype=int)

    results = pd.read_excel(filename, sheet_name="Summary")
    results = results[results["Condition"] != "~"]

    for index, row in results.iterrows():
        smartchip_row = [row["Num_Live"], row["Num_Dead"], row["Num_Other"]]
        override_row = [row["Rev_Live"], row["Rev_Dead"], row["Rev_Other"]]
        if np.array_equal(override_row, [-1, -1, -1]):
            cell = check_smartchip_row(index, smartchip_row)

        else:
            cell = check_smartchip_row(index, override_row)

        if cell is not None:
            doublet_table[col_names[cell[0]]][row_names[cell[1]]] += 1

    return doublet_table

def parse_smartchipapp_results_file(filename):
    """ Parse the result file of SmartChipApp.
    """
    results, region_metadata = read_excel_sheets(filename, ['Summary', 'Region_Meta_Data'])

    # filter out the cells whose Spot_Well value is not NaN
    results = results[~results['Spot_Well'].isnull()]
    results = results.sort_values(by='Sample')

    # change the column names to match the filed names of the model
    results.columns = [c.lower() for c in results.columns]
    region_metadata.columns = [c.lower() for c in region_metadata.columns]

    # Lower case metadata field names and check if column exists in metadata fields
    # region_metadata.columns = [c.lower() for c in region_metadata.columns]
    for c in region_metadata.columns:
        if c not in MetadataField.objects.all().values_list('field', flat=True) and c!= "region":
            raise ValueError('invalid metadata column: {col_name}'.format(col_name=c))

    region_metadata.columns.name = 'metadata_field'
    region_metadata.rename(columns={'region': 'region_code'}, inplace=True)
    region_metadata = region_metadata.set_index('region_code').stack().rename('metadata_value').reset_index()

    return results, region_metadata

def create_sublibrary_models(library, sublib_results, region_metadata):
    """ Create sublibrary models from SmartChipApp Tables
    """

    # Populate the ChipRegion and ChipRegionMetadata from the SmartChipApp results
    chip_spot_region_id = {}
    chip_spot_sample_id = {}
    for code, metadata in region_metadata.groupby('region_code'):
        chip_region = ChipRegion(region_code=code)
        chip_region.library_id = library.pk
        chip_region.save()
        sample_id = None
        for idx, row in metadata.iterrows():
            row['metadata_field'] = row['metadata_field'].lower()
            chip_region_metadata = ChipRegionMetadata(
                metadata_field=MetadataField.objects.get(field=row['metadata_field']),
                metadata_value=row['metadata_value'])
            chip_region_metadata.chip_region_id = chip_region.id
            chip_region_metadata.save()
            if row['metadata_field'] == 'sample_id':
                sample_id = row['metadata_value']
        if sample_id is None:
            raise ValueError('No sample id for region {}'.format(code))
        try:
            #Need to encode as ascii and ignore special characters, otherwise we get sample IDs like 'SA1151\xa0' instead of 'SA1151'
            sample = Sample.objects.get(sample_id=sample_id.encode('ascii', 'ignore'))
        except Sample.DoesNotExist:
            raise ValueError('Unrecognized sample {}'.format(sample_id))
        for idx, row in sublib_results[sublib_results['condition'] == code].iterrows():
            chip_spot_region_id[(row['row'], row['column'])] = chip_region.id
            chip_spot_sample_id[(row['row'], row['column'])] = sample
    # Populate the Sublibrary from the SmartChipApp input and results
    for idx, row in sublib_results.iterrows():
        row = row.drop('rev_class')
        sublib = SublibraryInformation(**row.to_dict())
        sublib.library_id = library.pk
        try:
            sublib.chip_region_id = chip_spot_region_id[(row['row'], row['column'])]
            sublib.sample_id = chip_spot_sample_id[(row['row'], row['column'])]
            sublib.save()
        except KeyError:
            raise ValueError('Undefined condition in metadata at row, column: {}, {}'.format(row['row'], row['column']))
    library.num_sublibraries = len(sublib_results.index)
    library.save()


def create_doublet_info_model(library, doublet_info):

    doublet_info = DoubletInformation(
        live_single=doublet_info["live"]["single"],
        dead_single=doublet_info["dead"]["single"],
        other_single=doublet_info["other"]["single"],
        live_doublet=doublet_info["live"]["doublet"],
        dead_doublet=doublet_info["dead"]["doublet"],
        other_doublet=doublet_info["other"]["doublet"],
        live_gt_doublet=doublet_info["live"]["more_than_doublet"],
        dead_gt_doublet=doublet_info["dead"]["more_than_doublet"],
        other_gt_doublet=doublet_info["other"]["more_than_doublet"],
    )
    doublet_info.library_id = library.pk
    doublet_info.save()


#=================
# History manager
#-----------------
class HistoryManager(object):

    """
    An api for simple_history app.
    """

    @staticmethod
    def print_history(object, history_type=None):
        print('=' * 100)
        print("Object\tID\tDate\tAction\tUser")
        print( '=' * 100)
        if history_type is None:
            histories = object.history.all()
        else:
            histories = object.history.filter(history_type=history_type)

        for h in histories:
            print( "\t".join([
                str(h.instance),
                str(h.instance.id),
                str(h.history_date),
                h.get_history_type_display(),
                str(h.history_user),
                ]))
            print( '-' * 100)


def generate_tenx_pool_sample_csv(id):
    buffer = io.StringIO()
    pool = TenxPool.objects.get(id=id)
    list_of_dict = []
    for library in pool.libraries.all():
        index = library.tenxlibraryconstructioninformation.index_used
        list_of_dict.append({
            "lane" : "*" ,
            "sample" : library.name,
            "index" : index.split(",")[0] if index else "None"})

    wr = csv.DictWriter(buffer, fieldnames=["lane","sample","index"])
    wr.writeheader()
    wr.writerows(list_of_dict)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}_tenxpool_sample.csv'.format(pool.id)
    return response


#======================
# Generate sample sheet
#----------------------
def generate_samplesheet(pk, wdir=None):
    """generate samplesheet for the given Sequencing."""
    samplesheet = SampleSheet(pk)
    sheet_name = samplesheet.sheet_name
    if wdir:
        ofilename = os.path.join(wdir, sheet_name)
    else:
        ofilename = os.path.join(settings.MEDIA_ROOT, sheet_name)
    samplesheet.write_header(ofilename)
    samplesheet.write_data(ofilename)
    return sheet_name, os.path.abspath(ofilename)

class SampleSheet(object):

    """
    Sequencing SampleSheet.
    """

    def __init__(self, pk):
        self._lane = get_object_or_404(DlpLane, pk=pk)
        self._si = self._lane.sequencing.sequencing_instrument
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
        self._rev_comp_i7 = False
        self._rev_comp_i5 = False
        # All the sequencing machines listed in the models need i7 to be reverse complemented
        if self._si != "O":
            self._rev_comp_i7 = True
        # Only the NextSeq & HX requires the i5 to be reverse complemented
        if self._si == "N550" or self._si!='HX':
            self._rev_comp_i5 = True
        rev_comp_override = self._lane.sequencing.rev_comp_override
        if rev_comp_override is not None:
            self._rev_comp_i7 = ('rev(i7)' in rev_comp_override)
            self._rev_comp_i5 = ('rev(i5)' in rev_comp_override)

    @property
    def sequencing(self):
        return self._sequencing

    @property
    def sheet_name(self):
        fc_id = self._lane.flow_cell_id
        sheet_name = 'SampleSheet_%s.csv' % fc_id
        return sheet_name

    def write_header(self, ofilename):
        """write the header section of the sequencing SampleSheet."""
        with open(self._header, 'r') as tempstr:
            s = Template(tempstr.read())
            d = {
            'sequencing_instrument': self._lane.sequencing.get_sequencing_instrument_display(),
            'submission_date': self._lane.sequencing.submission_date,
            'pool_id': self._lane.sequencing.library.pool_id,
            'read1_length': self._lane.sequencing.read1_length,
            'read2_length': self._lane.sequencing.read2_length,
            }

            # Sequencing may have no SequencingDetail
            try:
                d['flow_cell_id'] = self._lane.flow_cell_id
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
        if (len(data_table.columns)!=0):
            data_table = data_table[self._colnames]
            data_table.to_csv(ofilename, mode='a', index=False)
        else:
            ofile = open(ofilename,'w')
            ofile.write("ERROR")
            ofile.write("\nNo sublibrary data, cannot generate samplesheet\n")
            ofile.close()

    def _mk_data_table(self):
        """make data table for data section of the samplesheet template."""
        def _map_to_template(s):
            d = s.to_dict()
            # This is the relation between columns in the template samplesheet
            # and the actual columns in df from LIMS.

            # for leading 0s in samplesheet
            row = str(d['row']) if d['row'] > 9 else '0' + str(d['row'])
            col = str(d['column']) if d['column'] > 9 else '0' + str(d['column'])

            index = d['primer_i7']
            if self._rev_comp_i7:
                index = _rc(index)

            index2 = d['primer_i5']
            if self._rev_comp_i5:
                index2 = _rc(index2)

            res = {
            'Sample_ID': '-'.join([
            str(self._lane.sequencing.library.sample),
            str(self._lane.sequencing.library.pool_id),
            'R' + row,
            'C' + col
            ]),
            'Sample_Name': '',
            'Sample_Plate': 'R' + str(d['row']) + '_C' + str(d['column']),
            'Sample_Well': 'R' + str(d['row']) + '_C' + str(d['img_col']),
            'I7_Index_ID': d['index_i7'],
            'index': index,
            'I5_Index_ID': d['index_i5'],
            'index2': index2,
            'Description': 'CC=' + d['pick_met'] + ';' + 'EC=' + d['condition'],
            }
            return res

        sample_project = '' #','.join(sequencing.library.projects.names())
        newl = []
        oldl = list(self._lane.sequencing.library.sublibraryinformation_set.values())
        df = pd.DataFrame(oldl)
        for d in df.apply(_map_to_template, axis=1):
            d['Sample_Project'] = sample_project
            newl.append(d)
        return pd.DataFrame(newl)

def _rc(primer):
    "reverse complement given primer string."
    d = {'A':'T', 'C':'G', 'G':'C', 'T':'A'}
    try:
        res = ''.join([d[p] for p in primer])
    except:
        raise Exception("invalid index: %s" % primer)
    return res[::-1]

#=============================
# Generate GSC submission form
#-----------------------------
def generate_gsc_form(pk, metadata):
    """generate the GSC submission form for the given library."""
    gsc_form = GSCForm(pk,metadata["library_method"])
    pool_df = gsc_form.meta_df
    sample_df = gsc_form.data_df
    header1 = gsc_form.meta_header
    header2 = gsc_form.data_header
    form_name = gsc_form.get_form_name(metadata["sow"])
    buffer = io.BytesIO()
    workbook = Submission(pool_df, sample_df, buffer)
    workbook.set_column_width()
    workbook.write_address_box(metadata)
    workbook.write_pool_header(header1)
    workbook.write_sample_header(header2)
    workbook.close()
    return form_name, buffer

class GSCForm(object):

    """
    GSC sequencing submission form.
    """

    def __init__(self, pk,library):
        self._sequencing = get_object_or_404(DlpSequencing, pk=pk)
        self._library = self._sequencing.library
        self._library_method = library
        self._libconst = self._library.dlplibraryconstructioninformation
        self._libquant = self._library.dlplibraryquantificationandstorage
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
        'NON Chromium / Single Cell'
        'Chromium / Single Cell',
        'Size Range (bp)',
        'Average Size (bp)',
        'Number of libraries in pool',
        'Read Type',
        'Read Length',
        'Sequencer',
        'Format for data dissemination',
        'Reference genome for alignment',
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
        'Cell Type (if sorted)',
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
        'Chromium Sample Index Name', # Replaced from "Indexed? If the libraries are indexed, provide the index sequence from 5' to 3'"
        'Index Read Type (select from drop down list)',
        'Index Sequence', # Renamed from 'Dual Indices for LIMS Upload',
        'No. of cells/IP',
        'Crosslinking Method',
        'Crosslinking Time',
        'Sonication Time',
        'Antibody Used',
        'Antibody catalogue number',
        'Antibody Lot number',
        'Antibody Vendor',
        'Amount of Antibody Used(ug)',
        'Amount of Bead Used(ul)',
        'Bead Type',
        'Amount of Chromatin Used(ug)',
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
        " ",
        self._library_method,
        self._libquant.size_range,
        self._libquant.average_size,
        self._library.num_sublibraries,
        self._sequencing.get_read_type_display(),
        self._sequencing.read1_length,
        self._sequencing.get_sequencing_instrument_display(),
        self._sequencing.format_for_data_submission,
        "N/A",
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
        """return a dataframe of sublibrary information for the given library.
           NOTE: MUST use the same key values as seen in _data_colnames. """
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
        'Cell Type (if sorted)': self._sample_addinfo.cell_type,
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
        'Sample Collection Date': self._library.dlplibrarysampledetail.sample_spot_date,
        'DNA Volume (uL)': "", #self._libquant.dna_volume,
        'DNA Concentration (nM)': "", #self._libquant.dna_concentration_nm,
        'Storage Medium': "", #self._libquant.storage_medium,
        'Quantification Method': "", #self._libquant.quantification_method,
        'Library Type': self._libconst.library_type,
        'Library Construction Method': self._library_method,
        'Size Range (bp)': self._libquant.size_range,
        'Average Size (bp)': self._libquant.average_size,
        'Chromium Sample Index Name': "",
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
        'Antibody catalogue number': None,
        'Antibody Lot number': None,
        'Antibody Vendor': None,
        'Amount of Antibody Used(ug)': None,
        'Amount of Bead Used(ul)': None,
        'Bead Type': None,
        'Amount of Chromatin Used(ug)': None,
        }

        res = []
        sublib_set = self._library.sublibraryinformation_set.all()
        dual_index = lambda sl: _rc(sl.primer_i7) + '-' + sl.primer_i5
        for sl in sublib_set:
            d = {
            'Sub-Library ID': sl.get_sublibrary_id(),
            'Index Sequence': dual_index(sl),
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
    Updated by Jessica Ngo for new GSC form as of May 2017
    """

    def __init__(self, df_pool, df_samples, output):

        self.pool_start = 65
        self.sample_start = self.pool_start + len(df_pool) + 9
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
        self.worksheet.set_column('C:AO', 15)
        return self.worksheet

    def write_address_box(self, info_dict):

        HEADER = ["Deliver/ship samples on dry ice or ice pack to:",
                  "%s" % info_dict['name'],
                  "%s" % info_dict['org'],
                  "%s" % info_dict['org_gsc'],
                  "%s" % info_dict['org_bcca'],
                  "%s" % info_dict['addr'],
                  "%s" % info_dict['city'],
                  "%s" % info_dict['country'],
                  "",
                  "Email: %s" % info_dict['email'],
                  "Tel: %s" % info_dict['tel'],
                  "",
                  ]

        row = len(HEADER) + 2
        column_span = 7

        input_cell = "{column}{row}"
        nextera_compatible = "Yes" if info_dict.get('nextera_compatible') else "No"
        truseq_compatible = "Yes" if info_dict.get('truseq_compatible') else "No"
        bcgsc_standard = "Yes" if info_dict.get('bcgsc_standard') else "No"
        custom = "Yes" if info_dict.get('custom') else "No"
        pbal_library = "Yes" if info_dict.get('is_this_pbal_library') else "No"
        chromium_library = "Yes" if info_dict.get('is_this_chromium_library') else "No"
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
        teal = self.workbook.add_format({'pattern':True, 'bold':True, 'align':'right', 'bg_color':'#B7DBE7', 'border':1})

        # setting up header box border
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

        # writing header box text
        for x in range(0,len(HEADER)):
            if x == 0:
                self.worksheet.write(input_cell.format(column="A", row=x+1), HEADER[x], header)
            else:
                self.worksheet.write(input_cell.format(column="A", row=x+1), HEADER[x], text)


        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "PLEASE PROVIDE COMPLETE INFORMATION FOR YOUR SAMPLES IN THE FIELDS BELOW.  ENTER \"N/A\" IN FIELDS THAT DO NOT APPLY TO YOUR SAMPLES.", red)

        row += 2
        self.worksheet.write(input_cell.format(column="A", row=row), "Submitting Organization:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), info_dict['submitting_org'], left_align)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Name of Principal Investigator:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), info_dict['pi_name'], left_align)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Principal Investigator's email:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), info_dict['pi_email'], left_align)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Name of Submitter:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), info_dict['submitter_name'], left_align)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Submitter's email:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), info_dict['submitter_email'], left_align)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Submission Date:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), info_dict['submission_date'], left_align)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Project Name:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), info_dict['project_name'], left_align)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Statement of Work (SOW) #:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), info_dict['sow'], left_align)

        row += 3
        self.worksheet.write(input_cell.format(column="A", row=row), "**Mandatory** Library Info:", yellow)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Nextera Compatible", light_green)
        self.worksheet.write(input_cell.format(column="B", row=row), nextera_compatible)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "TruSeq Compatible", light_green)
        self.worksheet.write(input_cell.format(column="B", row=row), truseq_compatible)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "BC Genome Science Centre Standard", light_green)
        self.worksheet.write(input_cell.format(column="B", row=row), bcgsc_standard)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Custom", light_green)
        self.worksheet.write(input_cell.format(column="B", row=row), custom)

        row += 2
        self.worksheet.write(input_cell.format(column="A", row=row), "Is this is pbal Library?", peach)
        self.worksheet.write(input_cell.format(column="B", row=row), pbal_library)

        row += 2
        self.worksheet.write(input_cell.format(column="A", row=row), "Is this Chromium library?", self.workbook.add_format({'pattern':True, 'bold':True, 'align':'right', 'bg_color':'#B7DBE7', 'border':2}))
        self.worksheet.write(input_cell.format(column="B", row=row), chromium_library)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "PLEASE NOTE:", self.workbook.add_format(
            {'pattern': True, 'bold': True, 'align': 'right', 'bg_color': '#B7DBE7', 'font_color':'red', 'border':1}))
        self.worksheet.write(input_cell.format(column="B", row=row), "If yes, please provide specific chromium sample index name in Column AE. Here are some helpful links:",
                             self.workbook.add_format({'bold': True, 'font_color':'red', 'align':'left'}))

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Single cell:", teal)
        self.worksheet.write(input_cell.format(column="B", row=row), "http://support.10xgenomics.com/single-cell/sequencing/doc/specifications-sample-index-sets-for-single-cell-3")

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "Genome/Exome:", teal)
        self.worksheet.write(input_cell.format(column="B", row=row), "http://support.10xgenomics.com/genome-exome/sequencing/doc/specifications-sample-index-sets-for-genome-and-exome")

        row += 2
        self.worksheet.write(input_cell.format(column="A", row=row), "For Custom Library Info only:", dark_green); row+=1
        self.worksheet.write(input_cell.format(column="A", row=row), "Primer 1 Name:", light_green); row+=1
        self.worksheet.write(input_cell.format(column="A", row=row), "Primer 1 Sequence (with 5' and 3'):", light_green); row+=1
        self.worksheet.write(input_cell.format(column="A", row=row), "Primer 2 Name:", light_green); row+=1
        self.worksheet.write(input_cell.format(column="A", row=row), "Primer 2 Sequence (with 5' and 3'):", light_green); row+=1
        self.worksheet.write(input_cell.format(column="A", row=row), "Adaptor 1 Name:", light_green); row+=1
        self.worksheet.write(input_cell.format(column="A", row=row), "Adaptor 1 Sequence (with 5' and 3'):", light_green); row+=1
        self.worksheet.write(input_cell.format(column="A", row=row), "Adaptor 2 Name:", light_green); row+=1
        self.worksheet.write(input_cell.format(column="A", row=row), "Adaptor 2 Sequence (with 5' and 3'):", light_green); row+=2

        self.worksheet.write(input_cell.format(column="A", row=row), "At completion of project (choose one):", right_align);
        self.worksheet.write(input_cell.format(column="B", row=row), at_completion);
        self.worksheet.write(input_cell.format(column="C", row=row), "=IF(EXACT(B45, \"Destroy Unused Sample\"), \"GSC will destroy any remaining sample at completion of project\", IF(EXACT(B45,\"Return Unused Sample\"), \"GSC will return any residual sample at Submitter's expense\",\"\"))", bold)

        row += 3
        self.worksheet.write(input_cell.format(column="A", row=row), "Sample Requirements (Volume & Amounts):", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), "http://www.bcgsc.ca/services/sequencing-libraries-faq")

        row += 2
        self.worksheet.write(input_cell.format(column="A", row=row), "*NCBI Taxonomy link:", right_align)
        self.worksheet.write(input_cell.format(column="B", row=row), "http://www.ncbi.nlm.nih.gov/Taxonomy/")

        row += 2
        self.worksheet.write(input_cell.format(column="A", row=row), "PLEASE NOTE", self.workbook.add_format({'bold':True, 'font_color':'red', 'pattern':True, 'bg_color':'#F7C876', 'align':'right'}))
        self.worksheet.write(input_cell.format(column="B", row=row), "If indices are supplied, the reads will automatically be split by index.", bold)

        row += 1
        self.worksheet.write(input_cell.format(column="A", row=row), "", self.workbook.add_format({'bold':True, 'font_color':'red', 'pattern':True, 'bg_color':'#F7C876'}))
        self.worksheet.write(input_cell.format(column="B", row=row), "If the reads require splitting by index, but indices are not supplied or are incorrect, there will be a 1-2 week delay in the data processing.", bold)

        row += 2
        self.worksheet.write_rich_string(input_cell.format(column="A", row=row),
                                         bold, 'Mandatory Fields in ',
                                         red, 'RED',
                                         bold, ', Optional Fields in ',
                                         blue, 'BLUE',
                                         yellow_fill)

        row += 2
        self.worksheet.write_rich_string(input_cell.format(column="A", row=row),
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

        for k,v in headers.items():
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
                for k2,v2 in v.items():
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
        for k,v in headers.items():
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
            for k2,v2 in v.items():
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
