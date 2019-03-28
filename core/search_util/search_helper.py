from django.contrib.postgres.search import SearchVector
from django.db.models import Q

from core.models import *
from sisyphus.models import *
from core.search_util.search_fields import *


def return_text_search(query):
    context = {
        "core": {
            "Samples": [],
            "Projects": []
        },
        "dlp": {
            "Libraries": [],
            "Sequencings": [],
            "Analyses": []
        },
        "pbal": {
            "Libraries": [],
            "Sequencings": []
        },
        "tenx": {
            "Chip": [],
            "Libraries": [],
            "Sequencings": [],
            "Analyses": []
        },
        "query" : query,
        "total" : 0
    }

    context["core"]["Samples"].extend(list(Sample.objects.annotate(search=SearchVector(*SAMPLE)).filter(Q(search=query) | Q(search__icontains=query))))
    context["core"]["Projects"].extend(list(Project.objects.annotate(search=SearchVector(*PROJECT)).filter(Q(search=query) | Q(search__icontains=query))))

    context["dlp"]["Libraries"].extend(list(DlpLibrary.objects.annotate(search=SearchVector(*(CORE_LIBRARY + DLP_LIBRARY))).filter(Q(search=query) | Q(search__icontains=query))))
    context["dlp"]["Sequencings"].extend(list(DlpSequencing.objects.annotate(search=SearchVector(*(CORE_SEQUENCING + DLP_SEQUENCING))).filter(Q(search=query) | Q(search__icontains=query))))
    context["dlp"]["Analyses"].extend(list(DlpAnalysisInformation.objects.annotate(search=SearchVector(*CORE_ANALYSES)).filter(Q(search=query) | Q(search__icontains=query))))

    context["pbal"]["Libraries"].extend(list(PbalLibrary.objects.annotate(search=SearchVector(*(CORE_LIBRARY + PBAL_LIBRARY))).filter(Q(search=query) | Q(search__icontains=query))))
    context["pbal"]["Sequencings"].extend(list(PbalSequencing.objects.annotate(search=SearchVector(*(CORE_SEQUENCING + PBAL_SEQUENCING))).filter(Q(search=query) | Q(search__icontains=query))))

    context["tenx"]["Chip"].extend(list(TenxChip.objects.annotate(search=SearchVector(*TENX_CHIP)).filter(Q(search=query) | Q(search__icontains=query))))
    context["tenx"]["Libraries"].extend(list(TenxLibrary.objects.annotate(search=SearchVector(*(CORE_LIBRARY + TENX_LIBRARY))).filter(Q(search=query) | Q(search__icontains=query))))
    context["tenx"]["Sequencings"].extend(list(TenxSequencing.objects.annotate(search=SearchVector(*(CORE_SEQUENCING + TENX_SEQUENCING))).filter(Q(search=query) | Q(search__icontains=query))))
    context["tenx"]["Analyses"].extend(list(TenxAnalysisInformation.objects.annotate(search=SearchVector(*(CORE_ANALYSES + TENX_ANALYSES))).filter(Q(search=query) | Q(search__icontains=query))))

    sample_type_choices = dict((y, x) for x, y in Sample.sample_type_choices)
    if partial_key_match(query, sample_type_choices):
        context["core"]["Samples"].extend(list(Sample.objects.filter(sample_type=partial_key_match(query, sample_type_choices))))

    pathology_occurrence_choices = dict((y, x) for x, y in AdditionalSampleInformation.pathology_occurrence_choices)
    sex_choices = dict((y, x) for x, y in AdditionalSampleInformation.sex_choices)
    tissue_type_choices = dict((y, x) for x, y in AdditionalSampleInformation.tissue_type_choices)
    treatment_status_choices = dict((y, x) for x, y in AdditionalSampleInformation.treatment_status_choices)
    tissue_states = dict((y, x) for x, y in AdditionalSampleInformation.TISSUE_STATES)
    if partial_key_match(query, pathology_occurrence_choices):
        context["core"]["Samples"].extend(
            list(Sample.objects.filter(additionalsampleinformation__pathology_occurrence=partial_key_match(query, pathology_occurrence_choices))))
    # don't partial search for gender, otherwise query with text "Male" will also return the results containing "Fe'male'"
    if query in sex_choices.keys():
        context["core"]["Samples"].extend(
            list(Sample.objects.filter(additionalsampleinformation__sex__icontains=sex_choices[query])))
    if partial_key_match(query,tissue_type_choices):
        context["core"]["Samples"].extend(
            list(Sample.objects.filter(additionalsampleinformation__tissue_type=partial_key_match(query,tissue_type_choices))))
    if partial_key_match(query, treatment_status_choices):
        context["core"]["Samples"].extend(
            list(Sample.objects.filter(additionalsampleinformation__treatment_status=partial_key_match(query, treatment_status_choices))))
    if partial_key_match(query, tissue_states):
        context["core"]["Samples"].extend(
            list(Sample.objects.filter(additionalsampleinformation__tissue_state=partial_key_match(query, tissue_states))))

    cell_state = dict((y, x) for x, y in LibrarySampleDetail.cell_state_choices)
    spotting_location_choices = dict((y, x) for x, y in PbalLibrarySampleDetail.spotting_location_choices)
    if partial_key_match(query, cell_state):
        context["dlp"]["Libraries"].extend(
            list(DlpLibrary.objects.filter(dlplibrarysampledetail__cell_state=partial_key_match(query, cell_state))))
        context["pbal"]["Libraries"].extend(
            list(PbalLibrary.objects.filter(pballibrarysampledetail__cell_state=partial_key_match(query, cell_state))))
        context["tenx"]["Libraries"].extend(
            list(TenxLibrary.objects.filter(tenxlibrarysampledetail__cell_state=partial_key_match(query, cell_state))))
    if partial_key_match(query, spotting_location_choices):
        context["dlp"]["Libraries"].extend(
            list(DlpLibrary.objects.filter(dlplibrarysampledetail__spotting_location=partial_key_match(query, spotting_location_choices))))
        context["dlp"]["Libraries"].extend(
            list(DlpLibrary.objects.filter(dlplibraryconstructioninformation__spotting_location=partial_key_match(query, spotting_location_choices))))
        context["pbal"]["Libraries"].extend(
            list(PbalLibrary.objects.filter(pballibrarysampledetail__spotting_location=partial_key_match(query, spotting_location_choices))))

    chip_format_choices = dict((y, x) for x, y in DlpLibraryConstructionInformation.chip_format_choices)
    if partial_key_match(query, chip_format_choices):
        context["dlp"]["Libraries"].extend(
            list(DlpLibrary.objects.filter(dlplibraryconstructioninformation__chip_format=partial_key_match(query, chip_format_choices))))

    sequencing_instrument_choices = dict((y, x) for x, y in Sequencing.sequencing_instrument_choices)
    sequencing_output_mode_choices = dict((y, x) for x, y in Sequencing.sequencing_output_mode_choices)
    read_type_choices = dict((y, x) for x, y in Sequencing.read_type_choices)
    if partial_key_match(query, sequencing_instrument_choices):
        context["dlp"]["Sequencings"].extend(
            list(DlpSequencing.objects.filter(sequencing_instrument=partial_key_match(query, sequencing_instrument_choices))))
        context["pbal"]["Sequencings"].extend(
            list(PbalSequencing.objects.filter(sequencing_instrument=partial_key_match(query, sequencing_instrument_choices))))
        context["tenx"]["Sequencings"].extend(
            list(TenxSequencing.objects.filter(sequencing_instrument=partial_key_match(query, sequencing_instrument_choices))))
    if partial_key_match(query, sequencing_output_mode_choices):
        context["dlp"]["Sequencings"].extend(
            list(DlpSequencing.objects.filter(sequencing_output_mode=partial_key_match(query, sequencing_output_mode_choices))))
        context["pbal"]["Sequencings"].extend(
            list(PbalSequencing.objects.filter(sequencing_output_mode=partial_key_match(query, sequencing_output_mode_choices))))
        context["tenx"]["Sequencings"].extend(
            list(TenxSequencing.objects.filter(sequencing_output_mode=partial_key_match(query, sequencing_output_mode_choices))))
    if partial_key_match(query,read_type_choices):
        context["dlp"]["Sequencings"].extend(
            list(DlpSequencing.objects.filter(read_type=partial_key_match(query,read_type_choices))))
        context["pbal"]["Sequencings"].extend(
            list(PbalSequencing.objects.filter(read_type=partial_key_match(query,read_type_choices))))
        context["tenx"]["Sequencings"].extend(
            list(TenxSequencing.objects.filter(read_type=partial_key_match(query,read_type_choices))))

    rev_comp_override_choices = dict((y, x) for x, y in DlpSequencing.rev_comp_override_choices)
    if partial_key_match(query, rev_comp_override_choices):
        context["dlp"]["Sequencings"].extend(
            list(DlpSequencing.objects.filter(rev_comp_override=partial_key_match(query, rev_comp_override_choices))))

    aligner_choices = dict((y, x) for x, y in AbstractAnalysisInformation.aligner_choices)
    smoothing_choices = dict((y, x) for x, y in AbstractAnalysisInformation.smoothing_choices)
    priority_level_choices = dict((y, x) for x, y in AbstractAnalysisInformation.priority_level_choices)
    verified_choices = dict((y, x) for x, y in AbstractAnalysisInformation.verified_choices)
    if partial_key_match(query, aligner_choices):
        context["tenx"]["Analyses"].extend(list(TenxAnalysisInformation.objects.filter(aligner=partial_key_match(query, aligner_choices))))
        context["dlp"]["Analyses"].extend(list(DlpAnalysisInformation.objects.filter(aligner=partial_key_match(query, aligner_choices))))
    if partial_key_match(query, smoothing_choices):
        context["tenx"]["Analyses"].extend(list(TenxAnalysisInformation.objects.filter(smoothing=partial_key_match(query, smoothing_choices))))
        context["dlp"]["Analyses"].extend(list(DlpAnalysisInformation.objects.filter(smoothing=partial_key_match(query, smoothing_choices))))
    if partial_key_match(query, priority_level_choices):
        context["tenx"]["Analyses"].extend(list(TenxAnalysisInformation.objects.filter(priority_level=partial_key_match(query, priority_level_choices))))
        context["dlp"]["Analyses"].extend(list(DlpAnalysisInformation.objects.filter(priority_level=partial_key_match(query, priority_level_choices))))
    if partial_key_match(query, verified_choices):
        context["tenx"]["Analyses"].extend(list(TenxAnalysisInformation.objects.filter(verified=partial_key_match(query, verified_choices))))
        context["dlp"]["Analyses"].extend(list(DlpAnalysisInformation.objects.filter(verified=partial_key_match(query, verified_choices))))

    context = remove_duplicate(context)

    context["total"] = len(context["core"]["Samples"] + context["dlp"]["Libraries"] + context["dlp"]["Sequencings"]+ context["dlp"]["Analyses"] +
                           context["pbal"]["Libraries"] +  context["pbal"]["Sequencings"] +  context["tenx"]["Chip"] + context["core"]["Projects"] +
                           context["tenx"]["Libraries"] + context["tenx"]["Sequencings"] + context["tenx"]["Analyses"] )
    return context

def partial_key_match(lookup, dict):
    for key,value in dict.items():
        if lookup in key:
            return value
    return False

def remove_duplicate(context):
    context["core"]["Samples"] = list(set(context["core"]["Samples"]))
    context["dlp"]["Libraries"]  = list(set(context["dlp"]["Libraries"]))
    context["dlp"]["Sequencings"] = list(set(context["dlp"]["Sequencings"]))
    context["dlp"]["Analyses"] = list(set(context["dlp"]["Analyses"]))
    context["pbal"]["Libraries"] = list(set(context["pbal"]["Libraries"]))
    context["pbal"]["Sequencings"] = list(set(context["pbal"]["Sequencings"]))
    context["tenx"]["Chip"] = list(set(context["tenx"]["Chip"]))
    context["core"]["Projects"] = list(set(context["core"]["Projects"]))
    context["tenx"]["Libraries"] = list(set(context["tenx"]["Libraries"]))
    context["tenx"]["Sequencings"] = list(set(context["tenx"]["Sequencings"]))
    context["tenx"]["Analyses"] = list(set(context["tenx"]["Analyses"]))
    return context