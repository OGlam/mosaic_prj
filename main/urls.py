from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('<int:pk>/', views.MosaicView.as_view(), name='detail'),
]
