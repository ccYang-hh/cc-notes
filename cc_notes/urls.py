

from django.contrib import admin
from django.urls import path,include,re_path
from django.views.generic import TemplateView
from django.contrib.staticfiles.views import serve

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve

import notifications.urls


def return_static(request, path, insecure=True, **kwargs):
    return serve(request, path, insecure, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    #re_path(r'^$', TemplateView.as_view(template_name="index.html")),
    re_path(r'^api/static/(?P<path>.*)$', return_static, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^api/media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),

    path('api/users/', include('users.urls')),
    path('api/tools/', include('tools.urls')),
    path('api/articles/', include('notes.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/feeds/', include('feeds.urls')),
    path('api/notice/', include('notice.urls')),
    path('api/events/', include('events.urls')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)