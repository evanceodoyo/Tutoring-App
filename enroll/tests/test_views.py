from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from courses.models import Category, Course, Tag
from enroll.models import Enrollment, EnrolledCourse
from django.urls import reverse

User = get_user_model()

class AddToCartTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            name="test teacher",
            username="testteacher",
            email="test@teacher.com",
            password="secret",
            is_student=False,
        )
        self.student = User.objects.create_user(
            name="test student",
            username="teststudent",
            email="test@student.com",
            password="secret",
            is_student=True,
        )
        self.category = Category.objects.create(title="Test category")
        self.tag = Tag.objects.create(title="Test tag")
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

    def test_add_to_cart_logged_in(self):
        self.client.force_login(self.student)        
        # send a GET request to the addToCart view with the test course id
        response = self.client.get(reverse('add_to_cart'), {'course_id': self.course.pk})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.course.get_absolute_url())
        
        # check the cart in the session
        cart = self.client.session.get("cart")
        self.assertIsNotNone(cart)
        self.assertEqual(cart[str(self.course.pk)], 1)
        
        # assert that a success message is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), f"{self.course.title} added to cart successfully."
        )
    
    def test_add_to_cart_not_logged_in(self):
        # send a GET request to the addToCart view with the test course id
        response = self.client.get(reverse('add_to_cart'), {'course_id': self.course.pk})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.course.get_absolute_url())
        
        # check the cart in the session
        cart = self.client.session.get("cart")
        self.assertIsNotNone(cart)
        self.assertEqual(cart[str(self.course.pk)], 1)
        
        # assert that a success message is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), f"{self.course.title} added to cart successfully."
        )
        
    def test_add_to_cart_already_enrolled(self):
        enrollment = Enrollment.objects.create(
            enrollment_id="123AB",
            student=self.student,
            amount=self.course.price,
        )
        EnrolledCourse.objects.create(
            enrollment=enrollment, course=self.course, student=self.student
        )
        # login the test user
        self.client.force_login(self.student)
        response = self.client.get(reverse('add_to_cart'), {'course_id': self.course.pk})
        self.assertEqual(response.status_code, 302)
        
        # assert that the user is redirected to the my_courses page
        self.assertRedirects(response, reverse('my_courses'))
        
        # assert that an info message is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You are already enrolled for this course.")

        
    def test_add_to_cart_course_not_found(self):
        # send a GET request to the addToCart view with an invalid course id
        response = self.client.get(reverse('add_to_cart'), {'course_id': 99999999})
        self.assertEqual(response.status_code, 404)

class CartTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            name="test teacher",
            username="testteacher",
            email="test@teacher.com",
            password="secret",
            is_student=False,
        )
        self.student = User.objects.create_user(
            name="test student",
            username="teststudent",
            email="test@student.com",
            password="secret",
            is_student=True,
        )
        self.category = Category.objects.create(title="Test category")
        self.tag = Tag.objects.create(title="Test tag")
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
        self.url = reverse("cart")

    def test_get_cart_view_sets_page_title(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_title'], 'Cart')
        self.assertTemplateUsed(response, 'cart.html')

    def test_cart_view_adds_cart_courses_and_total_to_context(self):
        # simulate cart exists
        session = self.client.session
        session['cart'] = {str(self.course.pk): 1}
        session.save()

        response = self.client.get(self.url)
        self.assertIsNotNone(response.context['cart_courses'])
        self.assertIsNotNone(response.context['cart_total'])
        self.assertEqual(response.context['cart_total'], 150.0)

    def test_cart_view_removes_course_from_cart(self):
        course = Course.objects.create(
            owner=self.teacher,
            title="Test Course 2",
            category=self.category,
            overview="The overview of a test course 2.",
            language="English",
            old_price=150,
            price=100,
            thumbnail="courses/thumbnails/course_img.png",
        )
        
        # simulate courses in cart
        session = self.client.session
        session['cart'] = {str(self.course.pk): 1}
        session['cart'].update({str(course.pk): 1})
        session.save()

        # send a GET request to the cart view with the test course id
        # To remove `Test Course` from cart.
        response = self.client.get(reverse('cart'), {'course_id': self.course.pk})
        self.assertNotIn(str(self.course.pk), self.client.session['cart'])

        # assert that an info message is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Course removed from cart successfully.")

        # assert user is redirected to cart
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("cart"))



class CheckoutViewTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            name="test teacher",
            username="testteacher",
            email="test@teacher.com",
            password="secret",
            is_student=False,
        )
        self.student = User.objects.create_user(
            name="test student",
            username="teststudent",
            email="test@student.com",
            password="secret",
            is_student=True,
        )
        self.category = Category.objects.create(title="Test category")
        self.tag = Tag.objects.create(title="Test tag")
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
        self.url = reverse("checkout")

    def test_checkout_view_redirects_to_login_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/enroll/checkout/')
        self.assertRedirects(response, reverse('login') + '?next=/enroll/checkout/')

    def test_checkout_view_displays_error_message_if_cart_empty(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("courses"))

        # assert info is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Please select course(s) to enroll first.')

    def test_checkout_view_removes_enrolled_course_from_cart(self):
        enrollment = Enrollment.objects.create(
            enrollment_id="123AB",
            student=self.student,
            amount=self.course.price,
        )
        EnrolledCourse.objects.create(
            enrollment=enrollment, course=self.course, student=self.student
        )

        course = Course.objects.create(
            owner=self.teacher,
            title="Test Course 2",
            category=self.category,
            overview="The overview of a test course 2.",
            language="English",
            old_price=150,
            price=100,
            thumbnail="courses/thumbnails/course_img.png",
        )
        # self.client.get(reverse('add_to_cart'), {'course_id': self.course.pk})
        # self.client.get(reverse('add_to_cart'), {'course_id': course.pk})

        session = self.client.session
        session['cart'] = {str(self.course.pk): 1}
        session['cart'].update({str(course.pk): 1})
        session.save()
        self.client.force_login(self.student)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('checkout'))

        # assert info is displayed to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'{self.course.title} removed. You are enrolled for the course already!')

        # assert the enrolled course does not exist in cart
        self.assertNotIn(str(self.course.pk), self.client.session['cart'])
        

    def test_checkout_view_enrolls_user_in_courses_and_clears_cart(self):
        self.client.force_login(self.student)
        session = self.client.session
        session['cart'] = {str(self.course.pk): 1}
        session.save()

        # send POST request to the checkout view
        response = self.client.post(reverse('checkout'))

        # assert the user is redirected
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('my_courses'))

        # assert the enrollment is saved in the database
        enrollment = Enrollment.objects.all()
        enrolled_course = EnrolledCourse.objects.all()
        self.assertEqual(enrollment.count(), 1)
        self.assertEqual(enrolled_course.count(), 1)

        # 
        self.assertEqual(enrollment.first().student, self.student)
        self.assertEqual(enrolled_course.first().student, self.student)

        # assert cart is cleared on successful enrollment
        self.assertEqual(self.client.session['cart'], {})

        # assert success messages show to the user
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Enrollment successful. Thank you!")