from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from courses.models import Category, Course
from events.models import Event, EventTicket

User = get_user_model()
now = datetime.now()
evnt_end = now + timedelta(days=1)

class EventsListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@mail.com",
            username="testuser",
            password="secret",
        )
        self.category = Category.objects.create(title="Category")
        self.event1 = Event.objects.create(
            organiser=self.user,
            title="Test Event",
            description="This is a test event",
            banner="events/banners/default.jpg",
            category=self.category,
            start_date=now.date(),
            end_date=evnt_end.date(),
            start_time=now.time(),
            end_time=evnt_end.time(),
            old_price=100.00,
            price=50.00,
            venue="Test Venue",
            is_active=True,
        )
        self.event2 = Event.objects.create(
            organiser=self.user,
            title="Test Event 1",
            description="This is a test event 1",
            banner="events/banners/default.jpg",
            category=self.category,
            start_date=now.date(),
            end_date=evnt_end.date(),
            start_time=now.time(),
            end_time=evnt_end.time(),
            old_price=100.00,
            price=50.00,
            venue="Test Venue",
            is_active=True,
        )
        self.url = reverse("events")

    def test_events_list_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_title"], "Events")
        self.assertTemplateUsed('events.html')
        
        
    def test_event_list_contains_active_events(self):
        Event.objects.create(
            organiser=self.user,
            title="Test Event 3",
            description="This is a test event 3",
            banner="events/banners/default.jpg",
            category=self.category,
            start_date=now.date(),
            end_date=evnt_end.date(),
            start_time=now.time(),
            end_time=evnt_end.time(),
            old_price=100.00,
            price=50.00,
            venue="Test Venue",
            is_active=False,
        )
        response = self.client.get(self.url)
        events = response.context["events"]
        self.assertEqual(len(events), 2)
        for event in events:
            self.assertIs(event.is_active, True)
            self.assertEqual(event.organiser, self.user)

    def test_event_list_contains_today_or_future_events(self):
        Event.objects.create(
            organiser=self.user,
            title="Test Event 3",
            description="This is a test event 3",
            banner="events/banners/default.jpg",
            category=self.category,
            start_date=(now - timedelta(days=1)).date(),
            end_date=evnt_end.date(),
            start_time=now.time(),
            end_time=evnt_end.time(),
            old_price=100.00,
            price=50.00,
            venue="Test Venue",
            is_active=True,
        )
        response = self.client.get(self.url)
        events = response.context["events"]
        self.assertEqual(len(events), 2)
        for event in events:
            self.assertTrue(event.start_date >= now.date())

    def test_course_teachers_not_availble(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["course_teachers"].exists())
    
    def test_course_teachers_available(self):
        Course.objects.create(
            owner=self.user,
            title="Test Course",
            category=self.category,
            overview="The overview of a test course.",
            language="English",
            old_price=200,
            price=150,
            thumbnail="courses/thumbnails/course_img.png",
        )
        response = self.client.get(self.url)
        ct = response.context["course_teachers"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ct), 1)
        self.assertEqual(ct.first().owner, self.user)


class EventDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@mail.com",
            username="testuser",
            password="secret",
        )
        self.category = Category.objects.create(title="Category")
        self.event = Event.objects.create(
            organiser=self.user,
            title="Test Event",
            description="This is a test event",
            banner="events/banners/default.jpg",
            category=self.category,
            start_date=now.date(),
            end_date=evnt_end.date(),
            start_time=now.time(),
            end_time=evnt_end.time(),
            old_price=100.00,
            price=50.00,
            venue="Test Venue",
            is_active=True,
        )

        self.url = reverse("event_detail", kwargs={"event_slug": self.event.slug})

    def test_event_detail_GET(self):
        response = self.client.get(self.url)
        event = response.context["event"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_title"], self.event.title)
        self.assertEqual(event, self.event)
        self.assertIs(event.is_active, True)
        self.assertTemplateUsed(response, "event-details.html")

    def test_event_detail_with_invalid_slug_returns_404(self):
        response = self.client.get(reverse(
                "event_detail",
                kwargs={"event_slug": "invalid-slug"},
            ))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_event_detail_with_inactive_event(self):
        Event.objects.create(
            organiser=self.user,
            title="Test Event 2",
            description="This is a test event 2",
            banner="events/banners/default.jpg",
            category=self.category,
            start_date=now.date(),
            end_date=evnt_end.date(),
            start_time=now.time(),
            end_time=evnt_end.time(),
            old_price=100.00,
            price=50.00,
            venue="Test Venue",
            is_active=False,
        )

        response = self.client.get(reverse(
                "event_detail",
                kwargs={"event_slug": "test-event-2"},
            ))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed("404.html")

    def test_event_today_or_in_future(self):
        # Create event which has already began.
        Event.objects.create(
            organiser=self.user,
            title="Test Event 3",
            description="This is a test event 3",
            banner="events/banners/default.jpg",
            category=self.category,
            start_date=(now - timedelta(days=1)).date(),
            end_date=evnt_end.date(),
            start_time=now.time(),
            end_time=evnt_end.time(),
            old_price=100.00,
            price=50.00,
            venue="Test Venue",
            is_active=True,
        )
        response = self.client.get(reverse(
                "event_detail",
                kwargs={"event_slug": "test-event-3"},
            ))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed("404.html")


class EnrollEventTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@mail.com",
            username="testuser",
            password="secret",
        )
        self.user2 = User.objects.create_user(
            name="testuser2",
            email="testuser2@mail.com",
            username="testuser2",
            password="secret",
        )
        self.category = Category.objects.create(title="Category")
        self.event = Event.objects.create(
            organiser=self.user,
            title="Test Event",
            description="This is a test event",
            banner="events/banners/default.jpg",
            category=self.category,
            start_date=now.date(),
            end_date=evnt_end.date(),
            start_time=now.time(),
            end_time=evnt_end.time(),
            old_price=100.00,
            price=50.00,
            venue="Test Venue",
            is_active=True,
        )

        self.url = reverse("event_detail", kwargs={"event_slug": self.event.slug})
    
    def test_enroll_event_not_logged_in(self):
        # send a GET request to the enrollEvent view without logging in.
        response = self.client.get(reverse('buy_event_ticket', kwargs={'event_slug': self.event.slug}))

        # assert that the response status code is 302 (redirect)
        # and user is redirected to login page.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('buy_event_ticket', kwargs={'event_slug': self.event.slug}))

    def test_enroll_event_success(self):
        self.client.force_login(self.user2)
        response = self.client.post(reverse('buy_event_ticket', kwargs={'event_slug': self.event.slug}))
        self.assertEqual(response.status_code, 302)

        # assert that the user is redirected to the event page.
        self.assertRedirects(response, self.event.get_absolute_url())
        
        # check the EventTicket table in the database.
        ticket = EventTicket.objects.get(user=self.user2, event=self.event)
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.amount, self.event.price)