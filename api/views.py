"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""
#============================
# Django & Django rest framework imports
#----------------------------
from rest_framework import pagination, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly


#============================
# App imports
#----------------------------
from .serializers import (
    SampleSerializer,
    LibrarySerializer,
    LaneSerializer,
    SequencingSerializer,
    SublibraryInformationSerializer,
    )

from core.models import (
    Sample,
    DlpLibrary,
    DlpSequencing,
    DlpLane,
    SublibraryInformation,
    )


#============================
# Other imports
#----------------------------


class SmallResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class SampleViewSet(viewsets.ModelViewSet):
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


class LaneViewSet(viewsets.ModelViewSet):
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


class SequencingViewSet(viewsets.ModelViewSet):
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
        'dlpsequencingdetail__gsc_library_id',
    )


class LibraryViewSet(viewsets.ModelViewSet):
    """
    View for Library that is queryable by pool_id (aka chip ID) and sample it belongs to.

    See documentation here:
    https://www.bcgsc.ca/wiki/display/MO/Colossus+Documentation#ColossusDocumentation-ColossusRESTAPI
    """

    queryset = DlpLibrary.objects.all()
    serializer_class = LibrarySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'pool_id',
        'sample__sample_id',
        'jira_ticket',
    )


class SublibraryViewSet(viewsets.ModelViewSet):
    """
    View for Library's Sublibraries that is queryable by Library's pool_id (aka chip id)
    """
    queryset = SublibraryInformation.objects.all()
    serializer_class = SublibraryInformationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'library__pool_id',
    )

