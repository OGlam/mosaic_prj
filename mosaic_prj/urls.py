from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from main import views
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('about-edit/', views.AboutEditView.as_view(), name='about_edit'),
    path('contact', users_views.ContactView.as_view(), name='contact'),
    path('', include('main.urls')),
    path('tags/', views.tags, name='tags'),
    path('map/', views.mosaic_map, name='map'),
    path('account/', include('users.urls')),
    path('tag/<int:tagid>/', views.tag_page, name='tag-url'),
    path('jsi18n/', JavaScriptCatalog.as_view(packages=['main']), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
)
