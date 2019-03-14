import os
import django
import sys
import csv
import re

#dictionary for key look up, name of field in colossus differs to those in sheet0
general_naming = {
    "sample_id": "sample_id", "patient_id" : "anonymous_patient_id", "anatomic_site" : "anatomic_site", "sample_type" : "sample_type",
    "cancer_type" : "cancer_type", "cancer_subtype" : "cancer_subtype", "condition" : "condition", "tissue_state" : "tissue_state", "shahlab_path" : "path_to_archive",
    "jira_ticket" : "jira_ticket", "genome" : "genome", "GSC_BRC" : "sequencing_center", "chem_version" : "chemistry_version", "tissue_type" : "tissue_type",
}

#field lookup in models
tenxlibrary_keys = ["id", "condition", "jira_ticket"]
sample_keys = ["sample_id", "anonymous_patient_id","sample_type"]
additionalsampleinformation_keys = ["anatomic_site", "cancer_type", "cancer_subtype", "tissue_state", "tissue_type"]
sequencing_keys = ["sequencing_center"]
lane_keys = ["path_to_archive"]
tenxanalysisinformation_keys = ["genome"]
tenxlibraryconstructioninformation_keys =["chemistry_version"]

path = os.getcwd()

# Set up, otherwise unable to import django models
def setup():
    print "SET UP"

    if path not in sys.path:
        sys.path.append(path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
    django.setup()

# Read csv file and return a list of dictionaries(rows)
def read_csv(filepath):
    with open(filepath) as csv_file:
        if csv_file:
            return list(csv.DictReader(csv_file, delimiter=','))
        else:
            return None

# Return list of merged list of id from list of csv files
def get_set_id(csvs):
    return_set = set()
    for c in csvs:
        for row in c:
            return_set.add(row["id"])

    return list(return_set)

# Parse id
# Google sheet id follows a format of either TENX00ID__SAMPLE_ID__LANE_NUMBER or TENX00ID
def parse_id(id):
    id_split =  id.split("_")
    #re translation: collect integer from string TENX00ID
    id_split[0] = int(re.search(r'\d+', id_split[0]).group())
    return id_split

# SCRNA10X_[SA|DH]_CHIP00ID_lANE
def naming_convention(split_id, chip_name, lab_name):
    if len(split_id) > 1:
        return "SCRNA10X_" + lab_name + "_CHIP" +  format(chip_name, "04") + "_" + split_id[2]
    else:
        return "SCRNA10X_" + lab_name + "_CHIP" + format(chip_name, "04") + "_000"

def update_row(csvs):
    from core.models import (
        TenxLibrary,
    )


    id_list =  get_set_id(csvs)
    for id in id_list:
        id_split =  parse_id(id)
        library = TenxLibrary.objects.filter(id=id_split[0])[0]
        # do not remove below print statements
        print library.tenxlibraryconstructioninformation.id
        print library.tenxlibrarysampledetail.id
        chip = library.chips
        project = [str(tag.name) for tag in library.projects.all()]
        new_name = naming_convention(id_split, chip.id, str(chip.lab_name))
        print new_name


        if TenxLibrary.objects.filter(name=new_name).count() == 0 :
            #clone
            library.pk = None
            library.name = new_name
            library.save()

            for tag in project:
                library.projects.add(tag)

            library.tenxlibraryconstructioninformation.id = None
            library.tenxlibraryconstructioninformation.library = library
            library.tenxlibraryconstructioninformation.save()

            library.tenxlibrarysampledetail.id = None
            library.tenxlibrarysampledetail.library = library
            library.tenxlibrarysampledetail.save()

            library.tenxsequencing_set = []
            library.tenxcondition_set = []
        else:
            print "ALREADY EXIST"
            library = TenxLibrary.objects.filter(name=new_name)[0]
            for tag in project:
                library.projects.add(tag)

        for c in csvs:
            id_library = filter(lambda item: item['id'] == id, c)
            if id_library:
                for key, val in id_library[0].items():
                    if key in general_naming.keys():
                        if general_naming[key] in tenxlibrary_keys:
                            print general_naming[key]
                            library.__dict__[general_naming[key]] = val
                            library.save()
                        elif general_naming[key] in sample_keys:
                            library.sample.__dict__[general_naming[key]] = val
                            library.sample.save()
                        elif general_naming[key] in additionalsampleinformation_keys:
                            library.sample.additionalsampleinformation.__dict__[general_naming[key]] = val
                            library.sample.additionalsampleinformation.save()
                        # elif general_naming[key] in lane_keys:
                        #     pass
                        # elif general_naming[key] in sequencing_keys:
                        #     pass
                        # elif general_naming[key] in tenxanalysisinformation_keys:
                        #     pass
                        elif general_naming[key] in tenxlibraryconstructioninformation_keys:
                            library.tenxlibraryconstructioninformation.__dict__[general_naming[key]] = val
                            library.tenxlibraryconstructioninformation.save()
                    else:
                        print "KEY " + key + "is not found in Colossus. :("

                c.remove(id_library[0])




def initial_update():

    print "STARTING"
    csvs = [read_csv(path  + "/core/utility/sheet_initial/temperature_effects.csv"), read_csv(path + "/core/utility/sheet_initial/breast_scrnaseq_master.csv")]

    update_row(csvs)

if __name__ == "__main__":
    setup()
    initial_update()

