from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
    path('<int:pk>/', views.MosaicView.as_view(), name='detail'),
    path('tag/create/', views.TagCreateView.as_view(), name='tag_create'),
    path('tag/update/<int:pk>/', views.TagUpdateView.as_view(), name='tag_update'),
    path('tag/delete/<int:pk>/', views.TagDeleteView.as_view(), name='tag_delete'),
    path('site/create/', views.MosaicSiteCreateView.as_view(), name='site_create'),
    path('site/update/<int:pk>/', views.MosaicSiteUpdateView.as_view(), name='site_update'),
    path('site/delete/<int:pk>/', views.MosaicSiteDeleteView.as_view(), name='site_delete'),
    path('item/create/', views.MosaicItemCreateView.as_view(), name='item_create'),
    path('item/update/<int:pk>/', views.MosaicItemUpdateView.as_view(), name='item_update'),
    path('item/delete/<int:pk>/', views.MosaicItemDeleteView.as_view(), name='item_delete'),
]
