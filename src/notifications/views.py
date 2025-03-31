from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import TokenFCM
from .serializers import TokenCreateSerializer


class FCMTokenViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = TokenFCM.objects.all()
    serializer_class = TokenCreateSerializer
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED)