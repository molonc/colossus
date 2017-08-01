import argparse
import pandas as pd


def write_excel(filename, sheets):
    writer = pd.ExcelWriter(filename)
    for sheet_name, sheet_data in sheets.iteritems():
        sheet_data.to_excel(writer, sheet_name, index=False)
    writer.save()


def convert_from_v1(args):
    data = pd.read_excel(args['input_results'], sheetname=None)

    # Update summary sheet
    data['Summary'].rename(columns={'Spot_Class': 'Condition'}, inplace=True)
    data['Summary']['Rev_Class'] = 'Auto'

    # Create region meta data
    regions = data['Summary'][['Condition']].drop_duplicates().rename(columns={'Condition': 'Region'})
    regions = regions[regions['Region'] != '~']
    regions = regions[regions['Region'].notnull()]
    regions['Sample_ID'] = args['sample_id']
    data['Region_Meta_Data'] = regions

    write_excel(args['output_results'], data)


def add_v1_arguments(parser):
    parser.add_argument('input_results', help='SmartChipApp results filename')
    parser.add_argument('output_results', help='Output SmartChipApp results filename')
    parser.add_argument('sample_id', help='Sample ID for all spots')
    parser.set_defaults(func=convert_from_v1)


def convert_from_v2_prelim(args):
    data = pd.read_excel(args['input_results'], sheetname=None)

    data['Region_Meta_Data'] = pd.read_excel(args['input_data'], sheetname='Region Meta Data')

    region_codes = pd.read_excel(args['input_data'], sheetname='Region Codes')

    # Stack to create row, column, code table
    region_codes.index.name = 'Row'
    region_codes.columns.name = 'Column'
    region_codes = region_codes.stack().rename('Condition').reset_index()

    # Update summary sheet
    data['Summary']['Rev_Class'] = 'Auto'
    data['Summary'].drop(['Sample_Type', 'Spot_Class'], axis=1, inplace=True)
    data['Summary'] = data['Summary'].merge(region_codes, how='left')
    assert data['Summary']['Condition'].notnull().any()

    write_excel(args['output_results'], data)


def add_v2_prelim_arguments(parser):
    parser.add_argument('input_data', help='SmartChipApp input data filename')
    parser.add_argument('input_results', help='SmartChipApp results filename')
    parser.add_argument('output_results', help='Output SmartChipApp results filename')
    parser.set_defaults(func=convert_from_v2_prelim)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()
    add_v1_arguments(subparsers.add_parser('v1'))
    add_v2_prelim_arguments(subparsers.add_parser('v2_prelim'))

    args = vars(parser.parse_args())

    args['func'](args)


