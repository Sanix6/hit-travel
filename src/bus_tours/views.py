from django.db.models import Count, F, Sum
from django.db.models.functions import TruncMonth
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import BusToursFilter
from .models import BusTourRequest, BusTours, Category, Reviews
from .serializers import (
    BusTourDetailSerializer,
    BusTourListSerializer,
    BusTourRequestSerializer,
    CategorySerializer,
    MyBusToursSerializer,
    ReviewCreateSerializer,
)
from .services import send_bustour_request


class BusTourListAPIView(ListAPIView):
    queryset = BusTours.objects.all()
    serializer_class = BusTourListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BusToursFilter


class BusTourListParamsAPIView(APIView):
    def get(self, request):
        bus_tours = BusTours.objects.all()

        monthly_data = (
            bus_tours.annotate(month=TruncMonth("datefrom"))
            .values("month")
            .annotate(
                total_price=Sum("price"),
                total_count=Count("id"),
            )
        )

        response_data = {"data": {"calendar": {"month": {}}}}

        for entry in monthly_data:
            month = entry["month"].strftime("%-m")
            date_info = {"days": []}

            days_info = bus_tours.filter(datefrom__month=entry["month"].month).values(
                "datefrom", "price"
            )

            for day_info in days_info:
                date_info["days"].append(
                    {
                        "date": day_info["datefrom"].strftime("%d.%m.%Y"),
                        "price": day_info["price"],
                    }
                )

            response_data["data"]["calendar"]["month"][month] = date_info

        departure_choices = [
            {"name": choice[0]} for choice in BusTours.DEPARTURE_CHOICES
        ]

        categories = Category.objects.all()
        category_serializer = CategorySerializer(categories, many=True)

        response_data["categories"] = category_serializer.data
        response_data["departures"] = departure_choices
        return Response(response_data)


class BusTourDetailAPIView(RetrieveAPIView):
    queryset = BusTours.objects.all()
    serializer_class = BusTourDetailSerializer


class ReviewCreateAPIView(CreateAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewCreateSerializer


class BusTourRequestAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = BusTourRequest.objects.all()
    serializer_class = BusTourRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        user = request.user

        if serializer.is_valid():
            tour = serializer.validated_data.get("tour")
            existing_tour_request = BusTourRequest.objects.filter(tour=tour, user=user)

            if existing_tour_request.exists():
                return Response({"response": False})

            serializer.save(user=request.user)

            res = send_bustour_request(serializer.data, user)
            if res:
                tour_request = BusTourRequest.objects.get(tour=tour, user=user)
                tour_request.request_number = res["id"]
                tour_request.save()

            return Response(
                {
                    "response": True,
                    "message": "Заявка успешно отправлено",
                }
            )
        return Response(serializer.errors)


class MyBusToursAPIView(ListAPIView):
    serializer_class = MyBusToursSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BusTourRequest.objects.filter(user=self.request.user)
