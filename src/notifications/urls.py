from django.urls import include, path
from rest_framework_nested import routers

from . import views

app_name = "notification"

router = routers.SimpleRouter()
router.register(r"fcm-token", views.FCMTokenViewSet)

urlpatterns = [
    path("", include(router.urls)),
]