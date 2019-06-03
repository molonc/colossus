"""
Created Oct 19, 2017

@author: Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from dlp import views
from core.views import (
    JiraTicketConfirm,
    AddWatchers
)

app_name = 'dlp'
urlpatterns = [
    url(r'^library/(?P<pk>\d+)$', views.DlpLibraryDetail.as_view(), name='library_detail'),
    url(r'^library/list$', views.DlpLibraryList.as_view(), name='library_list'),
    url(r'^library/create/$', views.DlpLibraryCreate.as_view(), name='library_create'),
    url(r'^library/create/(?P<pk>\d+)$', views.DlpLibraryCreate.as_view(), name='library_create_from_sample'),
    url(r'^library/update/(?P<pk>\d+)$', views.DlpLibraryUpdate.as_view(), name='library_update'),
    url(r'^library/delete/(?P<pk>\d+)$', views.DlpLibraryDelete.as_view(), name='library_delete'),
    url(r'^library/create/confirm$', JiraTicketConfirm.as_view(), name='jira_ticket_confirm'),
    url(r'^library/(?P<pool_id>[ABMD]\w+)$', views.library_id_to_pk_redirect),
    url(r'^sequencing/(?P<pk>\d+)$', views.DlpSequencingDetail.as_view(), name='sequencing_detail'),
    url(r'^sequencing/list$', views.DlpSequencingList.as_view(), name='sequencing_list'),
    url(r'^sequencing/create/$', views.DlpSequencingCreate.as_view(), name='sequencing_create'),
    url(r'^sequencing/create/(?P<from_library>\d+)$', views.DlpSequencingCreate.as_view(), name='sequencing_create_from_library'),
    url(r'^sequencing/create/confirm$', AddWatchers.as_view(), name='add_watchers'),
    url(r'^sequencing/update/(?P<pk>\d+)$', views.DlpSequencingUpdate.as_view(), name='sequencing_update'),
    url(r'^sequencing/delete/(?P<pk>\d+)$', views.DlpSequencingDelete.as_view(), name='sequencing_delete'),
    url(r'^sequencing/gsc_form/create/(?P<pk>\d+)$', views.DlpSequencingCreateGSCFormView.as_view(), name='sequencing_create_gsc_form'),
    url(r'^sequencing/gsc_form/download/(?P<pk>\d+)$', views.dlp_sequencing_get_gsc_form, name='sequencing_get_gsc_form'),
    url(r'^lane/create/$', views.DlpLaneCreate.as_view(), name='lane_create'),
    url(r'^lane/create/(?P<from_sequencing>\d+)$', views.DlpLaneCreate.as_view(), name='lane_create_from_sequencing'),
    url(r'^lane/update/(?P<pk>\d+)$', views.DlpLaneUpdate.as_view(), name='lane_update'),
    url(r'^lane/delete/(?P<pk>\d+)$', views.DlpLaneDelete.as_view(), name='lane_delete'),
    url(r'^summary$', views.dlp_summary_view, name='summary'),
    url(r'summary/graph_cell_counts/$', views.dlp_get_cell_graph, name='summary_graph'),
    url(r'^library/(?P<pk>\d+)/export', views.export_sublibrary_csv, name='export_sublibrary_csv'),
]
