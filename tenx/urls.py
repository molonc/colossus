"""
Created Oct 23, 2017

@author: Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from tenx import views
from core.views import (
    JiraTicketConfirm,
    AddWatchers,
)

app_name = 'tenx'
urlpatterns = [
    url(r'^library/(?P<pk>\d+)$', views.TenxLibraryDetail.as_view(), name='library_detail'),
    url(r'^library/list$', views.TenxLibraryList.as_view(), name='library_list'),
    url(r'^library/create/$', views.TenxLibraryCreate.as_view(), name='library_create'),
    url(r'^library/create/(?P<pk>\d+)$', views.TenxLibraryCreate.as_view(), name='library_create_from_sample'),
    url(r'^library/update/(?P<pk>\d+)$', views.TenxLibraryUpdate.as_view(), name='library_update'),
    url(r'^library/delete/(?P<pk>\d+)$', views.TenxLibraryDelete.as_view(), name='library_delete'),
    url(r'^library/create/confirm$', JiraTicketConfirm.as_view(), name='jira_ticket_confirm'),
    url(r'^library/(?P<pool_id>[A-Z]\w+)$', views.library_id_to_pk_redirect),
    url(r'^sequencing/(?P<pk>\d+)$', views.TenxSequencingDetail.as_view(), name='sequencing_detail'),
    url(r'^sequencing/list$', views.TenxSequencingList.as_view(), name='sequencing_list'),
    url(r'^sequencing/create/$', views.TenxSequencingCreate.as_view(), name='sequencing_create'),
    url(r'^sequencing/create/confirm$', AddWatchers.as_view(), name='add_watchers'),
    url(r'^sequencing/create/(?P<from_library>\d+)$',
        views.TenxSequencingCreate.as_view(),
        name='sequencing_create_from_library'),
    url(r'^sequencing/update/(?P<pk>\d+)$', views.TenxSequencingUpdate.as_view(), name='sequencing_update'),
    url(r'^sequencing/delete/(?P<pk>\d+)$', views.TenxSequencingDelete.as_view(), name='sequencing_delete'),
    url(r'^lane/create/$', views.TenxLaneCreate.as_view(), name='lane_create'),
    url(r'^lane/create/(?P<from_sequencing>\d+)$', views.TenxLaneCreate.as_view(), name='lane_create_from_sequencing'),
    url(r'^lane/update/(?P<pk>\d+)$', views.TenxLaneUpdate.as_view(), name='lane_update'),
    url(r'^lane/delete/(?P<pk>\d+)$', views.TenxLaneDelete.as_view(), name='lane_delete'),
    url(r'^chip/list$', views.TenxChipList.as_view(), name='chip_list'),
    url(r'^chip/detail/(?P<pk>\d+)$', views.TenxChipDetail.as_view(), name='chip_detail'),
    url(r'^chip/create$', views.TenxChipCreate.as_view(), name='chip_create'),
    url(r'^chip/update/(?P<pk>\d+)$', views.TenxChipUpdate.as_view(), name='chip_update'),
    url(r'^chip/delete/(?P<pk>\d+)$', views.TenxChipDelete.as_view(), name='chip_delete'),
    url(r'^pool/list$', views.TenxPoolList.as_view(), name='pool_list'),
    url(r'^pool/detail/(?P<pk>\d+)$', views.TenxPoolDetail.as_view(), name='pool_detail'),
    url(r'^pool/create$', views.TenxPoolCreate.as_view(), name='pool_create'),
    url(r'^pool/update/(?P<pk>\d+)$', views.TenxPoolUpdate.as_view(), name='pool_update'),
    url(r'^pool/delete/(?P<pk>\d+)$', views.TenxPoolDelete.as_view(), name='pool_delete'),
    url(r'^pool/gsc_form/(?P<pk>\d+)$', views.get_gsc_submission_form, name='gsc_form'),
    url(r'^analysis/list$', views.analys_list, name='tenxanalysis_list'),
    url(r'^analysis/detail/(?P<pk>\d+)$', views.analysis_detail, name='tenxanalysis_detail'),
]
