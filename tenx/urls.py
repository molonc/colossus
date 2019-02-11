"""
Created Oct 23, 2017

@author: Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from core import views

app_name = 'tenx'
urlpatterns = [
    url(r'^library/(?P<pk>\d+)$', views.TenxLibraryDetail.as_view(), name='library_detail'),
    url(r'^library/list$', views.TenxLibraryList.as_view(), name='library_list'),
    url(r'^library/create/$', views.TenxLibraryCreate.as_view(), name='library_create'),
    url(r'^library/create/(?P<pk>\d+)$', views.TenxLibraryCreate.as_view(), name='library_create_from_sample'),
    url(r'^library/update/(?P<pk>\d+)$', views.TenxLibraryUpdate.as_view(), name='library_update'),
    url(r'^library/delete/(?P<pk>\d+)$', views.TenxLibraryDelete.as_view(), name='library_delete'),
    url(r'^library/create/confirm$', views.JiraTicketConfirm.as_view(), name='jira-ticket-confirm'),
    url(r'^library/delete-conditions/(?P<pk>\d+)$', views.TenxConditionsDelete.as_view(), name='library_conditions_delete'),
    url(r'^sequencing/(?P<pk>\d+)$', views.TenxSequencingDetail.as_view(), name='sequencing_detail'),
    url(r'^sequencing/list$', views.TenxSequencingList.as_view(), name='sequencing_list'),
    url(r'^sequencing/create/$', views.TenxSequencingCreate.as_view(), name='sequencing_create'),
    url(r'^sequencing/create/(?P<from_library>\d+)$', views.TenxSequencingCreate.as_view(), name='sequencing_create_from_library'),
    url(r'^sequencing/update/(?P<pk>\d+)$', views.TenxSequencingUpdate.as_view(), name='sequencing_update'),
    url(r'^sequencing/delete/(?P<pk>\d+)$', views.TenxSequencingDelete.as_view(), name='sequencing_delete'),
    url(r'^lane/create/$', views.TenxLaneCreate.as_view(), name='lane_create'),
    url(r'^lane/create/(?P<from_sequencing>\d+)$', views.TenxLaneCreate.as_view(), name='lane_create_from_sequencing'),
    url(r'^lane/update/(?P<pk>\d+)$', views.TenxLaneUpdate.as_view(), name='lane_update'),
    url(r'^lane/delete/(?P<pk>\d+)$', views.TenxLaneDelete.as_view(), name='lane_delete')
]
