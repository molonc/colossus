"""colossus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
    
    
Created on May 16, 2016

@author: Jafar Taghiyar (jtaghiyar@bccrc.ca)

Updated Oct 19, 2017 by Spencer Vatrt-Watts (github.com/Spenca)
"""

from django.conf import settings
from django.conf.urls import url, include, static
from django.contrib import admin
from core import views

urlpatterns = [
    url(r'^$', views.index_view, name='index'),    
    url(r'^admin/', admin.site.urls),
    url(r'^search/', views.search_view, name='search'),
    url(r'^core/', include('core.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^sisyphus/', include('sisyphus.urls')),
]

urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)