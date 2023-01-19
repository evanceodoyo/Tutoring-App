from django.test import TestCase
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from events.models import (
    Event,
    Category,
    EventTag,
    Objective,
    EventObjective,
    EventTicket,
)

User = get_user_model()

now = datetime.now()
evnt_end = now + timedelta(days=1)


class EventModelTests(TestCase):
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
        )

    def test_event_creation(self):
        self.assertTrue(isinstance(self.event, Event))
        self.assertEqual(
            self.event.__str__(), "Test Event organised by testuser: testuser"
        )

    def test_event_absolute_url(self):
        self.assertEqual(self.event.get_absolute_url(), "/events/test-event/")

    def test_event_discount(self):
        self.assertEqual(self.event.discount(), 50)

    def test_event_is_active(self):
        self.assertTrue(self.event.is_active)

    def test_event_slug_generation(self):
        self.assertEqual(self.event.slug, "test-event")

    def test_event_slug_update(self):
        self.event.title = "Updated Event"
        self.event.save()
        self.assertEqual(self.event.slug, "test-event")

    def test_event_category_related_name(self):
        self.assertEqual(self.category.events.count(), 1)
        self.assertEqual(self.category.events.first(), self.event)

    def test_validate_event_start_greater_than_end_raises_exception(self):
        # Test if the validate_event_time method raises an exception when the start time is greater than the end time
        with self.assertRaises(Exception) as cm:
            event = Event.objects.create(
                organiser=self.user,
                title="Test Event Time",
                description="This is a test event",
                banner="events/banners/default.jpg",
                category=self.category,
                start_date=evnt_end.date(),
                end_date=evnt_end.date(),
                start_time=(evnt_end + timedelta(seconds=59)).time(),
                end_time=evnt_end.time(),
                old_price=100.00,
                price=50.00,
                venue="Test Venue",
            )
            event.validate_event_time()
        self.assertEqual(
            str(cm.exception),
            "The event's start time cannot be greater than or same as the event's end time.",
        )
        # Confirm that the event was not added to the database.
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().slug, "test-event")

    def test_validate_event_time_end_in_past_raises_exception(self):
        # Test if the validate_event_time method raises an exception when the end time is in the past.
        self.event.end_date = (now - timedelta(days=1)).date()
        with self.assertRaises(Exception) as cm:
            event = Event.objects.create(
                organiser=self.user,
                title="Test Event Time",
                description="This is a test event",
                banner="events/banners/default.jpg",
                category=self.category,
                start_date=(now - timedelta(days=1)).date(),
                end_date=now.date(),
                start_time=now.time(),
                end_time=(now - timedelta(seconds=59)).time(),
                old_price=100.00,
                price=50.00,
                venue="Test Venue",
            )
            event.validate_event_time()
        self.assertEqual(
            str(cm.exception),
            "The end date and time of the event must be a later time of today or in the future.",
        )
        # Confirm that the event was not added to the database.
        events = Event.objects.all()
        self.assertEqual(events.count(), 1)
        self.assertEqual(events.first().slug, "test-event")
        self.assertNotEqual(events.first().slug, "test-event-time")

    def test_validate_event_time_valid(self):
        self.event.validate_event_time()  # Should not raise an exception


class ObjectiveModelTests(TestCase):
    def setUp(self):
        self.obj1 = Objective.objects.create(objective="Test Objective 1")
        self.obj2 = Objective.objects.create(objective="Test Objective 2")
        self.obj3 = Objective.objects.create(objective="Test Objective 3")

    def test_objective_creation(self):
        self.assertTrue(isinstance(self.obj1, Objective))
        self.assertEqual(self.obj1.__str__(), self.obj1.objective)

    def test_objective_max_length(self):
        max_length = self.obj1._meta.get_field("objective").max_length
        self.assertEqual(max_length, 80)

    def test_objective_unique(self):
        with self.assertRaises(IntegrityError) as cm:
            Objective.objects.create(objective="Test Objective 1")
        self.assertEqual(
            str(cm.exception),
            'duplicate key value violates unique constraint "objectives_objective_key"\nDETAIL:  Key (objective)=(Test Objective 1) already exists.\n',
        )


class EventObjectiveModelTests(TestCase):
    def setUp(self):
        self.objective1 = Objective.objects.create(objective="Test Objective 1")
        self.objective2 = Objective.objects.create(objective="Test Objective 2")
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
        )

        self.event_objective1 = EventObjective.objects.create(
            objective=self.objective1, event=self.event
        )
        self.event_objective2 = EventObjective.objects.create(
            objective=self.objective2, event=self.event
        )

    def test_event_objective_creation(self):
        self.assertTrue(isinstance(self.event_objective1, EventObjective))
        self.assertEqual(
            self.event_objective1.__str__(),
            f"{self.event_objective1.objective.objective} for event {self.event.title}",
        )

    def test_event_objective_ordering(self):
        event_objectives = EventObjective.objects.all()
        self.assertEqual(
            list(event_objectives), [self.event_objective2, self.event_objective1]
        )

    def test_event_objective_event_relationship(self):
        self.assertEqual(self.event_objective1.event, self.event)
        self.assertEqual(self.event_objective2.event, self.event)

    def test_event_objective_objective_relationship(self):
        self.assertEqual(self.event_objective1.objective, self.objective1)
        self.assertEqual(self.event_objective2.objective, self.objective2)


class EventTicketModelTests(TestCase):
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
        )
        self.ticket1 = EventTicket.objects.create(
            user=self.user, event=self.event, amount=50
        )
        self.ticket2 = EventTicket.objects.create(
            user=self.user, event=self.event, amount=100
        )

    def test_event_ticket_creation(self):
        self.assertTrue(isinstance(self.ticket1, EventTicket))
        self.assertEqual(
            self.ticket1.__str__(), f"{self.ticket1.ticket_id} : {self.ticket1.event}"
        )

    def test_event_ticket_amount(self):
        self.assertEqual(self.ticket1.amount, 50)
        self.assertEqual(self.ticket2.amount, 100)

    def test_event_ticket_user_relationship(self):
        self.assertEqual(self.ticket1.user, self.user)
        self.assertEqual(self.ticket2.user, self.user)

    def test_event_ticket_event_relationship(self):
        self.assertEqual(self.ticket1.event, self.event)
        self.assertEqual(self.ticket2.event, self.event)

    def test_event_ticket_unique_ticket_id(self):
        ticket_id = self.ticket1.ticket_id
        with self.assertRaises(IntegrityError) as cm:
            EventTicket.objects.create(
                user=self.user, event=self.event, amount=150, ticket_id=ticket_id
            )
        self.assertEqual(
            str(cm.exception),
            f'duplicate key value violates unique constraint "event_tickets_ticket_id_key"\nDETAIL:  Key (ticket_id)=({ticket_id}) already exists.\n',
        )
