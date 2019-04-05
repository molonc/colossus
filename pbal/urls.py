"""
Created Oct 23, 2017

@author: Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from pbal import views

app_name = 'pbal'
urlpatterns = [
    url(r'^library/(?P<pk>\d+)$', views.PbalLibraryDetail.as_view(), name='library_detail'),
    url(r'^library/list$', views.PbalLibraryList.as_view(), name='library_list'),
    url(r'^library/create/$', views.PbalLibraryCreate.as_view(), name='library_create'),
    url(r'^library/create/(?P<pk>\d+)$', views.PbalLibraryCreate.as_view(), name='library_create_from_sample'),
    url(r'^library/update/(?P<pk>\d+)$', views.PbalLibraryUpdate.as_view(), name='library_update'),
    url(r'^library/delete/(?P<pk>\d+)$', views.PbalLibraryDelete.as_view(), name='library_delete'),
    url(r'^sequencing/(?P<pk>\d+)$', views.PbalSequencingDetail.as_view(), name='sequencing_detail'),
    url(r'^sequencing/list$', views.PbalSequencingList.as_view(), name='sequencing_list'),
    url(r'^sequencing/create/$', views.PbalSequencingCreate.as_view(), name='sequencing_create'),
    url(r'^sequencing/create/(?P<from_library>\d+)$', views.PbalSequencingCreate.as_view(), name='sequencing_create_from_library'),
    url(r'^sequencing/update/(?P<pk>\d+)$', views.PbalSequencingUpdate.as_view(), name='sequencing_update'),
    url(r'^sequencing/delete/(?P<pk>\d+)$', views.PbalSequencingDelete.as_view(), name='sequencing_delete'),
    url(r'^lane/create/$', views.PbalLaneCreate.as_view(), name='lane_create'),
    url(r'^lane/create/(?P<from_sequencing>\d+)$', views.PbalLaneCreate.as_view(), name='lane_create_from_sequencing'),
    url(r'^lane/update/(?P<pk>\d+)$', views.PbalLaneUpdate.as_view(), name='lane_update'),
    url(r'^lane/delete/(?P<pk>\d+)$', views.PbalLaneDelete.as_view(), name='lane_delete'),
    url(r'^plate/create/(?P<from_library>\d+)$', views.plate_create, name='plate_create_from_library'),
    url(r'^plate/create$', views.plate_create, name='plate_create'),
    url(r'^plate/update/(?P<pk>\d+)$', views.plate_update, name='plate_update'),
    url(r'^plate/delete/(?P<pk>\d+)$', views.plate_delete, name='plate_delete')
]