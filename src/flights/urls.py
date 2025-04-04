from django.urls import path

from src.flights.views import (
    BookingHistory,
    BookingHistoryDetail,
    BookingInfoView,
    BookingView,
    CancelBookingView,
    FlightDetailView,
    FlightRulesView,
    FlightsSearchView,
    GetTokenView,
    RefundAmountsView,
    SearchParamsView,
    SearchParamsViewV3,
    Token
)

urlpatterns = [
    path("avia/params/v2/", SearchParamsViewV3.as_view(), name="avia_params_v2_read"),
    path(
        "avia/params/v2/<str:city>/",
        SearchParamsView.as_view(),
        name="avia_params_v2_read",
    ),
    path("avia/search/", FlightsSearchView.as_view(), name="seach-tickets"),
    path("avia/detail/<str:tid>", FlightDetailView.as_view(), name="detail-ticket"),
    path("avia/rules/<str:tid>", FlightRulesView.as_view(), name="rules-ticket"),
    path("avia/book/", BookingView.as_view(), name="book"),
    path("avia/booking-history/", BookingHistory.as_view(), name="booking-history"),
    path("avia/booking-info/<int:billing_number>", BookingInfoView.as_view()),
    path(
        "avia/booking-history/<str:booking_id>/",
        BookingHistoryDetail.as_view(),
        name="booking-history-detail",
    ),
    path("avia/booking-cancel/", CancelBookingView.as_view(), name="booking-cancel"),
    path("avia/get-token/", GetTokenView.as_view(), name="get_token"),
    path("avia/refund-amounts/", RefundAmountsView.as_view(), name="refund-amounts"),
    path('toke', Token.as_view())
]
