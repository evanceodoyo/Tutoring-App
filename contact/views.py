from django.contrib import messages
from django.shortcuts import redirect, render

from .models import CustomerInquiry


def submitInquiry(request):
    context = {"page_title": "Contact Us"}
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        context.update(
            {"name": name, "email": email, "subject": subject, "message": message}
        )

        if not (name and email and subject and message):
            messages.error(request, "All fields are required!")
        else:
            CustomerInquiry.objects.create(
                name=name, email=email, subject=subject, message=message
            )
            messages.success(
                request,
                "Your message submitted successfully. We will get back to you soon!",
            )
            return redirect("home")

    return render(request, "contact.html", context)
