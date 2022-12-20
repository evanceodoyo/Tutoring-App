from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Event, EventTicket
from courses.models import Course
from datetime import date

User = get_user_model()
today = date.today()


def eventsList(request):
    try:
        events = (
            Event.objects.select_related("organiser")
            .filter(start_date__gte=today, is_active=True)
            .order_by("start_date")
        )
        course_teachers = Course.objects.only("owner")[:4]
        return render(
            request,
            "events.html",
            {
                "page_title": "Events",
                "events": events,
                "course_teachers": course_teachers,
            },
        )
    except Exception as e:
        print(e)
        return redirect("home")


def eventDetail(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug, is_active=True)
    return render(
        request,
        "event-details.html",
        {
            "page_title": event.title,
            "event": event,
        },
    )


@login_required
def enrollEvent(request, event_slug):
    try:
        event = get_object_or_404(Event, slug=event_slug, start_date__gte=today)
        if request.method == "POST":
            user = request.user
            phone = request.POST.get("phone")  # Use for M-Pesa integration.
            # if user.is_authenticated and user.enrolled_events.filter(event=event).exists():
            #     messages.info(request, "You have already bought a ticket to this event.")
            #     return redirect(event)

            EventTicket.objects.create(user=user, event=event, amount=event.price)
            messages.success(request, "Ticket purchase successfull, thank you.")
            return redirect(event)
        return redirect(event)
    except Exception as e:
        print(e)
        return redirect("events")
