from django.urls import path
from src.payment.views import MPaymentView, PaylerPaymentView, PaylerCallbackView, PaymentCallbackFront

urlpatterns = [
    # mbank
    path('payment/', MPaymentView.as_view(), name='Mbank webhook'),

    # payler
    path('payler/pay/', PaylerPaymentView.as_view()),
    path('payler/callback/', PaylerCallbackView.as_view()),
    # path('payler/return/', PaylerReturnView.as_view()),
    path("payler/check/", PaymentCallbackFront.as_view(template_name="payments/payment_check.html")),
]