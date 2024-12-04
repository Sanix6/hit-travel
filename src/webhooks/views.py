from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
import time


from .models import (
    CreateRequest,
    CreateClient,
)
from .serializers import (
    CreateRequestSerializer,
    CreateClientSerializer,
)
from .services import (
    add_request,
)

class SaveDataView(APIView):
    def post(self, request, format=None):
        try:
            data = request.body.decode('utf-8')
            with open("webhook.txt", "a") as file:
                file.write(f"{data}\n\n")
            return Response({"message": "Data saved successfully"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


# working API
class CreateRequestView(APIView):
    queryset = CreateRequest.objects.all()
    serializer_class = CreateRequestSerializer

    def post(self, request, *args, **kwargs):
        try:
            data = request.data

            uon_id = data.get('uon_id')
            uon_subdomain = data.get('uon_subdomain')
            datetime_str = data.get('datetime')
            datetime = parse_datetime(datetime_str)
            type_id = data.get('type_id')
            request_id = data.get('request_id')
            nurbek_test = data.get('nurbek_test')

            instance = CreateRequest.objects.create(
                uon_id=uon_id,
                uon_subdomain=uon_subdomain,
                datetime=datetime,
                type_id=type_id,
                request_id=int(request_id)
            )
            instance.save()
            time.sleep(2)
            with open("webhook.txt", "a") as file:
                file.write(f"{data}\n\n")

            if nurbek_test:
                add_request.apply_async(args=[instance.request_id], countdown=1)
            else:
                add_request.apply_async(args=[instance.request_id], countdown=700)

            return Response({"message": "Данные успешно сохранены"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class CreateClientView(CreateAPIView):
    queryset = CreateClient.objects.all()
    serializer_class = CreateClientSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
