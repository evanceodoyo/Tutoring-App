from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField


class Designation(models.Model):
    title = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "designation"

    def __str__(self):
        return self.title


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True, default="")
    designation = models.ForeignKey(
        "Designation", on_delete=models.CASCADE, blank=True, null=True
    )
    is_student = models.BooleanField("Student", default=True)
    is_active = models.BooleanField("Active", default=True)
    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=100, editable=False)
    avatar = ResizedImageField(
        size=[370, 259],
        default="accounts/avatars/default.png",
        upload_to="accounts/avatars",
    )
    first_name = None
    last_name = None

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "name"]

    class Meta:
        db_table = "users"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username}: {self.name}"

    def get_absolute_url(self):
        return reverse("team_detail", args=[self.username])

    def email_exists(self):
        return User.objects.filter(email=self.email).exists()

    def username_exists(self):
        return User.objects.filter(username=self.username).exists()


class NewsLetterSubscriber(models.Model):
    email = models.EmailField(max_length=80, unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "news_letter_subscribers"
        ordering = ["email"]

    def __str__(self):
        return self.email
