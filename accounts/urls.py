from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    loginView,
    logoutView,
    newsLetterSubscription,
    passwordChange,
    passwordReset,
    profile,
    profileUpdate,
    signUp,
)

urlpatterns = [
    path("sign-up/", signUp, name="sign_up"),
    path("profile/", profile, name="profile"),
    path("profile-update/", profileUpdate, name="profile_update"),
    path("login/", loginView, name="login"),
    path("logout/", logoutView, name="logout"),
    path(
        "news-letter/subscription/",
        newsLetterSubscription,
        name="news_letter_subscription",
    ),
    path("password-change/", passwordChange, name="password_change"),
    path("password-reset/", passwordReset, name="password_reset"),
    path(
        "password-reset-done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password-reset-done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password-reset-confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password-reset-complete.html"
        ),
        name="password_reset_complete",
    ),
]
