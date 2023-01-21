from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, send_mail
from django.shortcuts import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


@shared_task
def send_reset_email(user_id):
    user = User.objects.get(pk=user_id)
    subject = "Password Reset"
    sent_from = settings.EMAIL_HOST_USER

    d = {
        "email": user.email,
        "domain": "127.0.0.1:8000",
        "uid": urlsafe_base64_encode(force_bytes(user.id)),
        "user": user,
        "site_name": settings.SITE_NAME,
        "token": default_token_generator.make_token(user),
        "protocol": "http",
    }

    mail = render_to_string("password_reset_email.txt", d)
    try:
        send_mail(subject, mail, sent_from, [user.email], fail_silently=False)
    except BadHeaderError:
        return HttpResponse("Invalid header found.")
