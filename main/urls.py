from django.conf.urls import url

from . import views

app_name = 'main'
urlpatterns = [
    url(r'(?P<pk>[0-9]+)/$', views.MosaicView.as_view(), name='detail'),
]