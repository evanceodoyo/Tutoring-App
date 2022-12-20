from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Category, Course
from django.urls import reverse

User = get_user_model()

class AddToCartTests(TestCase):
    def setUp(self):
        pass