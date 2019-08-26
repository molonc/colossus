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

from jira import JIRA, JIRAError
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
    JiraUser
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
# JIRA
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

def get_jira_api(encoded_credentials):
    
    try:
        print("attempting to authenticate credentials")
        decoded_credentials = jwt.decode(
            encoded_credentials, 'secret', algorithms=['HS256'])

        username = decoded_credentials["username"]
        password = decoded_credentials["password"]

        jira_api = JIRA('https://www.bcgsc.ca/jira/',
                        basic_auth=(username, password), validate=True, max_retries=0)

        return jira_api

    except JIRAError as e:
        raise JIRAError()


@csrf_exempt
def create_jira_ticket(request):

    try: 
        jira_api = get_jira_api(request.body.token)
    except:
        return HttpResponseBadRequest(content="Invalid credentials")

    task = {
        'project': {'key': 'SC'}, # todo: get project key
        'summary': request.body.title,
        'issuetype': {'name': 'Task'},
        'description': request.body.title,
    }

    task_issue = jira_api.create_issue(fields=task)
    jira_ticket = task_issue.key

    # Add watchers
    username = request.body.username
    jira_api.add_watcher(jira_ticket, username)

    # Assign task to myself
    task_issue.update(assignee={'name': username})

    return HttpResponse(jira_ticket)


@csrf_exempt
def get_jira_users(request):
    jira_users = JiraUser.objects.all().order_by('name')
    jira_users = dict(users = [dict(name=user.name, user=user.username) for user in jira_users])
    print(jira_users)
    return HttpResponse(json.dumps(jira_users))


def get_user_list():
    #Default empty choice for user_list
    user_list = []
    for user in JiraUser.objects.all().order_by('name'):
        user_list.append((user.username, user.name))
    return user_list


@csrf_exempt
def get_jira_projects(request):
    try:
        print("in jira projects")
        body = request.body.decode("utf-8")
        body_info = json.loads(body)
        print(body_info)

        jira_api = get_jira_api(body_info["token"])
        projects = sorted(
            jira_api.projects(), key=lambda project: project.name.strip())

        projects_names = dict(projects=[])
        for project in projects:
            projects_names["projects"].append(
                dict(key=project.key, name=project.name))

        # projects_names = dict(project_names=[project.key for project in projects])
        # projects_names = [dict(project=dict.fromkeys(["key", "name"])]

        print(projects_names)
        return HttpResponse(json.dumps(projects_names))

    except Exception as e:
        print(e)
        return HttpResponseBadRequest(content="Invalid credentials")

#============================
# KUDU API
#----------------------------

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

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#CORE Sample
class KuduSampleList(KuduList):
    queryset = Sample.objects.all()
    serializer_class = KuduSampleSerializer
    filter_class = get_filter_model(Sample)

class KuduSampleDetail(KuduList):
    queryset = Sample.objects.all()
    serializer_class = DetailSampleSerializer

    def create(self, request, *args, **kwargs):
        print("CREATE")
        print(request.body)


    def update(self, request, *args, **kwargs):
        print("UPDATE")
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

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

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

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#DLP Sequencing
class KuduDLPSequencingList(KuduList):
    queryset = DlpSequencing.objects.all()
    serializer_class = KuduDLPSequencingSerializer
    filter_class = get_filter_model(DlpSequencing)

class KuduDLPSequencingDetail(KuduList):
    queryset = DlpSequencing.objects.all()
    serializer_class = DetailDLPSequencingSerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#DLP Analysis
class KuduDLPAnalysisList(KuduList):
    queryset = DlpAnalysisInformation.objects.all()
    serializer_class = KuduDLPAnalysisSerializer
    filter_class = get_filter_model(DlpAnalysisInformation)

class KuduDLPAnalysisDetail(KuduList):
    queryset = DlpAnalysisInformation.objects.all()
    serializer_class = DetailDLPAnalysisSerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#TENX Library
class KuduTenxLibraryList(KuduList):
    queryset = TenxLibrary.objects.all()
    serializer_class = KuduTenxLibraryListSerializer
    filter_class = get_filter_model(TenxLibrary)

class KuduTenxLibraryDetail(KuduList):
    queryset = TenxLibrary.objects.all()
    serializer_class = DetailTenxLibrarySerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#TENX Chip
class KuduTenxChipList(KuduList):
    queryset = TenxChip.objects.all()
    serializer_class = KuduTenxChipSerializer
    filter_class = get_filter_model(TenxChip)

class KuduTenxChipDetail(KuduList):
    queryset = TenxChip.objects.all()
    serializer_class = DetailTenxChipSerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#TENX Pool
class KuduTenxPoolList(KuduList):
    queryset = TenxPool.objects.all()
    serializer_class = KuduTenxPoolSerializer
    filter_class = get_filter_model(TenxPool)

class KuduTenxPoolDetail(KuduList):
    queryset = TenxPool.objects.all()
    serializer_class = DetailTenxPoolSerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#TENX Sequencing
class KuduTenxSequencingList(KuduList):
    queryset = TenxSequencing.objects.all()
    serializer_class = KuduTenxSequencingSerializer
    filter_class = get_filter_model(TenxSequencing)

class KuduTenxSequencingDetail(KuduList):
    queryset = TenxSequencing.objects.all()
    serializer_class = DetailTenxSequencingSerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)


#TENX Analysis
class KuduTenxAnalysisList(KuduList):
    queryset = TenxAnalysis.objects.all()
    serializer_class = KuduTenxAnalysisSerializer
    filter_class = get_filter_model(TenxAnalysis)

class KuduTenxAnalysisDetail(KuduList):
    queryset = TenxAnalysis.objects.all()
    serializer_class = DetailTenxAnalysisSerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)

#TENX Lane
class KuduTenxLaneList(KuduList):
    queryset = TenxLane.objects.all()
    serializer_class = KuduTenxLaneSerializer
    filter_class = get_filter_model(TenxLane)

class KuduTenxLaneDetail(KuduList):
    queryset = TenxLane.objects.all()
    serializer_class = DetailTenxLaneSerializer

    def create(self, request, *args, **kwargs):
        print(request.body)
    def update(self, request, *args, **kwargs):
        print(request.body)
    def destroy(self, request, *args, **kwargs):
        print(request.body)


