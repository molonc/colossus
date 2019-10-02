from core.utils import GSCForm
from django.shortcuts import get_object_or_404
from django.conf import settings
from tenx.models import TenxPool


class TenXGSCForm(GSCForm):
    def __init__(self, pk, info):
        self._tenxpool = get_object_or_404(TenxPool, pk=pk)
        self._libraries = self._tenxpool.libraries
        self._get_data_df()

        submission_info = dict(
            name="Andy Mungall, Room 508",
            org="Biospecimen Core",
            org_gsc="Genome Sciences Centre",
            org_bcca="BC Cancer Agency",
            addr="Suite 100, 570 West 7th Avenue",
            city="Vancouver, BC  V5Z 4S6",
            country="Canada",
            email="amungall@bcgsc.ca",
            tel="604-707-5900 ext 673251",
            submitting_org="BBCRC",
            pi_name="Samuel Aparicio",
            pi_email="pi_email",
            submitter_name=info["name"],
            submitter_email=info["email"],
            submission_date=info["date"],
            project_name="Single Cell DNA sequencing",
            sow="SOW-0297",
            nextera_compatible=True,
            truseq_compatible=False,
            custom=False,
            is_this_pbal_library=False,
            is_this_chromium_library=False,
            at_completion="R",
        )

        shipping_details_box = ["Deliver/ship samples on dry ice or ice pack to:",
            info_dict['name'],
            info_dict['org'],
            info_dict['org_gsc'],
            info_dict['org_bcca'],
            info_dict['addr'],
            info_dict['city'],
            info_dict['country'],
            "",
            f"Email: {info_dict['email']}",
            f"Tel: {info_dict['tel']}",
            "",
        ]

    def get_sublibrary_info(self):
        for library in self._libraries.all():
            print(library)
            sublibrary_info = {
                'Sub-Library ID': library.name,
                'Tube Label': "N/A",
                'Taxonomy ID': library.sample.taxonomy_id,
                'Anonymous Patient ID': library.sample.anonymous_patient_id,
                'Strain': library.sample.strain,
                'Disease Condition/Health Status': library.sample.additionalsampleinformation.disease_condition_health_status,
                'Sex': library.sample.additionalsampleinformation.get_sex_display(),
                'Sample Collection Date': library.tenxlibrarysampledetail.sample_prep_date,
                'Anatomic Site': library.sample.additionalsampleinformation.anatomic_site,
                'Anatomic Sub-Site': library.sample.additionalsampleinformation.anatomic_sub_site,
                'Developmental Stage': library.sample.additionalsampleinformation.developmental_stage,
                'Tissue Type': library.sample.additionalsampleinformation.get_tissue_type_display(),
                'Cell Type (if sorted)': library.sample.additionalsampleinformation.cell_type,
                'Cell Line ID': library.sample.cell_line_id,
                'Pathology/Disease Name (for diseased sample only)': library.sample.additionalsampleinformation.pathology_disease_name,
                'Additional Pathology Information': library.sample.additionalsampleinformation.additional_pathology_info,
                'Grade': library.sample.additionalsampleinformation.grade,
                'Stage': library.sample.additionalsampleinformation.stage,
                'Tumor content (%)': library.sample.additionalsampleinformation.tumour_content,
                'Pathology Occurrence': library.sample.additionalsampleinformation.get_pathology_occurrence_display(),
                'Treatment Status': library.sample.additionalsampleinformation.get_treatment_status_display(),
                'Family Information': library.sample.additionalsampleinformation.family_information,
                'DNA Volume (uL)': 30*len(self._libraries.all()), # this should be in analyte information
                'DNA Concentration (nM)': 4,
                'Storage Medium': "",
                'Quantification Method': "",
                'Library Type': library.tenxlibraryconstructioninformation.library_type,
                'Library Construction Method': library.tenxlibraryconstructioninformation.library_construction_method,
                'Size Range (bp)': "",
                'Average Size (bp)': "", # todo: look at description in colo1
                'Index Read Type (select from drop down list)': "Single Index (i7)",
                'Chromium Sample Index Name': library.tenxlibraryconstructioninformation.index_used.split(",")[0],
                'Index Sequence': "; ".join(library.tenxlibraryconstructioninformation.index_used.split(",")[1:]),
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

            print(sublibrary_info)
            continue


def tenxlibrary_naming_scheme(library):
    return "_".join(
        ["SCRNA10X", library.chips.lab_name, "CHIP" + str(library.chips.pk).zfill(4), str(library.chip_well).zfill(3)]
    )


def tenxpool_naming_scheme(pool):
    return "".join(["TENXPOOL", str(pool.id).zfill(4)])
