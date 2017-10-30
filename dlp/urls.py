"""
Created Oct 19, 2017

@author: Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from core import views

app_name = 'dlp'
urlpatterns = [
    url(r'^library/(?P<pk>\d+)$', views.dlp_library_detail, name='library_detail'),
    url(r'^library/list$', views.dlp_library_list, name='library_list'),
    url(r'^library/create/$', views.DlpLibraryCreate.as_view(), name='library_create'),
    url(r'^library/create/(?P<from_sample>\d+)$', views.DlpLibraryCreate.as_view(), name='library_create_from_sample'),
    url(r'^library/update/(?P<pk>\d+)$', views.DlpLibraryUpdate.as_view(), name='library_update'),
    url(r'^library/delete/(?P<pk>\d+)$', views.dlp_library_delete, name='library_delete'),
    url(r'^sequencing/(?P<pk>\d+)$', views.dlp_sequencing_detail, name='sequencing_detail'),
    url(r'^sequencing/list$', views.dlp_sequencing_list, name='sequencing_list'),
    url(r'^sequencing/create/$', views.dlp_sequencing_create, name='sequencing_create'),
    url(r'^sequencing/create/(?P<from_library>\d+)$', views.dlp_sequencing_create, name='sequencing_create_from_library'),
    url(r'^sequencing/update/(?P<pk>\d+)$', views.dlp_sequencing_update, name='sequencing_update'),
    url(r'^sequencing/delete/(?P<pk>\d+)$', views.dlp_sequencing_delete, name='sequencing_delete'),
    url(r'^sequencing/samplesheet/download/(?P<pk>\d+)$', views.dlp_sequencing_get_samplesheet, name='sequencing_get_samplesheet'),
    url(r'^sequencing/samplesheet/query_download/(?P<pool_id>.+)/(?P<flowcell>.+)$', views.dlp_sequencing_get_queried_samplesheet, name='sequencing_get_samplesheet'),
    url(r'^sequencing/gsc_form/create/(?P<pk>\d+)$', views.DlpSequencingCreateGSCFormView.as_view(), name='sequencing_create_gsc_form'),
    url(r'^sequencing/gsc_form/download/(?P<pk>\d+)$', views.dlp_sequencing_get_gsc_form, name='sequencing_get_gsc_form'),
    url(r'^lane/create/$', views.dlp_lane_create, name='lane_create'),
    url(r'^lane/create/(?P<from_sequencing>\d+)$', views.dlp_lane_create, name='lane_create_from_sequencing'),
    url(r'^lane/update/(?P<pk>\d+)$', views.dlp_lane_update, name='lane_update'),
    url(r'^lane/delete/(?P<pk>\d+)$', views.dlp_lane_delete, name='lane_delete'),
    url(r'^summary$', views.dlp_summary_view, name='summary'),
    url(r'summary/graph_cell_counts/$', views.dlp_get_cell_graph, name='summary_graph')
]