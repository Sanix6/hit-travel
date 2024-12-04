from django.urls import path

from .views import (
    CreateRequestView,
    # CreateClientView
    # SaveDataView,
)


urlpatterns = [
    path("create-request", CreateRequestView.as_view()),
    # path("create_client", CreateClientView.as_view(), name="create_client"),
]
