from django.urls import path

from .views import eventDetail, eventsList, enrollEvent

urlpatterns = [
    path("", eventsList, name="events"),
    path("<slug:event_slug>/", eventDetail, name="event_detail"),
    path("buy-event-ticket/<slug:event_slug>/", enrollEvent, name="buy_event_ticket"),
]
