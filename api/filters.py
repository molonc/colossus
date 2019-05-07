"""Contains filters for API viewsets."""

from django.db import models
from django_filters import rest_framework as filters
from django_filters import DateFromToRangeFilter
from core.models import (
    Analysis,
)

from sisyphus.models import DlpAnalysisInformation


class AnalysisFilter(filters.FilterSet):
    """Filters for Analysis."""

    def __init__(self, *args, **kwargs):
        super(AnalysisFilter, self).__init__(*args, **kwargs)
        self.filters["dlp_library__pool_id"].label = "DLP Library Chip ID"
        self.filters["tenx_library__name"].label = "TenX Library Chip ID"

    class Meta():
        model = Analysis
        fields = {
            "input_type": ["exact"],
            "version": ["exact"],
            "jira_ticket": ["exact"],
            "run_status": ["exact"],
            "dlp_library__pool_id": ["exact"],
            "tenx_library__name": ["exact"],
        }

    # TODO: Create single library filter field that takes in dlp/tenx/pbal


class AnalysisInformationFilter(filters.FilterSet):
    """"
    https://django-filter.readthedocs.io/en/latest/guide/usage.html
    DateFromToRangeFiler() :it uses datetime format values instead of numerical values.
    It can be used with DateTimeField.
    """
    analysis_run__last_updated = DateFromToRangeFilter(
        method='filter_analysis_run__last_updated')

    def filter_analysis_run__last_updated(self, queryset, name, value):
        if value.start:
            queryset = queryset.filter(
                analysis_run__last_updated__gte=value.start)

        if value.stop:
            queryset = queryset.filter(
                analysis_run__last_updated__lte=value.stop)

        return queryset

    class Meta:
        model = DlpAnalysisInformation
        fields = [
        'priority_level',
        'analysis_jira_ticket',
        'version',
        'analysis_submission_date',
        'reference_genome',
        'analysis_run',
        'id',
        'analysis_run__run_status',
        'analysis_run__last_updated',
        'library__pool_id'
        ]
