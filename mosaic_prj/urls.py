from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from main import views

urlpatterns = [
    path('tags', views.tags, name='tags'),
    path('map', views.map, name='map'),
    path('main/', include('main.urls')),
    path('tag/<int:tagid>/', views.tagPage, name='tag-url'),
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(packages=['main']), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
