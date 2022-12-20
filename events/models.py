from datetime import datetime, timedelta
import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django_resized import ResizedImageField

from courses.models import Category, Tag, TimeStampedModel


def default_start_time():
    return datetime.now() + timedelta(days=1)


def default_end_time():
    return default_start_time() + timedelta(hours=4)


class Event(TimeStampedModel):
    organiser = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField()
    banner = ResizedImageField(size=[600, 400], upload_to="events/banners")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="events"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    old_price = models.DecimalField(decimal_places=2, max_digits=9, default=0.0)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    venue = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "events"

    def __str__(self):
        return f"{self.title} organised by {self.organiser}"

    def get_absolute_url(self):
        return reverse("event_detail", kwargs={"event_slug": self.slug})

    def discount(self):
        return round((self.old_price - self.price) / self.old_price * 100)

    def event_expired(self):
        return


class EventTag(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_tags"
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        db_table = "event_tags"

    def __str__(self):
        return self.tag.title


class Sponsor(TimeStampedModel):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="events/sponsors")
    event = models.ForeignKey(
        Event, on_delete=models.SET_NULL, related_name="sponsors", blank=True, null=True
    )

    class Meta:
        db_table = "sponsors"

    def __str__(self):
        return self.name


class Objective(TimeStampedModel):
    objective = models.CharField(max_length=80, unique=True)

    class Meta:
        db_table = "objectives"
        ordering = ["-created", "objective"]

    def __str__(self):
        return self.objective


class EventObjective(TimeStampedModel):
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_objectives"
    )

    class Meta:
        db_table = "event_objectives"
        ordering = ["-created", "objective"]

    def __str__(self):
        return f"{self.objective.objective} for event {self.event.title}"


class EventTicket(TimeStampedModel):
    ticket_id = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="enrolled_events"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)

    class Meta:
        db_table = "event_tickets"

    def __str__(self):
        return f"{self.ticket_id} : {self.event}"
