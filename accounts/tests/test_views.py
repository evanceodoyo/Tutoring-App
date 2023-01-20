from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class SignUpViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name="testuser", email="testuser@mail.com", username='testuser', password='secret')
        self.url = reverse('sign_up')

    def test_signup_view_redirects_to_home_if_already_logged_in(self):
        self.client.login(email='testuser@mail.com', password='secret')
        response = self.client.get(reverse('sign_up'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_signup_view_displays_error_message_if_name_not_provided(self):
        response = self.client.post(self.url, {'email': 'test@example.com', 'username': 'testuser2', 'password': 'secret'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Name required!')
        self.assertTemplateUsed(response, "sign-up.html")
        self.assertEqual(response.context['page_title'], "SignUp")


    def test_signup_view_displays_error_message_if_username_contains_invalid_characters(self):
        response = self.client.post(self.url, {'name': 'Test User', 'email': 'test@example.com', 'username': 'test user', 'password': 'secret'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username can only contain alphanumeric characters and underscore.')

    def test_signup_view_displays_error_message_if_email_already_registered(self):
        response = self.client.post(self.url, {'name': 'Test User', 'email': 'testuser@mail.com', 'username': 'testuser', 'password': 'secret'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User with the email you provided already registered.')

    def test_signup_view_displays_error_message_if_username_already_taken(self):
        response = self.client.post(self.url, {'name': 'Test User', 'email': 'test@example.com', 'username': 'testuser', 'password': 'secret'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username you provided is already taken.')

    def test_signup_view_creates_new_user_and_logs_in_if_valid_data_provided(self):
        response = self.client.post(self.url, {'name': 'Test User', 'email': 'test@example.com', 'username': 'testexample', "user_type": 'student', 'password': 'secret'})

        # assert user is redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

        # assert user is saved to the database
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        auth_user_id = self.client.session.get('_auth_user_id')
        self.assertTrue(auth_user_id)
        self.assertEqual(auth_user_id, str(User.objects.get(username='testexample').pk))

    