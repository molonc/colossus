"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""
#============================
# Django & Django rest framework imports
#----------------------------
import os

import django_filters
import rest_framework.exceptions
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import pagination, viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.urlresolvers import reverse

#============================
# App imports
#----------------------------
from core.utils import generate_samplesheet
from .serializers import (
    SampleSerializer,
    LibrarySerializer,
    LaneSerializer,
    SequencingSerializer,
    SublibraryInformationSerializer,
    SublibraryInformationSerializerBrief,
    AnalysisInformationSerializer,
    AnalysisInformationCreateSerializer,
    AnalysisRunSerializer,
    ChipRegionSerializer,
    JiraUserSerializer,
    TenxConditionSerializer,
    TenxLibrarySerializer,
    TenxLaneSerializer,
    TenxSequencingSerializer,
    TenxChipSerializer,
    ProjectSerializer,
    TenxPoolSerializer,
    AnalysisSerializer)

from core.models import (
    Sample,
    DlpLibrary,
    DlpSequencing,
    DlpLane,
    SublibraryInformation,
    ChipRegion,
    JiraUser,
    TenxLibrary,
    TenxSequencing,
    TenxCondition,
    TenxLane,
    TenxChip,
    Project,
    TenxPool,
    Analysis)
from pbal.models import PbalSequencing, PbalLibrary
from sisyphus.models import DlpAnalysisInformation, AnalysisRun


#============================
# Other imports
#----------------------------


class SmallResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class RestrictedQueryMixin(object):
    """Cause view to fail on invalid filter query parameter.

    Thanks to rrauenza on Stack Overflow for their post here:
    https://stackoverflow.com/questions/27182527/how-can-i-stop-django-rest-framework-to-show-all-records-if-query-parameter-is-w/50957733#50957733
    """
    def get_queryset(self):
        non_filter_params = set(['limit', 'offset', 'page', 'page_size', 'format'])

        qs = super(RestrictedQueryMixin, self).get_queryset().order_by('id')

        if hasattr(self, 'filter_fields') and hasattr(self, 'filter_class'):
            raise RuntimeError("%s has both filter_fields and filter_class" % self)

        if hasattr(self, 'filter_class'):
            filter_class = getattr(self, 'filter_class', None)
            filters_dict = filter_class.get_filters()
            filters = set(filters_dict.keys())

            # Deal with DateFromToRangeFilters
            for filter_name, filter_inst in filters_dict.items():
                if type(filter_inst) == django_filters.filters.DateFromToRangeFilter:
                    filters.update({filter_name + '_0', filter_name + '_1'})

        elif hasattr(self, 'filter_fields'):
            filters = set(getattr(self, 'filter_fields', []))
        else:
            filters = set()

        for key in self.request.GET.keys():
            if key in non_filter_params:
                continue
            if key not in filters:
                raise rest_framework.exceptions.APIException(
                    'no filter %s' % key)

        return qs


class ProjectViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Sample that is queryable by sample_ID.
    Try adding "?sample_id=SA928" without the quotes to the end of the url.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)
    filter_fields = (
        'id',
        'name',
    )


class SampleViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Sample that is queryable by sample_ID.
    Try adding "?sample_id=SA928" without the quotes to the end of the url.
    """

    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    permission_classes = (IsAuthenticated, )
    filter_fields = (
        'id',
        'sample_id',
    )

class AnalysisViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer
    filter_fields = "__all__"

class LaneViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Lanes.

    Lanes are queryable by its flowcell id.
    Try adding "?flow_cell_id=HKNHHALXX_8" without the quotes to the end of the url.

    See documentation here:
    https://www.bcgsc.ca/wiki/display/MO/Colossus+Documentation#ColossusDocumentation-ColossusRESTAPI
    """
    queryset = DlpLane.objects.all()
    serializer_class = LaneSerializer
    permission_classes = (IsAuthenticated, )
    filter_fields = (
        'id',
        'flow_cell_id',
        'sequencing',
        'sequencing__library__pool_id',
    )


class SequencingViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Sequencings.

    Sequencings are queryable by GSC library id.
    Try adding "?gsc_library_id=PX0566" without the quotes to the end of the url.

    See documentation here:
    https://www.bcgsc.ca/wiki/display/MO/Colossus+Documentation#ColossusDocumentation-ColossusRESTAPI
    """
    queryset = DlpSequencing.objects.all()
    serializer_class = SequencingSerializer
    permission_classes = (IsAuthenticated, )
    filter_fields = (
        'id',
        'library__pool_id',
        'gsc_library_id',
        'number_of_lanes_requested',
        'sequencing_center',
    )


class LibraryViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Library that is queryable by pool_id (aka chip ID) and sample it belongs to.

    See documentation here:
    https://www.bcgsc.ca/wiki/display/MO/Colossus+Documentation#ColossusDocumentation-ColossusRESTAPI
    """
    permission_classes = (IsAuthenticated, )
    queryset = DlpLibrary.objects.all()
    serializer_class = LibrarySerializer
    filter_fields = (
        'id',
        'pool_id',
        'sample__sample_id',
        'jira_ticket',
        'failed',
        'projects__name',
        'exclude_from_analysis',
    )


class SublibraryViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Library's Sublibraries that is queryable by Library's pool_id (aka chip id)
    """
    queryset = SublibraryInformation.objects.all()
    serializer_class = SublibraryInformationSerializer
    permission_classes = (IsAuthenticated, )
    filter_fields = (
        'id',
        'library__pool_id',
    )


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'


class SublibraryViewSetBrief(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Library's Sublibraries that is queryable by Library's pool_id (aka chip id)
    """
    queryset = SublibraryInformation.objects.all()
    serializer_class = SublibraryInformationSerializerBrief
    permission_classes = (IsAuthenticated, )
    pagination_class = LargeResultsSetPagination
    filter_fields = (
        'id',
        'library__pool_id',
    )


class AnalysisInformationFilter(django_filters.rest_framework.FilterSet):
    """"
    https://django-filter.readthedocs.io/en/latest/guide/usage.html
    DateFromToRangeFiler() :it uses datetime format values instead of numerical values.
    It can be used with DateTimeField.
    """
    analysis_run__last_updated = django_filters.DateFromToRangeFilter(
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


class AnalysisInformationViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Analysis Objects
    Analysis Objects are queryable by Jira ticket
    """
    queryset = DlpAnalysisInformation.objects.all()
    permission_classes = (IsAuthenticated, )
    filter_class = AnalysisInformationFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AnalysisInformationCreateSerializer

        # Use serializer with lots of nesting
        return AnalysisInformationSerializer


class AnalysisRunViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for AnalaysisRun Objects
    Should be be AllowAll so that Sisyphus can modify it
    """
    queryset = AnalysisRun.objects.all()
    serializer_class = AnalysisRunSerializer
    permission_classes = (IsAuthenticated, )
    filter_fields = (
        'id',
        'last_updated',
        'run_status',
        'dlpanalysisinformation',
        'log_file'
    )


class ExperimentalMetadata(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for ChipRegion Objects
    ChipRegion Objects are queryable by Jira ticket or library pool id
    """
    queryset = ChipRegion.objects.all()
    serializer_class = ChipRegionSerializer
    permission_classes = (IsAuthenticated, )
    filter_fields = (
        'id',
        'library__jira_ticket',
        'library__pool_id',
    )


class JiraUserViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    queryset = JiraUser.objects.all()
    serializer_class = JiraUserSerializer
    permission_classes = (IsAuthenticated, )


class TenxLibraryViewSet(RestrictedQueryMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = TenxLibrary.objects.all()
    serializer_class = TenxLibrarySerializer
    filter_fields = (
        'id',
        'name',
        'jira_ticket',
        'projects__name',
        'failed',
        'chips',
        'sample__sample_id'

    )

class TenxSequencingViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    queryset = TenxSequencing.objects.all()
    serializer_class = TenxSequencingSerializer
    permission_classes = (IsAuthenticated, )
    filter_fields = (
        'id',
        'library',
        'read_type',
        'gsc_library_id',
        'number_of_lanes_requested',
        'sequencing_center',
    )

class TenxConditionViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    queryset = TenxCondition.objects.all()
    serializer_class = TenxConditionSerializer
    permission_classes = (IsAuthenticated, )

    filter_fields = (
        'id',
        'library',
        'sample',
        'condition_id',
        'experimental_condition',
        'enzyme',
        'digestion_temperature',
        'live_dead',
        'cells_targeted'
    )

class TenxLaneViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = TenxLane.objects.all()
    serializer_class = TenxLaneSerializer
    filter_fields = (
        'id',
        'flow_cell_id',
        'sequencing',
    )

class TenxChipViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = TenxChip.objects.all()
    serializer_class = TenxChipSerializer
    filter_fields = (
        "id",
        "lab_name"
    )

class TenxPoolViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = TenxPool.objects.all()
    serializer_class = TenxPoolSerializer
    filter_fields = "__all__"

def dlp_sequencing_get_samplesheet(request, pk):

    """
    Generates downloadable samplesheet.
    """

    ofilename, ofilepath = generate_samplesheet(pk)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % ofilename
    ofile = open(ofilepath, 'r')
    response.write(ofile.read())
    ofile.close()
    os.remove(ofilepath)
    return response

def dlp_sequencing_get_queried_samplesheet(request, flowcell):

    """
    Makes downloading samplesheets from flowcell possible.
    """
    try:
        pk = DlpLane.objects.get(flow_cell_id=flowcell).pk
        return dlp_sequencing_get_samplesheet(request, pk)
    except DlpSequencing.DoesNotExist:
        msg = "Sorry, no sequencing with flowcell {} found.".format(flowcell)
        return HttpResponse(msg)
    except DlpSequencing.MultipleObjectsReturned:
        msg = "Multiple flowcells with ID {} found.".format(flowcell)
        return HttpResponse(msg)
