"""Contains filters for API viewsets."""

from django.db import models
from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters import FilterSet
from django_filters import Filter, DateFromToRangeFilter
from django_filters.fields import Lookup
from core.models import (
    Sample,
    SublibraryInformation,
    Project,
)

from sisyphus.models import DlpAnalysisInformation
import re

from tenx.models import TenxAnalysis


class TenxAnalysisFilter(filters.FilterSet):
    """Filters for Analysis."""
    def __init__(self, *args, **kwargs):
        super(TenxAnalysisFilter, self).__init__(*args, **kwargs)
        self.filters["tenx_library__name"].label = "TenX Library Chip ID"

    class Meta():
        model = TenxAnalysis
        fields = {
            "id": ["exact"],
            "input_type": ["exact"],
            "version": ["exact"],
            "jira_ticket": ["exact"],
            "run_status": ["exact"],
            "tenx_library__name": ["exact"],
        }

    # TODO: Create single library filter field that takes in dlp/tenx/pbal


class ListFilter(Filter):
    def filter(self, qs, value):
        value_list = value.replace(" ", "").split(u',')
        return super(ListFilter, self).filter(qs, Lookup(value_list, 'in'))


def get_filter_model(passed_model):
    class ListFilterSet(filters.FilterSet):
        class Meta:
            model = passed_model
            fields = {"id": ["in"]}

    return ListFilterSet


class AnalysisInformationFilter(filters.FilterSet):
    """"
    https://django-filter.readthedocs.io/en/latest/guide/usage.html
    DateFromToRangeFiler() :it uses datetime format values instead of numerical values.
    It can be used with DateTimeField.
    """
    def __init__(self, *args, **kwargs):
        super(AnalysisInformationFilter, self).__init__(*args, **kwargs)
        self.filters["version__version"].label = "Analysis Version"

    analysis_run__last_updated = DateFromToRangeFilter(method='filter_analysis_run__last_updated')

    def filter_analysis_run__last_updated(self, queryset, name, value):
        if value.start:
            queryset = queryset.filter(analysis_run__last_updated__gte=value.start)

        if value.stop:
            queryset = queryset.filter(analysis_run__last_updated__lte=value.stop)

        return queryset

    # jira_tickets = ListFilter(name='analysis_jira_ticket')

    class Meta:
        model = DlpAnalysisInformation
        fields = [
            'id',
            'aligner',
            'montage_status',
            'version__version',
            'analysis_jira_ticket',
            'analysis_submission_date',
            'analysis_run__run_status',
            'analysis_run__last_updated',
            'library__pool_id',
            'reference_genome',
        ]


class CellIdFilter(filters.Filter):
    def filter(self, qs, value):
        if value:
            cell_id = value.split("-")
            return qs.filter(
                Q(library__pool_id__exact=cell_id[1]) & Q(sample_id__sample_id__exact=cell_id[0])
                & Q(row__exact=int(re.search(r'\d+', cell_id[2]).group()))
                & Q(column__exact=int(re.search(r'\d+', cell_id[3]).group()))) if len(cell_id) > 3 else []
        else:
            return qs


class SublibraryInformationFilter(filters.FilterSet):
    cell_id = CellIdFilter(label="Cell Id", name="cell_id")

    class Meta:
        model = SublibraryInformation
        fields = (
            'id',
            'library__pool_id',
            'row',
            'column',
            'sample_id__sample_id',
        )


class SampleFilter(filters.FilterSet):
    class Meta:
        model = Sample
        fields = {
            'id': ["exact"],
            'sample_id': ["exact", "contains"],
        }
