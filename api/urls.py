"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from django.conf.urls import url, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from . import views

schema_view = get_schema_view(
   openapi.Info(
      title="Colossus API",
      default_version='v1',
   ),
   validators=['flex', 'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'project', views.ProjectViewSet, base_name='project')
router.register(r'sample', views.SampleViewSet)
router.register(r'lane', views.LaneViewSet)

router.register(r'sequencing', views.SequencingViewSet)
router.register(r'library', views.LibraryViewSet, base_name='library')
router.register(r'sublibraries', views.SublibraryViewSet, base_name='sublibraries')
router.register(r'sublibraries_brief', views.SublibraryViewSetBrief, base_name='sublibrariesbrief')
router.register(r'analysis_information', views.AnalysisInformationViewSet, base_name='analysis_information')
router.register(r'analysis_run', views.AnalysisRunViewSet, base_name='analysis_run')
router.register(r'experimental_metadata', views.ExperimentalMetadata, base_name='experimental_metadata')
router.register(r'jira_users', views.JiraUserViewSet, base_name='jira_user')

router.register(r'tenxpool', views.TenxPoolViewSet, base_name='tenxpool')
router.register(r'tenxchip', views.TenxChipViewSet, base_name='tenxchip')
router.register(r'tenxlibrary', views.TenxLibraryViewSet, base_name='tenxlibrary')
router.register(r'tenxsequencing', views.TenxSequencingViewSet, base_name='tenxsequencing')
router.register(r'tenxlane', views.TenxLaneViewSet, base_name='tenxlane')
router.register(r'tenxanalysis', views.TenxAnalysisViewSet, base_name='tenxanalysis')

#Kudu core
router.register(r'kuduproject_list', views.KuduProjectList, base_name="kudu_project_list")
router.register(r'kudusample_list', views.KuduSampleList, base_name="kudu_sample_list")

#Kudu dlp
router.register(r'kududlplibrary_list', views.KuduDLPLibraryList, base_name='kudu_dlp_library_list')
router.register(r'kududlpsequencing_list', views.KuduDLPSequencingList, base_name='kudu_dlp_sequencing_list')
router.register(r'kududlpanalysis_list', views.KuduDLPAnalysisList, base_name='kudu_dlp_analysis_list')
router.register(r'kududlpsublibrary_list', views.KuduDLPSublibraryList, base_name='kudu_dlp_sublibrary_list')
router.register(r'kududlplane_list', views.KuduDLPLaneList, base_name="kudu_dlp_lane_list")

#Kudu tenx
router.register(r'kudutenxlibrary_list', views.KuduTenxLibraryList, base_name='kudu_tenx_library_list')
router.register(r'kudutenxchip_list', views.KuduTenxChipList, base_name='kudu_tenx_chip_list')
router.register(r'kudutenxpool_list', views.KuduTenxPoolList, base_name='kudu_tenx_pool_list')
router.register(r'kudutenxsequencing_list', views.KuduTenxSequencingList, base_name='kudu_tenx_sequencing_list')
router.register(r'kudutenxanalysis_list', views.KuduTenxAnalysisList, base_name="kudu_tenx_analysis_list")
router.register(r'kudutenxlane_list', views.KuduTenxLaneList, base_name="kudu_tenx_lane_list")

app_name='api'
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^samplesheet/(?P<pk>\d+)$', views.dlp_sequencing_get_samplesheet, name='dlp_sequencing_get_queried_samplesheet'),
    url(r'^samplesheet_query/(?P<flowcell>.+)$', views.dlp_sequencing_get_queried_samplesheet, name='dlp_sequencing_get_queried_samplesheet'),
    url(r'^tenxpool_sheet/(?P<pk>\d+)$', views.tenx_pool_sample_sheet, name='tenx_pool_sample_sheet'),
    url(r'^tenxpool_sheet/(?P<pool_name>(TENXPOOL\d{4}))$', views.pool_name_to_id_redirect),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'^kudusearch/(?P<query>.+)$', views.kudu_search, name='kudu_search_query'),
    url(r'^auth/$', obtain_jwt_token),
    url(r'^auth/refresh/$', refresh_jwt_token)
]
