from django.test import TestCase
from django.urls import reverse, resolve
from events.views import eventDetail, enrollEvent


class EventURLTests(TestCase):
    def setUp(self):
        pass

    def test_events_list_url_available_by_name(self):
        response = self.client.get(reverse("events"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events.html")

    def test_events_list_url_available_at_correct_location(self):
        response = self.client.get("/events/")
        self.assertTemplateUsed(response, "events.html")
        self.assertEqual(response.status_code, 200)

    def test_event_detail_url(self):
        url = reverse("event_detail", kwargs={"event_slug": "test-event"})
        self.assertEqual(url, "/events/test-event/")
        self.assertEqual(resolve(url).func, eventDetail)

    def test_enroll_event_url(self):
        url = reverse("buy_event_ticket", kwargs={"event_slug": "test-event"})
        self.assertEqual(url, "/events/buy-event-ticket/test-event/")
        self.assertEqual(resolve(url).func, enrollEvent)
