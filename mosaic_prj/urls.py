from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from main import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('', include('main.urls')),
    path('account/', include('users.urls')),
    path('map', views.mosaic_map, name='map'),
    path('tag/<int:tagid>/', views.tag_page, name='tag-url'),
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(packages=['main']), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
