import re

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from enroll.models import EnrolledCourse
from utils.decorators import unauthenticated_user_required

from .models import NewsLetterSubscriber
from .tasks import send_reset_email

User = get_user_model()


def validate_user(user):
    error_msg = None
    if not user.name:
        error_msg = "Name required!"
    elif not re.match(r"^[A-Za-z0-9_]+$", user.username):
        error_msg = "Username can only contain alphanumeric characters and underscore."
    elif user.email_exists():
        error_msg = "User with the email you provided already registered."
    elif user.username_exists():
        error_msg = "Username you provided is already taken."
    # elif len(user.password) < 8:
    #     error_msg = "Password must be at least eight characters long."
    return error_msg


@unauthenticated_user_required
def signUp(request):
    context = {}
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("username")
        user_type = request.POST.get("user_type")
        password = request.POST.get("password")
        user = User(name=name, email=email, username=username)

        error_msg = None
        error_msg = validate_user(user)
        if not error_msg:
            if user_type != "student":
                user.is_student = False
            user.set_password(password)
            user.save()
            if user := authenticate(request, username=email, password=password):
                login(request, user)
                return redirect("home")
        context = {
            "page_title": "SignUp",
            "name": name,
            "email": email,
            "username": username,
            "error_msg": error_msg,
        }

    return render(request, "sign-up.html", context)


@unauthenticated_user_required
def loginView(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if user := authenticate(request, username=email, password=password):
            login(request, user)
            messages.success(request, "Login successful")
            if "next" in request.POST:
                return redirect(request.POST.get("next"))
            return redirect("home")
        messages.error(request, "Invalid email or password!")

        context = {"page_title": "Login", "email": email}
    return render(request, "sign-in.html", context)


def logoutView(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


@login_required
def profile(request):
    user = request.user
    enrolled_courses = EnrolledCourse.objects.select_related(
        "enrollment", "course"
    ).filter(student=user)
    return render(
        request,
        "my-profile.html",
        {
            "page_title": "Profile",
            "enrolled_courses": enrolled_courses,
            "user": user,
        },
    )


@login_required
def profileUpdate(request):
    if request.method == "POST":
        user = request.user
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        bio = request.POST.get("bio")

        if name:
            user.name = name
            user.phone = phone
            user.address = address
            user.bio = bio
            user.save()
            messages.success(request, "Profile updated successfully")
            return redirect("profile")
        messages.error(request, "Profile not updated. Name cannot be empty!")
        return redirect("profile_update")

    return redirect("profile")


@login_required
def passwordChange(request):
    user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        new_password2 = request.POST.get("new_password2")

        if new_password != new_password2:
            messages.error(request, "The passwords you entered do not match!")
            return redirect("password_change")

        if user := authenticate(
            request, username=user.email, password=current_password
        ):
            send_reset_email.delay(user.pk)
            logout(request)
            return redirect("password_reset_done")
        messages.error(request, "The current password entered is wrong.")
    return redirect("profile")


@unauthenticated_user_required
def passwordReset(request):
    context = {"page_title": "Password Reset"}
    if request.method == "POST":
        email = request.POST.get("email")
        context["email"] = email

        try:
            user = User.objects.get(email=email)
            send_reset_email.delay(user.pk)
            return redirect("password_reset_done")
        except User.DoesNotExist:
            messages.info(
                request, "Sorry, user with the provided email does not exist."
            )
            return redirect("password_reset")

    return render(request, "password-reset-form.html", context)


def newsLetterSubscription(request):
    if request.method == "POST":
        email = request.POST.get("email")
        url = request.META.get("HTTP_REFERER")

        if not NewsLetterSubscriber.objects.filter(email=email).exists():
            subscriber = NewsLetterSubscriber(email=email)
            subscriber.save()
            messages.info(request, "Thanks for subscribing to our newsletter.")
            return redirect(url)
        messages.info(request, "You've already subscribed to our newsletter.")
    return redirect(url)
