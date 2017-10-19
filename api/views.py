"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
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
    LibrarySerializerBrief,
    )

from core.models import (
    Sample,
    Library,
    Sequencing,
    Lane,
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
    queryset = Lane.objects.all()
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
    queryset = Sequencing.objects.all()
    serializer_class = SequencingSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'sequencingdetail__gsc_library_id',
    )


class LibraryViewSet(viewsets.ModelViewSet):
    """
    View for Library that is queryable by pool_id (aka chip ID) and sample it belongs to.
    This returns with sublibrary information for use by our workflows. This is not paginated, and loads slow on browser.

    If you are browsing from the web, consider browsing through library_brief instead.

    See documentation here:
    https://www.bcgsc.ca/wiki/display/MO/Colossus+Documentation#ColossusDocumentation-ColossusRESTAPI
    """

    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = (
        'pool_id',
        'sample__sample_id',
        'jira_ticket',
    )

class LibraryBriefViewSet(LibraryViewSet):
    """
    View for Library that is the same as /library/ with the exception that it does not return sublibrary information,
    so it is much faster, and ideal for browsing.

    Libraries are queryable by their pool_id (aka chip ID) and or sample it belongs to.
    Try adding "?pool_id=A72833" or "sample__sample_id=SA532X2XB00145" without the quotes to the end of the url.

    See documentation here:
    https://www.bcgsc.ca/wiki/display/MO/Colossus+Documentation#ColossusDocumentation-ColossusRESTAPI
    """

    serializer_class = LibrarySerializerBrief
    pagination_class = SmallResultsSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)



