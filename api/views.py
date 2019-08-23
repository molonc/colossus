"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)

Updated by Spencer Vatrt-Watts (github.com/Spenca)
"""
#============================
# Django & Django rest framework imports
#----------------------------
from django.views.decorators.csrf import csrf_exempt
import json
import os
import base64
import jwt

from jira import JIRA
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.shortcuts import redirect

#============================
# App imports
#----------------------------
from api.utils import RestrictedQueryMixin
from core.search_util.search_helper import return_text_search, get_model_names
from core.utils import generate_samplesheet, generate_tenx_pool_sample_csv
from .serializers import *

from core.models import (
    SublibraryInformation,
)

from dlp.models import (
    DlpLibrary,
    DlpSequencing,
    DlpLane,
)

from tenx.models import *
from api.filters import (
    get_filter_model,
)

from sisyphus.models import DlpAnalysisInformation, AnalysisRun

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


def tenx_pool_sample_sheet(request, pk):
    return generate_tenx_pool_sample_csv(pk)


def pool_name_to_id_redirect(request, pool_name):
    pk = get_object_or_404(TenxPool, pool_name=pool_name).pk
    return redirect('api:tenx_pool_sample_sheet', pk=pk)


#============================
# KUDU API
#----------------------------
@csrf_exempt
def jira_authenticate(request):

    decoded_credentials = base64.b64decode(
        request.META['HTTP_AUTHORIZATION'].split(' ')[1]
    ).decode("utf-8").split(':')
    username = decoded_credentials[0]
    password = decoded_credentials[1] 

    try:
        jira_api = JIRA('https://www.bcgsc.ca/jira/',
                        basic_auth=(username, password), validate=True, max_retries=0)
        
        encoded = jwt.encode(
            {'username': username, 'password': password}, 'secret', algorithm='HS256')

        token = encoded.decode("utf-8")
        print("TOKEN")
        print(token)

        return HttpResponse(token)
    
    except Exception:
        return HttpResponseBadRequest(content="Invalid Credentials")

    # if request.POST:
    #     print(request)
    #     print(dir(request))
    # return HttpResponse('Hello world')
    
def kudu_search(request, query):
    model_names = get_model_names()
    result_dict = {}
    query_dict = return_text_search(query)
    result_dict['query'] = query_dict.pop('query')
    result_dict['total'] = query_dict.pop('total')
    for app in query_dict:
        if app not in model_names.keys():
            continue

        result_dict[app] = {}
        print(model_names)
        for model in query_dict[app]:
            name = model_names[app][model]["name"]
            if name == "":
                result_dict[app][model] = [dict(id=m.id, name=str(m)) for m in query_dict[app][model]]
            else:
                result_dict[app][model] = [dict(id=m.id, name=getattr(m, name)) for m in query_dict[app][model]]

    return HttpResponse(json.dumps(result_dict))


class KuduList(RestrictedQueryMixin, viewsets.ModelViewSet):
    permission_classes = (AllowAny, )
    pagination_class = None

#CORE Project
class KuduProjectList(KuduList):
    queryset = Project.objects.all()
    serializer_class = KuduProjectSerializer
    filter_class = get_filter_model(Project)

class KuduProjectDetail(KuduList):
    queryset = Project.objects.all()
    serializer_class = DetailProjectSerializer

#CORE Sample
class KuduSampleList(KuduList):
    queryset = Sample.objects.all()
    serializer_class = KuduSampleSerializer
    filter_class = get_filter_model(Sample)

class KuduSampleDetail(KuduList):
    queryset = Sample.objects.all()
    serializer_class = DetailSampleSerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#DLP Library
class KuduDLPLibraryList(KuduList):
    queryset = DlpLibrary.objects.all()
    serializer_class = KuduDLPLibraryListSerializer
    filter_class = get_filter_model(DlpLibrary)

class KuduDLPLibraryDetail(KuduList):
    queryset = DlpLibrary.objects.all()
    serializer_class = DetailDLPLibrarySerializer

#DLP Sublibrary
class KuduDLPSublibraryList(KuduList):
    queryset = SublibraryInformation.objects.all()
    serializer_class = KuduDLPSublibrariesSerializer
    filter_class = get_filter_model(SublibraryInformation)

#DLP Lane
class KuduDLPLaneList(KuduList):
    queryset = DlpLane.objects.all()
    serializer_class = KuduDLPLaneSerializer
    filter_class = get_filter_model(DlpLane)

class KuduDLPLaneDetail(KuduList):
    queryset = DlpLane.objects.all()
    serializer_class = DetailDLPLaneSerializer

#DLP Sequencing
class KuduDLPSequencingList(KuduList):
    queryset = DlpSequencing.objects.all()
    serializer_class = KuduDLPSequencingSerializer
    filter_class = get_filter_model(DlpSequencing)

class KuduDLPSequencingDetail(KuduList):
    queryset = DlpSequencing.objects.all()
    serializer_class = DetailDLPSequencingSerializer

#DLP Analysis
class KuduDLPAnalysisList(KuduList):
    queryset = DlpAnalysisInformation.objects.all()
    serializer_class = KuduDLPAnalysisSerializer
    filter_class = get_filter_model(DlpAnalysisInformation)

class KuduDLPAnalysisDetail(KuduList):
    queryset = DlpAnalysisInformation.objects.all()
    serializer_class = DetailDLPAnalysisSerializer

#TENX Library
class KuduTenxLibraryList(KuduList):
    queryset = TenxLibrary.objects.all()
    serializer_class = KuduTenxLibraryListSerializer
    filter_class = get_filter_model(TenxLibrary)

class KuduTenxLibraryDetail(KuduList):
    queryset = TenxLibrary.objects.all()
    serializer_class = DetailTenxLibrarySerializer

#TENX Chip
class KuduTenxChipList(KuduList):
    queryset = TenxChip.objects.all()
    serializer_class = KuduTenxChipSerializer
    filter_class = get_filter_model(TenxChip)

class KuduTenxChipDetail(KuduList):
    queryset = TenxChip.objects.all()
    serializer_class = DetailTenxChipSerializer

#TENX Pool
class KuduTenxPoolList(KuduList):
    queryset = TenxPool.objects.all()
    serializer_class = KuduTenxPoolSerializer
    filter_class = get_filter_model(TenxPool)

class KuduTenxPoolDetail(KuduList):
    queryset = TenxPool.objects.all()
    serializer_class = DetailTenxPoolSerializer

#TENX Sequencing
class KuduTenxSequencingList(KuduList):
    queryset = TenxSequencing.objects.all()
    serializer_class = KuduTenxSequencingSerializer
    filter_class = get_filter_model(TenxSequencing)

class KuduTenxSequencingDetail(KuduList):
    queryset = TenxSequencing.objects.all()
    serializer_class = DetailTenxSequencingSerializer

#TENX Analysis
class KuduTenxAnalysisList(KuduList):
    queryset = TenxAnalysis.objects.all()
    serializer_class = KuduTenxAnalysisSerializer
    filter_class = get_filter_model(TenxAnalysis)

class KuduTenxAnalysisDetail(KuduList):
    queryset = TenxAnalysis.objects.all()
    serializer_class = DetailTenxAnalysisSerializer

#TENX Lane
class KuduTenxLaneList(KuduList):
    queryset = TenxLane.objects.all()
    serializer_class = KuduTenxLaneSerializer
    filter_class = get_filter_model(TenxLane)

class KuduTenxLaneDetail(KuduList):
    queryset = TenxLane.objects.all()
    serializer_class = DetailTenxLaneSerializer

