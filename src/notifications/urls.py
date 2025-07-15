from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationView, DeviceTokenView


router = DefaultRouter()
router.register(r'api', NotificationView, basename='api')
router.register(r'api', DeviceTokenView, basename='api')

urlpatterns = [
    path('', include(router.urls)),
]