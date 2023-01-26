from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from accounts.models import NewsLetterSubscriber
from courses.models import Category, Course
from enroll.models import EnrolledCourse, Enrollment

User = get_user_model()


class SignUpViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="testuser",
            email="testuser@mail.com",
            username="testuser",
            password="secret",
        )
        self.url = reverse("sign_up")

    def test_signup_view_redirects_to_home_if_already_logged_in(self):
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.get(reverse("sign_up"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_signup_view_displays_error_message_if_name_not_provided(self):
        response = self.client.post(
            self.url,
            {
                "email": "test@example.com",
                "username": "testuser2",
                "password": "secret",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name required!")
        self.assertTemplateUsed(response, "sign-up.html")
        self.assertEqual(response.context["page_title"], "SignUp")

    def test_signup_view_displays_error_message_if_username_contains_invalid_characters(
        self,
    ):
        response = self.client.post(
            self.url,
            {
                "name": "Test User",
                "email": "test@example.com",
                "username": "test user",
                "password": "secret",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Username can only contain alphanumeric characters and underscore.",
        )

    def test_signup_view_displays_error_message_if_email_already_registered(self):
        response = self.client.post(
            self.url,
            {
                "name": "Test User",
                "email": "testuser@mail.com",
                "username": "testuser",
                "password": "secret",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "User with the email you provided already registered."
        )

    def test_signup_view_displays_error_message_if_username_already_taken(self):
        response = self.client.post(
            self.url,
            {
                "name": "Test User",
                "email": "test@example.com",
                "username": "testuser",
                "password": "secret",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Username you provided is already taken.")

    def test_signup_view_creates_new_user_and_logs_in_if_valid_data_provided(self):
        response = self.client.post(
            self.url,
            {
                "name": "Test User",
                "email": "test@example.com",
                "username": "testexample",
                "user_type": "student",
                "password": "secret",
            },
        )

        # assert user is redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

        # assert user is saved to the database
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
        auth_user_id = self.client.session.get("_auth_user_id")
        self.assertTrue(auth_user_id)
        self.assertEqual(auth_user_id, str(
            User.objects.get(username="testexample").pk))


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="testuser@mail.com",
            password="secret",
        )
        self.url = reverse("login")

    def test_login_view_redirects_to_home_if_already_logged_in(self):
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))

    def test_login_view_displays_error_message_if_invalid_credentials(self):
        response = self.client.post(
            self.url, {"email": "test@example.com",
                       "password": "wrongpassword"}
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Invalid email or password!")
        self.assertEqual(response.status_code, 200)

    def test_login_view_logs_in_user_and_redirects_to_next_if_valid_credentials(self):
        response = self.client.post(
            self.url,
            {
                "email": "testuser@mail.com",
                "password": "secret",
                "next": reverse("courses"),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("courses"))
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_login_view_logs_in_user_and_redirects_to_home_if_valid_credentials(self):
        response = self.client.post(
            reverse("login"), {"email": "testuser@mail.com",
                               "password": "secret"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(self.client.session.get("_auth_user_id"))


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="testuser@mail.com",
            password="secret",
        )
        self.url = reverse("logout")

    def test_logout_view_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))

    def test_logout_view_logs_out_user_and_redirects_to_login(self):
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertFalse(self.client.session.get("_auth_user_id"))


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="testuser@mail.com",
            password="secret",
        )
        # Create a teacher and a course
        self.teacher = User.objects.create_user(
            name="test teacher",
            username="testteacher",
            email="test@teacher.com",
            password="secret",
            is_student=False,
        )
        self.category = Category.objects.create(title="Test category")
        self.course = Course.objects.create(
            owner=self.teacher,
            title="Test Course",
            category=self.category,
            overview="The overview of a test course.",
            language="English",
            old_price=200,
            price=150,
            thumbnail="courses/thumbnails/course_img.png",
        )

        # Enroll the student in the course
        self.enrollment = Enrollment.objects.create(
            enrollment_id="123AB",
            student=self.user,
            amount=self.course.price,
        )
        EnrolledCourse.objects.create(
            enrollment=self.enrollment, course=self.course, student=self.user
        )

        self.url = reverse("profile")

    def test_profile_view_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login") +
                             "?next=" + reverse("profile"))

    def test_profile_view_displays_enrolled_courses_and_user_data(self):
        # Login user and assert the can see their enrolled course/user data
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_title"], "Profile")
        self.assertTemplateUsed(response, "my-profile.html")
        self.assertContains(response, "Test Course")
        self.assertContains(response, "testuser")

    def test_profile_view_does_not_display_courses_enrolled_by_other_users(self):
        other_user = User.objects.create_user(
            name="Other Test User",
            username="testuser2",
            email="testuser2@mail.com",
            password="secret",
        )

        # Create another course
        course = Course.objects.create(
            owner=self.teacher,
            title="Test Course for other user",
            category=self.category,
            overview="The overview of other test course.",
            language="English",
            old_price=200,
            price=150,
            thumbnail="courses/thumbnails/course_img.png",
        )

        # Enroll the student in the course
        enrollment = Enrollment.objects.create(
            enrollment_id="123AB",
            student=other_user,
            amount=course.price,
        )
        EnrolledCourse.objects.create(
            enrollment=enrollment, course=course, student=other_user
        )

        # login a user not enrolled in the second (other) course
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # assert user cannot see the second (other) course in their profile
        self.assertNotContains(response, "Test Course for other user")


class ProfileUpdateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="testuser@mail.com",
            password="secret",
            address="Test Address",
            phone="0711223344",
        )
        self.url = reverse("profile_update")

    def test_profile_update_view_GET_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_profile_update_view_POST_redirects_to_profile_if_name_provided(self):
        self.client.login(email="testuser@mail.com", password="secret")

        # send POST request with first time bio update
        response = self.client.post(
            self.url,
            {
                "name": "Test User Changed",
                "phone": "0712345678",
                "address": "Test Address Changed",
                "bio": "Test Bio",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # assert the details have been updated
        updated_user = User.objects.get(username="testuser")
        self.assertEqual(updated_user.name, "Test User Changed")
        self.assertEqual(updated_user.phone, "0712345678")
        self.assertEqual(updated_user.address, "Test Address Changed")

        # assert the missing bio updated
        self.assertEqual(updated_user.bio, "Test Bio")

    def test_profile_update_view_displays_error_message_if_name_not_provided(self):
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.post(
            self.url,
            {
                "phone": "0712345678",
                "address": "Test Address Changed",
                "bio": "Test Bio",
            },
        )

        # assert that the profile was not updated
        not_updated_user = User.objects.get(username="testuser")
        self.assertEqual(not_updated_user.name, "Test User")
        self.assertNotEqual(not_updated_user.phone, "0712345678")
        self.assertNotEqual(not_updated_user.address, "Test Address Changed")
        self.assertNotEqual(not_updated_user.bio, "Test Bio")

        # assert error messages is shown to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Profile not updated. Name cannot be empty!")


class PasswordChangeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="testuser@mail.com",
            password="secret",
        )
        self.url = reverse("password_change")

    def test_password_change_view_redirects_to_login_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login") + "?next=" + self.url)

    def test_password_change_view_displays_error_message_if_passwords_dont_match(self):
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.post(
            self.url,
            {
                "current_password": "secret",
                "new_password": "newpassword",
                "new_password2": "newpassword2",
            },
        )

        # assert error message is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "The passwords you entered do not match!")

    def test_password_change_view_displays_error_message_if_current_password_is_wrong(
        self,
    ):
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.post(
            self.url,
            {
                "current_password": "wrongpassword",
                "new_password": "newpassword",
                "new_password2": "newpassword",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # assert error message is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]),
                         "The current password entered is wrong.")

    # TODO: Test password change email sent.


class PasswordResetViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            name="Test User",
            username="testuser",
            email="testuser@mail.com",
            password="secret",
        )
        self.url = reverse("password_reset")

    def test_password_reset_view_redirects_to_password_reset_done_if_user_exists(self):
        response = self.client.post(self.url, {"email": "testuser@mail.com"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("password_reset_done"))

    def test_password_reset_view_displays_error_message_if_user_does_not_exist(self):
        response = self.client.post(self.url, {"email": "wrong@mail.com"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("password_reset"))

        # assert info message is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), "Sorry, user with the provided email does not exist."
        )


class NewsLetterSubscriptionViewTests(TestCase):
    def setUp(self):
        self.url = reverse("news_letter_subscription")
        self.referrer_url = reverse("about")

    def test_newsletter_subscription_view_subscribes_user_if_not_already_subscribed(
        self,
    ):
        response = self.client.post(
            self.url,
            {"email": "testsubscriber@example.com"},
            HTTP_REFERER=self.referrer_url,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.referrer_url)

        # assert success message is shown to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), "Thanks for subscribing to our newsletter.")
        self.assertTrue(
            NewsLetterSubscriber.objects.filter(
                email="testsubscriber@example.com"
            ).exists()
        )

    def test_newsletter_subscription_view_displays_error_message_if_already_subscribed(
        self,
    ):
        NewsLetterSubscriber.objects.create(email="testsubscriber@example.com")
        response = self.client.post(
            self.url,
            {"email": "testsubscriber@example.com"},
            HTTP_REFERER=self.referrer_url,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.referrer_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]), "You've already subscribed to our newsletter."
        )
