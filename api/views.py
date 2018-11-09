"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""
#============================
# Django & Django rest framework imports
#----------------------------
import django_filters
import rest_framework.exceptions
from rest_framework import pagination, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny


#============================
# App imports
#----------------------------
from .serializers import (
    SampleSerializer,
    LibrarySerializer,
    LaneSerializer,
    SequencingSerializer,
    SequencingDetailSerializer,
    SublibraryInformationSerializer,
    AnalysisInformationSerializer,
    AnalysisInformationCreateSerializer,
    AnalysisRunSerializer,
    ChipRegionSerializer
)

from core.models import (
    Sample,
    DlpLibrary,
    DlpSequencing,
    DlpSequencingDetail,
    DlpLane,
    SublibraryInformation,
    ChipRegion
)

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

        qs = super(RestrictedQueryMixin, self).get_queryset()

        if hasattr(self, 'filter_fields') and hasattr(self, 'filter_class'):
            raise RuntimeError("%s has both filter_fields and filter_class" % self)

        if hasattr(self, 'filter_class'):
            filter_class = getattr(self, 'filter_class', None)
            filters_dict = filter_class.get_filters()
            filters = set(filters_dict.keys())

            # Deal with DateFromToRangeFilters
            for filter_name, filter_inst in filters_dict.iteritems():
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


class SampleViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Sample that is queryable by sample_ID.
    Try adding "?sample_id=SA928" without the quotes to the end of the url.
    """

    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'sample_id',
    )


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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'flow_cell_id',
        'sequencing',
    )


class SequencingViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Sequencings.

    Sequencings are queryable by GSC library id.
    Try adding "?sequencingdetail__gsc_library_id=PX0566" without the quotes to the end of the url.

    See documentation here:
    https://www.bcgsc.ca/wiki/display/MO/Colossus+Documentation#ColossusDocumentation-ColossusRESTAPI
    """
    queryset = DlpSequencing.objects.all()
    serializer_class = SequencingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'id',
        'library',
        'dlpsequencingdetail__gsc_library_id',
        'dlpsequencingdetail__lanes_requested',
        'dlpsequencingdetail__lanes_received',
        'dlpsequencingdetail__sequencing_center',
    )

class SequencingDetailsViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Sequencing Details.
    """
    queryset = DlpSequencingDetail.objects.all()
    serializer_class = SequencingDetailSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'gsc_library_id',
        'sequencing_center',
    )


class LibraryViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Library that is queryable by pool_id (aka chip ID) and sample it belongs to.

    See documentation here:
    https://www.bcgsc.ca/wiki/display/MO/Colossus+Documentation#ColossusDocumentation-ColossusRESTAPI
    """

    queryset = DlpLibrary.objects.all()
    serializer_class = LibrarySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'id',
        'pool_id',
        'sample__sample_id',
        'jira_ticket',
        'failed',
        'projects__name',
    )


class SublibraryViewSet(RestrictedQueryMixin, viewsets.ModelViewSet):
    """
    View for Library's Sublibraries that is queryable by Library's pool_id (aka chip id)
    """
    queryset = SublibraryInformation.objects.all()
    serializer_class = SublibraryInformationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'library__pool_id',
    )


class AnalysisInformationFilter(django_filters.FilterSet):
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
    permission_classes = (AllowAny,)
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
    permission_classes = (AllowAny,)
    filter_fields = (
        'library__jira_ticket',
        'library__pool_id',
    )
