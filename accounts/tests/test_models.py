from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()



class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name="Test User", username='testuser', email='testuser@mail.com', password='secret')

    def test_user_created_with_correct_fields(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@mail.com')
        self.assertEqual(self.user.name, 'Test User')

    def test_email_exists_method_returns_correct_result(self):
        self.assertTrue(self.user.email_exists())
        # self.assertRaises(User.DoesNotExist, User.objects.get(email='notexist@example.com').email_exists())

    def test_username_exists_method_returns_correct_result(self):
        self.assertTrue(self.user.username_exists())
        # self.assertRaises(User.DoesNotExist, User.objects.get(username='notexist').username_exists())

    def test_get_absolute_url_returns_correct_url(self):
        self.assertEqual(self.user.get_absolute_url(), '/team/testuser/')

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), 'testuser: Test User')