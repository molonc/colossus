
#reverse map
MAPPING = {
    "Patient" : "P", "Cell Line" : "C", "Xenograft" : "X", "Other" : "O",
    "Primary" : "PR", "Recurrent or Relapse" : "RC", "Metastatic" : "ME", "Remission": "RM",
}

#fields to filter
PROJECT = ["name", "description"]
SAMPLE = ["sample_id", "taxonomy_id", "anonymous_patient_id", "cell_line_id",
                 "xenograft_id", "xenograft_recipient_taxonomy_id", "xenograft_treatment_status", "strain", "notes",
                 "additionalsampleinformation__cancer_type",
                 "additionalsampleinformation__cancer_subtype",
                 "additionalsampleinformation__disease_condition_health_status",
                 "additionalsampleinformation__anatomic_site",
                 "additionalsampleinformation__anatomic_sub_site",
                 "additionalsampleinformation__developmental_stage",
                 "additionalsampleinformation__cell_type",
                 "additionalsampleinformation__pathology_disease_name",
                 "additionalsampleinformation__additional_pathology_info", "additionalsampleinformation__grade",
                 "additionalsampleinformation__stage", "additionalsampleinformation__tumour_content",
                 "additionalsampleinformation__family_information"]

ANALYSIS = ["input_type", "version", "jira_ticket", "run_status", "description"]

CORE_LIBRARY = ["description", "result"]
DLP_LIBRARY = ["pool_id", "jira_ticket", "title",
                    "dlplibrarysampledetail__spotting_location",
                     "dlplibrarysampledetail__cell_state",
                     "dlplibrarysampledetail__label_of_original_sample_vial",
                     "dlplibrarysampledetail__lims_vial_barcode",
                     "dlplibrarysampledetail__sample_notes", "dlplibrarysampledetail__sample_preparation_method",
                     "dlplibrarysampledetail__sample_preservation_method",

                     "dlplibraryconstructioninformation__chip_format",
                     "dlplibraryconstructioninformation__library_construction_method",
                     "dlplibraryconstructioninformation__library_type",
                     "dlplibraryconstructioninformation__library_notes", "dlplibraryconstructioninformation__protocol",
                     "dlplibraryconstructioninformation__spotting_location",

                     "dlplibraryquantificationandstorage__qc_check", "dlplibraryquantificationandstorage__qc_notes",
                     "dlplibraryquantificationandstorage__dna_volume",
                     "dlplibraryquantificationandstorage__freezer",
                     "dlplibraryquantificationandstorage__library_tube_label",
                     "dlplibraryquantificationandstorage__quantification_method",
                     "dlplibraryquantificationandstorage__size_range",
                     "dlplibraryquantificationandstorage__size_selection_method",
                     "dlplibraryquantificationandstorage__storage_medium"]

PBAL_LIBRARY = ["pballibrarysampledetail__spotting_location", "pballibrarysampledetail__cell_state",
                      "pballibrarysampledetail__label_of_original_sample_vial",
                      "pballibrarysampledetail__lims_vial_barcode", "pballibrarysampledetail__sample_notes",
                      "pballibrarysampledetail__sample_preparation_method",
                      "pballibrarysampledetail__sample_preservation_method",

                      "pballibraryconstructioninformation__format",
                      "pballibraryconstructioninformation__library_construction_method",
                      "pballibraryconstructioninformation__library_type",
                      "pballibraryconstructioninformation__library_prep_location",

                      "pballibraryquantificationandstorage__qc_check", "pballibraryquantificationandstorage__qc_notes"]

TENX_LIBRARY = ["name", "jira_ticket", "condition", "google_sheet", "tenxlibrarysampledetail__sorting_location",
                      "tenxlibrarysampledetail__cell_state",
                      "tenxlibrarysampledetail__label_of_original_sample_vial",
                      "tenxlibrarysampledetail__lims_vial_barcode",
                      "tenxlibrarysampledetail__sample_notes", "tenxlibrarysampledetail__sample_preparation_method",
                      "tenxlibrarysampledetail__sample_preservation_method",

                      "tenxlibraryconstructioninformation__library_construction_method",
                      "tenxlibraryconstructioninformation__library_type",
                      "tenxlibraryconstructioninformation__library_prep_location",
                      "tenxlibraryconstructioninformation__index_used", "tenxlibraryconstructioninformation__pool",
                      "tenxlibraryconstructioninformation__chemistry_version",

                      "tenxlibraryquantificationandstorage__qc_check", "tenxlibraryquantificationandstorage__qc_notes"]

TENX_CHIP = ["lab_name"]

CORE_SEQUENCING = ["adapter", "format_for_data_submission", "index_read_type", "read_type", "sequencing_instrument",
                   "sequencing_output_mode", "short_description_of_submission", "gsc_library_id",
                   "sequencer_id", "sequencing_center", "sequencer_notes"]

DLP_SEQUENCING = ["rev_comp_override", "dlplane__flow_cell_id", "dlplane__path_to_archive"]
PBAL_SEQUENCING = ["pballane__flow_cell_id", "pballane__path_to_archive"]
TENX_SEQUENCING = ["tenxlane__flow_cell_id", "tenxlane__path_to_archive"]

CORE_ANALYSES = [ "priority_level", "smoothing", "verified", "reference_genome__reference_genome", "version__version", "analysis_jira_ticket"]

TENX_ANALYSES = ["genome"]
