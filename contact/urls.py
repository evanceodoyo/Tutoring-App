from django.urls import path

from .views import submitInquiry

urlpatterns = [
    path("", submitInquiry, name="contact"),
]
