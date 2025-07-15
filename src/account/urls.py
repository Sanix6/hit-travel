from django.urls import path

from .profile_views import *
from .request_views import *
from .views import *

urlpatterns = [
    path("auth/register", RegisterAPIView.as_view(), name="register"),
    path("auth/verify-phone", VerifyPhoneView.as_view(), name="verify-phone"),
    path("auth/re-send", SendAgainCodeAPIView.as_view(), name="send-code-again"),
    path("auth/login", LoginAPIView.as_view(), name="login"),
    path("auth/logout", LogoutAPIView.as_view(), name="logout"),
    path(
        "auth/password-reset/request",
        PasswordResetRequestAPIView.as_view(),
        name="password-reset-request",
    ),
    path(
        "auth/password-reset/<str:token>",
        PasswordResetUpdateAPIView.as_view(),
        name="password-reset-update",
    ),
    path("auth/new-password", SetNewPasswordAPIView.as_view(), name="set-new-password"),
    # Profile
    path(
        "profile/update-photo",
        UpdateProfilePhotoAPIView.as_view(),
        name="Update profile photo",
    ),
    path(
        "profile/remove-photo",
        RemoveProfilePhotoAPIView.as_view(),
        name="Remove profile photo",
    ),
    path("profile/personal", ProfileInfoAPIView.as_view(), name="Profile information"),
    path("profile/update-info", UpdateInfoView.as_view(), name="update-info"),
    path("profile/delete", DeleteProfileView.as_view(), name="delete-profile"),
    path("profile/my-tour", MyTourAPIView.as_view(), name="my-tour"),
    path("profile/manual-requests/", ManualRequestsView.as_view()),
    path("profile/manual-requests/<int:pk>", ManualRequestsDetailView.as_view()),
    path(
        "profile/detail-my-tour/<int:pk>",
        MyTourDetailAPIVIew.as_view(),
        name="detail-my-tour",
    ),
    # Request
    path("tour/request", TourRequestView.as_view(), name="tour-request"),
    # hotel
    path("hotel/", RequestHotelView.as_view(), name="hotel"),
    path("hotel/<int:pk>", HotelDetail.as_view(), name="hotel-detail"),
    # Payments
    path("payment/qrcode", PaymentsAPIView.as_view(), name="qrcode"),
    # Bonuse
    path("bonus/history", BonusHistoryAPIView.as_view(), name="bonus-history"),
    # FAQ
    path("faq", FAQAPIView.as_view(), name="faq"),
]
