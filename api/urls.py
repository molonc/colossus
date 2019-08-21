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
#Kudu core
router.register(r'kuduproject_list', views.KuduProjectList, base_name="kudu_project_list")
router.register(r'kuduproject_detail', views.KuduProjectDetail, base_name="kudu_project_detail")
router.register(r'kudusample_list', views.KuduSampleList, base_name="kudu_sample_list")
router.register(r'kudusample_detail', views.KuduSampleDetail, base_name="kudu_sample_detail")

#Kudu dlp
router.register(r'kududlplibrary_list', views.KuduDLPLibraryList, base_name='kudu_dlp_library_list')
router.register(r'kududlplibrary_detail', views.KuduDLPLibraryDetail, base_name='kudu_dlp_library_detail')
router.register(r'kududlpsequencing_list', views.KuduDLPSequencingList, base_name='kudu_dlp_sequencing_list')
router.register(r'kududlpsequencing_detail', views.KuduDLPSequencingDetail, base_name='kudu_dlp_sequencing_detail')
router.register(r'kududlpanalysis_list', views.KuduDLPAnalysisList, base_name='kudu_dlp_analysis_list')
router.register(r'kududlpanalysis_detail', views.KuduDLPAnalysisDetail, base_name='kudu_dlp_analysis_detail')
router.register(r'kududlpsublibrary_list', views.KuduDLPSublibraryList, base_name='kudu_dlp_sublibrary_list')
router.register(r'kududlplane_list', views.KuduDLPLaneList, base_name="kudu_dlp_lane_list")
router.register(r'kududlplane_detail', views.KuduDLPLaneDetail, base_name="kudu_dlp_lane_detail")

#Kudu tenx
router.register(r'kudutenxlibrary_list', views.KuduTenxLibraryList, base_name='kudu_tenx_library_list')
router.register(r'kudutenxlibrary_detail', views.KuduTenxLibraryDetail, base_name='kudu_tenx_library_detail')
router.register(r'kudutenxchip_list', views.KuduTenxChipList, base_name='kudu_tenx_chip_list')
router.register(r'kudutenxchip_detail', views.KuduTenxChipDetail, base_name='kudu_tenx_chip_detail')
router.register(r'kudutenxpool_list', views.KuduTenxPoolList, base_name='kudu_tenx_pool_list')
router.register(r'kudutenxpool_detail', views.KuduTenxPoolDetail, base_name='kudu_tenx_pool_detail')
router.register(r'kudutenxsequencing_list', views.KuduTenxSequencingList, base_name='kudu_tenx_sequencing_list')
router.register(r'kudutenxsequencing_detail', views.KuduTenxSequencingDetail, base_name='kudu_tenx_sequencing_detail')
router.register(r'kudutenxanalysis_list', views.KuduTenxAnalysisList, base_name="kudu_tenx_analysis_list")
router.register(r'kudutenxanalysis_detail', views.KuduTenxAnalysisDetail, base_name="kudu_tenx_analysis_detail")
router.register(r'kudutenxlane_list', views.KuduTenxLaneList, base_name="kudu_tenx_lane_list")
router.register(r'kudutenxlane_detail', views.KuduTenxLaneDetail, base_name="kudu_tenx_lane_detail")

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
    url(r'^auth/refresh/$', refresh_jwt_token),
    url(r'^auth/jira/$', views.jira_authenticate, name="jira_authenticate"),
]
