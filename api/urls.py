"""
Created on July 25, 2017

@author: Jessica Ngo (jngo@bccrc.ca)
"""

from django.conf.urls import url, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, routers
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
app_name='api'
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
