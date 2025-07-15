from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status


#apps
from .models import Notifications
from .serializers import NotificationsSerializer, DeviceTokenSerializer

class NotificationView(ViewSet):
    @action(detail=False, methods=['get'], url_path='notifications')
    def get_notifications(self, request):
        queryset = Notifications.objects.order_by('-id')
        serializer = NotificationsSerializer(queryset, many=True)
        return Response(serializer.data)


class DeviceTokenView(ViewSet):
    @action(detail=False, methods=['post'], url_path='device-token')
    def post(self, request, *args, **kwargs):
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Токен сохранен"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)