from django.urls import path

from . import views
from django.conf.urls import include, url
#from main.views import MosaicSite

app_name = 'main'
urlpatterns = [
    path('<int:pk>/', views.MosaicView.as_view(), name='detail'),
    #http://localhost:8000/main/site_list/
    path('site_list/', views.SiteListView.as_view(), name='site_list'),
]
