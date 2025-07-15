from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import render
from django.urls import include, path
from django_prometheus import exports

from .yasg import doc_urlpatterns
import debug_toolbar


def index(request):
    return render(request, 'not.html')



urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("src.account.urls")),
    path("", include("src.search.urls")),
    path("", include("src.main.urls")),
    path("", include("src.bus_tours.urls")),
    # path("", include("src.notifications.urls")),
    path("", include("src.payment.urls")),
    path("", include("src.flights.urls")),
    path("webhook/", include("src.webhooks.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("index", index),
]


urlpatterns += [
    path("metrics/", exports.ExportToDjangoView),
]
urlpatterns += doc_urlpatterns
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)), 
    ]
