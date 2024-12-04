from django.urls import path, include
from rest_framework_nested import routers

from . import views

app_name = 'notification'

router = routers.SimpleRouter()
router.register(r'fcm-token', views.FCMTokenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]