from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('<int:pk>/', views.MosaicView.as_view(), name='detail'),
    path('tag/create/', views.TagCreateView.as_view(), name='tag_create'),
    path('tag/update/<int:pk>/', views.TagUpdateView.as_view(), name='tag_update'),
    path('tag/delete/<int:pk>/', views.TagDeleteView.as_view(), name='tag_delete'),
]
