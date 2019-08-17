import re
from django.contrib.postgres.search import SearchVector
from django.db.models import Q

from core.models import *
from tenx.models import *
from sisyphus.models import *
from pbal.models import *
from core.search_util.search_fields import *
from core.constants import *

def return_text_search(query):
    context = {
        "core": {
            "sample": [],
            "project": []
        },
        "dlp": {
            "library": [],
            "sequencing": [],
            "analysis": []
        },
        "pbal": {
            "library": [],
            "sequencing": []
        },
        "tenx": {
            "chip": [],
            "pool": [],
            "library": [],
            "sequencing": [],
            "analysis": [],
        },
        "query" : query,
        "total" : 0
    }

    context["core"]["sample"].extend(list(Sample.objects.annotate(search=SearchVector(*SAMPLE)).filter(Q(search=query) | Q(search__icontains=query))))
    context["core"]["project"].extend(list(Project.objects.annotate(search=SearchVector(*PROJECT)).filter(Q(search=query) | Q(search__icontains=query))))

    context["dlp"]["library"].extend(list(DlpLibrary.objects.annotate(search=SearchVector(*(CORE_LIBRARY + DLP_LIBRARY))).filter(Q(search=query) | Q(search__icontains=query))))
    context["dlp"]["sequencing"].extend(list(DlpSequencing.objects.annotate(search=SearchVector(*(CORE_SEQUENCING + DLP_SEQUENCING))).filter(Q(search=query) | Q(search__icontains=query))))
    context["dlp"]["analysis"].extend(list(DlpAnalysisInformation.objects.annotate(search=SearchVector(*DLP_ANALYSES)).filter(Q(search=query) | Q(search__icontains=query))))

    context["pbal"]["library"].extend(list(PbalLibrary.objects.annotate(search=SearchVector(*(CORE_LIBRARY + PBAL_LIBRARY))).filter(Q(search=query) | Q(search__icontains=query))))
    context["pbal"]["sequencing"].extend(list(PbalSequencing.objects.annotate(search=SearchVector(*(CORE_SEQUENCING + PBAL_SEQUENCING))).filter(Q(search=query) | Q(search__icontains=query))))

    context["tenx"]["chip"].extend(list(TenxChip.objects.annotate(search=SearchVector(*TENX_CHIP)).filter(Q(search=query) | Q(search__icontains=query))))
    context["tenx"]["pool"].extend(list(TenxPool.objects.annotate(search=SearchVector(*(TENX_POOL))).filter(Q(search=query) | Q(search__icontains=query))))
    context["tenx"]["library"].extend(list(TenxLibrary.objects.annotate(search=SearchVector(*(CORE_LIBRARY + TENX_LIBRARY))).filter(Q(search=query) | Q(search__icontains=query))))
    context["tenx"]["sequencing"].extend(list(TenxSequencing.objects.annotate(search=SearchVector(*TENX_SEQUENCING)).filter(Q(search=query) | Q(search__icontains=query))))
    context["tenx"]["analysis"].extend(list(TenxAnalysis.objects.annotate(search=SearchVector(*TENX_ANALYSIS)).filter(Q(search=query) | Q(search__icontains=query))))

    dict_sample_type_choices = dict((y, x) for x, y in Sample.sample_type_choices)
    dict_run_status = dict((y, x) for x, y in RUN_STATUS_CHOICES)
    if partial_key_match(query, dict_sample_type_choices):
        context["core"]["sample"].extend(list(Sample.objects.filter(sample_type=partial_key_match(query, dict_sample_type_choices))))
    if partial_key_match(query, dict_run_status):
        context["tenx"]["analysis"].extend(list(TenxAnalysis.objects.filter(run_status=partial_key_match(query, dict_run_status))))
    dict_pathology_occurrence_choices = dict((y, x) for x, y in pathology_occurrence_choices)
    dict_sex_choices = dict((y, x) for x, y in sex_choices)
    dict_tissue_type_choices = dict((y, x) for x, y in tissue_type_choices)
    dict_treatment_status_choices = dict((y, x) for x, y in treatment_status_choices)
    dict_tissue_states = dict((y, x) for x, y in TISSUE_STATES)
    if partial_key_match(query, dict_pathology_occurrence_choices):
        context["core"]["sample"].extend(
            list(Sample.objects.filter(additionalsampleinformation__pathology_occurrence=partial_key_match(query, dict_pathology_occurrence_choices))))
    # don't partial search for gender, otherwise query with text "Male" will also return the results containing "Fe'male'"
    if query in dict_sex_choices.keys():
        context["core"]["sample"].extend(
            list(Sample.objects.filter(additionalsampleinformation__sex__icontains=dict_sex_choices[query])))
    if partial_key_match(query,dict_tissue_type_choices):
        context["core"]["sample"].extend(
            list(Sample.objects.filter(additionalsampleinformation__tissue_type=partial_key_match(query,dict_tissue_type_choices))))
    if partial_key_match(query, dict_treatment_status_choices):
        context["core"]["sample"].extend(
            list(Sample.objects.filter(additionalsampleinformation__treatment_status=partial_key_match(query, dict_treatment_status_choices))))
    if partial_key_match(query, dict_tissue_states):
        context["core"]["sample"].extend(
            list(Sample.objects.filter(additionalsampleinformation__tissue_state=partial_key_match(query, dict_tissue_states))))

    dict_cell_state = dict((y, x) for x, y in cell_state_choices)
    dict_spotting_location_choices = dict((y, x) for x, y in spotting_location_choices)
    if partial_key_match(query, dict_cell_state):
        context["dlp"]["library"].extend(
            list(DlpLibrary.objects.filter(dlplibrarysampledetail__cell_state=partial_key_match(query, dict_cell_state))))
        context["pbal"]["library"].extend(
            list(PbalLibrary.objects.filter(pballibrarysampledetail__cell_state=partial_key_match(query, dict_cell_state))))
        context["tenx"]["library"].extend(
            list(TenxLibrary.objects.filter(tenxlibrarysampledetail__cell_state=partial_key_match(query, dict_cell_state))))
    if partial_key_match(query, dict_spotting_location_choices):
        context["dlp"]["library"].extend(
            list(DlpLibrary.objects.filter(dlplibrarysampledetail__spotting_location=partial_key_match(query, dict_spotting_location_choices))))
        context["dlp"]["library"].extend(
            list(DlpLibrary.objects.filter(dlplibraryconstructioninformation__spotting_location=partial_key_match(query, dict_spotting_location_choices))))
        context["pbal"]["library"].extend(
            list(PbalLibrary.objects.filter(pballibrarysampledetail__spotting_location=partial_key_match(query, dict_spotting_location_choices))))

    dict_chip_format_choices = dict((y, x) for x, y in chip_format_choices)
    if partial_key_match(query, dict_chip_format_choices):
        context["dlp"]["library"].extend(
            list(DlpLibrary.objects.filter(dlplibraryconstructioninformation__chip_format=partial_key_match(query, dict_chip_format_choices))))

    dict_sequencing_instrument_choices = dict((y, x) for x, y in sequencing_instrument_choices)
    dict_sequencing_output_mode_choices = dict((y, x) for x, y in sequencing_output_mode_choices)
    dict_read_type_choices = dict((y, x) for x, y in read_type_choices)
    if partial_key_match(query, dict_sequencing_instrument_choices):
        context["dlp"]["sequencing"].extend(
            list(DlpSequencing.objects.filter(sequencing_instrument=partial_key_match(query, dict_sequencing_instrument_choices))))
        context["pbal"]["sequencing"].extend(
            list(PbalSequencing.objects.filter(sequencing_instrument=partial_key_match(query, dict_sequencing_instrument_choices))))
        context["tenx"]["sequencing"].extend(
            list(TenxSequencing.objects.filter(sequencing_instrument=partial_key_match(query, dict_sequencing_instrument_choices))))

    if partial_key_match(query, dict_sequencing_output_mode_choices):
        context["dlp"]["sequencing"].extend(
            list(DlpSequencing.objects.filter(sequencing_output_mode=partial_key_match(query, dict_sequencing_output_mode_choices))))
        context["pbal"]["sequencing"].extend(
            list(PbalSequencing.objects.filter(sequencing_output_mode=partial_key_match(query, dict_sequencing_output_mode_choices))))

    if partial_key_match(query,dict_read_type_choices):
        context["dlp"]["sequencing"].extend(
            list(DlpSequencing.objects.filter(read_type=partial_key_match(query,dict_read_type_choices))))
        context["pbal"]["sequencing"].extend(
            list(PbalSequencing.objects.filter(read_type=partial_key_match(query,dict_read_type_choices))))

    dict_rev_comp_override_choices = dict((y, x) for x, y in rev_comp_override_choices)
    if partial_key_match(query, dict_rev_comp_override_choices):
        context["dlp"]["sequencing"].extend(
            list(DlpSequencing.objects.filter(rev_comp_override=partial_key_match(query, dict_rev_comp_override_choices))))

    dict_aligner_choices = dict((y, x) for x, y in aligner_choices)
    dict_smoothing_choices = dict((y, x) for x, y in smoothing_choices)
    dict_priority_level_choices = dict((y, x) for x, y in priority_level_choices)
    dict_verified_choices = dict((y, x) for x, y in verified_choices)
    if partial_key_match(query, dict_aligner_choices):
        context["dlp"]["analysis"].extend(list(DlpAnalysisInformation.objects.filter(aligner=partial_key_match(query, dict_aligner_choices))))
    if partial_key_match(query, dict_smoothing_choices):
        context["dlp"]["analysis"].extend(list(DlpAnalysisInformation.objects.filter(smoothing=partial_key_match(query, dict_smoothing_choices))))
    if partial_key_match(query, dict_priority_level_choices):
        context["dlp"]["analysis"].extend(list(DlpAnalysisInformation.objects.filter(priority_level=partial_key_match(query, dict_priority_level_choices))))
    if partial_key_match(query, dict_verified_choices):
        context["dlp"]["analysis"].extend(list(DlpAnalysisInformation.objects.filter(verified=partial_key_match(query, dict_verified_choices))))

    if sublibrary_id_search(query):
        sublibrary_id_fields = sublibrary_id_search(query)
        context["dlp"]["library"].extend(list(DlpLibrary.objects.filter(pool_id=sublibrary_id_fields[1], sample__sample_id=sublibrary_id_fields[0])))

    context = remove_duplicate(context)

    context["total"] = len(context["core"]["sample"] + context["dlp"]["library"] + context["dlp"]["sequencing"]+ context["dlp"]["analysis"] +
                           context["pbal"]["library"] +  context["pbal"]["sequencing"] +  context["tenx"]["chip"] + context["core"]["project"] +
                           context["tenx"]["library"] + context["tenx"]["pool"] + context["tenx"]["sequencing"] + context["tenx"]["analysis"] )

    return context

def partial_key_match(lookup, dict):
    for key,value in dict.items():
        if lookup in key:
            return value
    return False

def sublibrary_id_search(query):
    if re.match(".+-.+-R\d{2}-C\d{2}", query):
        return query.split('-')
    return False

def remove_duplicate(context):
    context["core"]["sample"] = list(set(context["core"]["sample"]))
    context["dlp"]["library"]  = list(set(context["dlp"]["library"]))
    context["dlp"]["sequencing"] = list(set(context["dlp"]["sequencing"]))
    context["dlp"]["analysis"] = list(set(context["dlp"]["analysis"]))
    context["pbal"]["library"] = list(set(context["pbal"]["library"]))
    context["pbal"]["sequencing"] = list(set(context["pbal"]["sequencing"]))
    context["tenx"]["chip"] = list(set(context["tenx"]["chip"]))
    context["core"]["project"] = list(set(context["core"]["project"]))
    context["tenx"]["library"] = list(set(context["tenx"]["library"]))
    context["tenx"]["sequencing"] = list(set(context["tenx"]["sequencing"]))
    context["tenx"]["analysis"] = list(set(context["tenx"]["analysis"]))
    return context

def get_model_names():

    app_models = {
        "core": {
            "sample": {
                "name": "sample_id",
            },
            "project": {
                "name": "name",
            },
        },
        "dlp": {
            "library": {
                "name": "pool_id",
            },
            "sequencing": {
                "name": "",
            },
            "analysis": {
                "name": "analysis_jira_ticket",
            },
        },
        "tenx": {
            "chip": {
                "name": "name",
            },
            "pool": {
                "name": "pool_name",
            },
            "library": {
                "name": "name",
            },
            "sequencing": {
                "name": ""
            },
            "analysis": {
                "name": "jira_ticket"
            },
        }
    }

    return app_models
