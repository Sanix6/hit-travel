from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .yasg import doc_urlpatterns

from django.shortcuts import render

def index(request):
    return render(request, 'not.html')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("src.account.urls")),
    path("", include("src.search.urls")),
    path("", include("src.main.urls")),
    path("", include("src.bus_tours.urls")),
    path("", include("src.notification.urls")),
    path("", include("src.payment.urls")),
    path("", include("src.flights.urls")),
    path("webhook/", include("src.webhooks.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("", index)
]

# urlpatterns += doc_urlpatterns
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
