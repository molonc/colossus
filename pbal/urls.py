"""
Created Oct 23, 2017

@author: Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf.urls import url
from core import views

app_name = 'pbal'
urlpatterns = [
    url(r'^library/(?P<pk>\d+)$', views.pbal_library_detail, name='library_detail'),
    url(r'^library/list$', views.pbal_library_list, name='library_list'),
    url(r'^library/create/$', views.PbalLibraryCreate.as_view(), name='library_create'),
    url(r'^library/create/(?P<from_sample>\d+)$', views.PbalLibraryCreate.as_view(), name='library_create_from_sample'),
    url(r'^library/update/(?P<pk>\d+)$', views.PbalLibraryUpdate.as_view(), name='library_update'),
    url(r'^library/delete/(?P<pk>\d+)$', views.pbal_library_delete, name='library_delete'),
    url(r'^sequencing/(?P<pk>\d+)$', views.pbal_sequencing_detail, name='sequencing_detail'),
    url(r'^sequencing/list$', views.pbal_sequencing_list, name='sequencing_list'),
    url(r'^sequencing/create/$', views.pbal_sequencing_create, name='sequencing_create'),
    url(r'^sequencing/create/(?P<from_library>\d+)$', views.pbal_sequencing_create, name='sequencing_create_from_library'),
    url(r'^sequencing/update/(?P<pk>\d+)$', views.pbal_sequencing_update, name='sequencing_update'),
    url(r'^sequencing/delete/(?P<pk>\d+)$', views.pbal_sequencing_delete, name='sequencing_delete'),
    url(r'^lane/create/$', views.pbal_lane_create, name='lane_create'),
    url(r'^lane/create/(?P<from_sequencing>\d+)$', views.pbal_lane_create, name='lane_create_from_sequencing'),
    url(r'^lane/update/(?P<pk>\d+)$', views.pbal_lane_update, name='lane_update'),
    url(r'^lane/delete/(?P<pk>\d+)$', views.pbal_lane_delete, name='lane_delete'),
    url(r'^plate/create/$', views.plate_create, name='plate_create'),
    url(r'^plate/create/(?P<from_library>\d+)$', views.plate_create, name='plate_create_from_library'),
    url(r'^plate/update/(?P<pk>\d+)$', views.plate_update, name='plate_update'),
    url(r'^plate/delete/(?P<pk>\d+)$', views.plate_delete, name='plate_delete')
]