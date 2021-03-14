"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
"""
import debug_toolbar
from ajax_select import urls as ajax_select_urls
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from djangoProject import settings

urlpatterns = [
    path('ajax_select/', include(ajax_select_urls)),
    path('admin/', admin.site.urls),
    path('', include('store.urls', namespace='store')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('ckeditor/', include('ckeditor_uploader.urls'))
]
if settings.DEBUG:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_DIR)
    urlpatterns += [re_path(
        r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT
        }
    )]
