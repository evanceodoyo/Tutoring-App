from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from courses.models import (
    Category,
    Course,
    Tag,
    CourseTag,
    TeacherReviewRating,
    CourseReviewRating,
)
from enroll.models import Enrollment, EnrolledCourse
from blog.models import Article
from django.contrib.messages import get_messages

User = get_user_model()


class HomeTests(TestCase):
    def setUp(self):
        self.url = reverse("home")
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

        self.enrollment = Enrollment.objects.create(
            enrollment_id="123AB",
            student=self.student,
            amount=self.course.price,
        )
        self.enrolled_course = EnrolledCourse.objects.create(
            enrollment=self.enrollment, course=self.course, student=self.student
        )
        self.course_review = CourseReviewRating.objects.create(
            user=self.student,
            course=self.course,
            title="Test Review",
            comment="Test comment",
            rating=5,
            is_active=True,
        )

    def test_featured_home_courses(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        courses = Course.objects.annotate(
            avg_rating=Avg("course_reviews__rating")
        ).filter(is_active=True)
        self.assertQuerysetEqual(response.context["courses"], courses)
        self.assertEqual(response.context["courses"].first().avg_rating, 5.0)
        self.assertTemplateUsed(response, "index.html")

    def test_featured_courses_title(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        course = response.context["courses"].first()
        self.assertEqual(course.title, "Test Course")
        self.assertEqual(course.owner, self.teacher)
        self.assertIs(course.owner.is_student, False)

    def test_test_featured_courses_rating(self):
        student = User.objects.create_user(
            name="test student 2",
            username="teststudent2",
            email="test@student2.com",
            password="secret",
        )

        CourseReviewRating.objects.create(
            user=student,
            course=self.course,
            title="Test Review 2",
            comment="Test comment 2",
            rating=4,
            is_active=True,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        courses = response.context["courses"]
        self.assertEqual(courses.first().avg_rating, 4.5)

    def test_student_count_is_correct(self):
        student = User.objects.create_user(
            name="test student 2",
            username="teststudent2",
            email="test@student2.com",
            password="secret",
        )
        enrollment = Enrollment.objects.create(
            enrollment_id="123BC",
            student=student,
            amount=self.course.price,
        )
        EnrolledCourse.objects.create(
            enrollment=enrollment, course=self.course, student=student
        )
        response = self.client.get(self.url)
        student_count = response.context["student_count"]
        student_count_2 = EnrolledCourse.objects.aggregate(
            sc=Count("student", distinct=True)
        )
        self.assertEqual(student_count, 2)
        self.assertEqual(student_count_2["sc"], 2)

    def test_teacher_count_is_correct(self):
        response = self.client.get(self.url)
        teacher_count = Course.objects.aggregate(tc=Count("owner", distinct=True))
        self.assertEqual(response.context["teacher_count"], 1)
        self.assertEqual(teacher_count["tc"], 1)

    def test_home_renders_articles(self):
        Article.objects.create(
            author=self.teacher,
            title="Test article title 1",
            content="The content of the article for article 1.",
            thumbnail="blog/images/default.jpeg",
        )
        Article.objects.create(
            author=self.student,
            title="Test article title 2",
            content="The content of the article for article 2.",
            thumbnail="blog/images/default.jpeg",
        )
        response = self.client.get(self.url)
        articles = response.context["articles"]
        articles_2 = Article.objects.all()
        self.assertCountEqual(articles, articles_2)
        self.assertEqual(articles.first().title, "Test article title 2")
        self.assertEqual(articles.first().author, self.student)


class CourseListView(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            name="test teacher",
            username="testteacher",
            email="test@teacher.com",
            password="secret",
            is_student=False,
        )
        self.category = Category.objects.create(title="Test category")
        self.courses = [
            Course.objects.create(
                owner=self.teacher,
                title=f"Test Course {course_id}",
                category=self.category,
                overview=f"The overview of a test course {course_id}.",
                language="English",
                old_price=200,
                price=150,
                thumbnail="courses/thumbnails/course_img.png",
            )
            for course_id in range(1, 16)
        ]
        self.url = reverse("courses")

    def test_courses_pagination_is_six(self):
        response = self.client.get(self.url)
        courses = response.context["courses"]
        self.assertEqual(response.status_code, 200)
        # check that the page has the correct number of items.
        self.assertEqual(courses.paginator.per_page, 6)
        # check that the page has correct items.
        self.assertEqual(list(courses), self.courses[:6])

    def test_pagination_with_GET_page(self):
        response = self.client.get(self.url, {"page": 2})
        courses = response.context["courses"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(courses.paginator.per_page, 6)
        self.assertEqual(list(courses), self.courses[6:12])

    def test_all_courses_in_list_is_active(self):
        for course in self.courses:
            self.assertIs(course.is_active, True)

        response = self.client.get(self.url)
        courses = response.context["courses"]
        for course in list(courses):
            self.assertIs(course.is_active, True)

    def test_courses_list_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_title"], "Our Courses")
        self.assertTemplateUsed(response, "courses.html")


class CourseDetailView(TestCase):
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
        self.enrollment = Enrollment.objects.create(
            enrollment_id="123AB",
            student=self.student,
            amount=self.course.price,
        )
        self.enrolled_course = EnrolledCourse.objects.create(
            enrollment=self.enrollment, course=self.course, student=self.student
        )
        self.course_review = CourseReviewRating.objects.create(
            user=self.student,
            course=self.course,
            title="Test Review",
            comment="Test comment",
            rating=5,
            is_active=True,
        )
        self.url = reverse("course_detail", kwargs={"course_slug": self.course.slug})

    def test_course_detail_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_title"], self.course.title)
        self.assertEqual(response.context["course"], self.course)
        self.assertTemplateUsed(response, "course-details.html")

    def test_course_detail_with_hardcoded_url(self):
        response = self.client.get(
            reverse("course_detail", kwargs={"course_slug": "test-course"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["course"], self.course)
        self.assertTemplateUsed(response, "course-details.html")

    def test_course_detail_with_invalid_slug_returns_404(self):
        response = self.client.get(
            reverse(
                "course_detail",
                kwargs={"course_slug": "invalid-slug"},
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_course_is_active(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIs(self.course.is_active, True)
        self.assertEqual(response.context["course"].is_active, True)

    def test_course_detail_view_with_inactive_course(self):
        # Create an inactive course
        Course.objects.create(
            owner=self.teacher,
            title="Test Course 2",
            category=self.category,
            overview="The overview of a test course 2.",
            language="English",
            old_price=200,
            price=150,
            thumbnail="courses/thumbnails/course_img.png",
            is_active=False,
        )

        # Send a GET request to the view with the slug of an inactive course
        response = self.client.get(
            reverse("course_detail", kwargs={"course_slug": "test-course-2"})
        )

        # Check that the response is 404 (Not Found)
        self.assertEqual(response.status_code, 404)

    def test_related_courses(self):
        course_2 = Course.objects.create(
            owner=self.teacher,
            title="Test Course 2",
            category=self.category,
            overview="The overview of a test course 2.",
            language="English",
            old_price=200,
            price=150,
            thumbnail="courses/thumbnails/course_img.png",
            is_active=False,
        )
        CourseTag.objects.create(course=self.course, tag=self.tag)
        CourseTag.objects.create(course=course_2, tag=self.tag)
        response = self.client.get(self.url)
        related_courses = response.context["related_courses"]
        # self.assertEqual(related_courses.first().title, 'Test Course 2')

    def test_my_courses_view(self):
        self.client.login(email="test@student.com", password="secret")
        response = self.client.get(reverse("my_courses"))
        enrolled_courses = response.context["enrolled_courses"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(enrolled_courses.first(), self.enrolled_course)
        self.assertEqual(enrolled_courses.first().course.title, "Test Course")
        self.assertTemplateUsed(response, "my-courses.html")


class TeamViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Test category")
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
        )
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
        self.teacher_rating = TeacherReviewRating.objects.create(
            user=self.student,
            teacher=self.teacher,
            is_active=True,
            comment="Test comment on teacher",
            rating=5,
        )
        self.url = reverse("team")

    def test_team_course_owner_is_correct(self):
        response = self.client.get(self.url)
        course_teachers = response.context["course_teachers"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_title"], "Team")
        self.assertEqual(course_teachers.first().owner, self.teacher)

    def test_team_testimonial(self):
        response = self.client.get(self.url)
        testimonials = response.context["testimonials"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(testimonials.first().comment, "Test comment on teacher")
        self.assertTemplateUsed(response, "team.html")

    def test_team_testimonials_are_active(self):
        student_2 = User.objects.create_user(
            name="test student 2",
            username="teststudent2",
            email="test@student_2@mail.com",
            password="secret",
        )
        TeacherReviewRating.objects.create(
            user=student_2,
            teacher=self.teacher,
            is_active=False,
            comment="Test comment on teacher",
            rating=5,
        )
        response = self.client.get(self.url)
        testimonials = response.context["testimonials"]
        self.assertEqual(len(testimonials), 1)
        for t in testimonials:
            self.assertIs(t.is_active, True)


class TeamDetailViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Test category")
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
        )
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
        self.teacher_rating = TeacherReviewRating.objects.create(
            user=self.student,
            teacher=self.teacher,
            is_active=True,
            comment="Test comment on teacher",
            rating=5,
        )
        self.url = reverse("team_detail", kwargs={"username": self.teacher.username})

    def test_team_detail_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_title"], "Team Details")
        self.assertEqual(response.context["teacher"], self.teacher)

    def test_team_detail_with_hardcoded_url(self):
        response = self.client.get(
            reverse("team_detail", kwargs={"username": "testteacher"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["teacher"], self.teacher)
        self.assertEqual(response.context["teacher"].name, "test teacher")

    def test_team_avg_rating(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context["teacher"].avg_rating, 5.0)
        self.assertTemplateUsed(response, "team-details.html")

    def test_team_core_courses_correct(self):
        response = self.client.get(self.url)
        core_courses = response.context["core_courses"]
        self.assertEqual(core_courses.first(), self.course)
        self.assertEqual(core_courses.first().owner, self.course.owner)

    def test_GET_team_detail_with_invalid_username_returns_404(self):
        response = self.client.get(
            reverse("team_detail", kwargs={"username": "invalid_username"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")


class CourseReviewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Test category")
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
        self.enrollment = Enrollment.objects.create(
            enrollment_id="123AB",
            student=self.student,
            amount=self.course.price,
        )
        self.enrolled_course = EnrolledCourse.objects.create(
            enrollment=self.enrollment, course=self.course, student=self.student
        )

    def test_course_review_POST_with_user_enrolled_in_course(self):
        self.client.login(email="test@student.com", password="secret")
        response = self.client.post(
            reverse("course_review", kwargs={"course_slug": self.course.slug}),
            {"title": "Test review", "comment": "Test comment", "rating": 5},
        )

        self.assertEqual(response.status_code, 302)
        # Test that the review was saved in the database
        self.assertEqual(CourseReviewRating.objects.count(), 1)
        course_review_rating = CourseReviewRating.objects.first()
        self.assertEqual(course_review_rating.user, self.student)
        self.assertEqual(course_review_rating.title, "Test review")
        self.assertEqual(course_review_rating.rating, 5)
        # Get the message from the response using wsgi
        # since response has no context
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Thank you! Your review has been submitted successfully."
        )

    def test_course_review_POST_with_user_not_enrolled_in_course(self):
        User.objects.create_user(
            name="test student 1",
            username="teststudent1",
            email="test@student1.com",
            password="secret",
            is_student=True,
        )
        self.client.login(email="test@student1.com", password="secret")
        response = self.client.post(
            reverse("course_review", kwargs={"course_slug": self.course.slug}),
            {"title": "Test review", "comment": "Test comment", "rating": 5},
        )

        self.assertEqual(response.status_code, 302)
        # Test that the review was not saved in the database
        self.assertEqual(CourseReviewRating.objects.count(), 0)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Only students who are already enrolled in this course can make reviews.",
        )

    def test_course_review_POST_with_user_enrolled_in_course_update_review(self):
        CourseReviewRating.objects.create(
            user=self.student,
            course=self.course,
            title="Test Review",
            comment="Test comment",
            rating=5,
            is_active=True,
        )
        self.client.login(email="test@student.com", password="secret")
        response = self.client.post(
            reverse("course_review", kwargs={"course_slug": self.course.slug}),
            {
                "title": "Test review updated",
                "comment": "Test comment updated",
                "rating": 4,
            },
        )

        self.assertEqual(response.status_code, 302)
        # Test that the review was updated in the database
        self.assertEqual(CourseReviewRating.objects.count(), 1)
        course_review_rating = CourseReviewRating.objects.first()
        self.assertEqual(course_review_rating.user, self.student)
        self.assertEqual(course_review_rating.title, "Test review updated")
        self.assertEqual(course_review_rating.rating, 4)
        # Get the message from the response using wsgi
        # since response has no context
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Thank you! Your review has been updated successfully."
        )

    def test_course_review_POST_course_owner_cannot_review_course(self):
        self.client.login(email="test@teacher.com", password="secret")
        response = self.client.post(
            reverse("course_review", kwargs={"course_slug": self.course.slug}),
            {"title": "Test review", "comment": "Test comment", "rating": 4},
        )

        self.assertEqual(response.status_code, 302)
        # Test that the review was updated in the database
        self.assertEqual(CourseReviewRating.objects.count(), 0)
        # Get the message from the response using wsgi
        # since response has no context
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Only students who are already enrolled in this course can make reviews.",
        )


class TeacherReviewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Test category")
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
        self.enrollment = Enrollment.objects.create(
            enrollment_id="123AB",
            student=self.student,
            amount=self.course.price,
        )
        self.enrolled_course = EnrolledCourse.objects.create(
            enrollment=self.enrollment, course=self.course, student=self.student
        )

    def test_teacher_review_POST_with_user_enrolled_in_teacher_course(self):
        self.client.login(email="test@student.com", password="secret")
        response = self.client.post(
            reverse("teacher_review", kwargs={"username": self.teacher.username}),
            {"comment": "Test comment on teacher", "rating": 5},
        )

        self.assertEqual(response.status_code, 302)
        # Test that the review was saved in the database
        self.assertEqual(TeacherReviewRating.objects.count(), 1)
        teacher_review_rating = TeacherReviewRating.objects.first()
        self.assertEqual(teacher_review_rating.user, self.student)
        self.assertEqual(teacher_review_rating.comment, "Test comment on teacher")
        self.assertEqual(teacher_review_rating.rating, 5)
        # Get the message from the response using wsgi
        # since response has no context
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Thank you! Your review has been submitted successfully."
        )

    def test_teacher_review_POST_with_user_not_enrolled_in_teacher_course(self):
        User.objects.create_user(
            name="test student 1",
            username="teststudent1",
            email="test@student1.com",
            password="secret",
            is_student=True,
        )
        self.client.login(email="test@student1.com", password="secret")
        response = self.client.post(
            reverse("teacher_review", kwargs={"username": self.teacher.username}),
            {"comment": "Test comment on teacher", "rating": 5},
        )

        self.assertEqual(response.status_code, 302)
        # Test that the review was not saved in the database
        self.assertEqual(TeacherReviewRating.objects.count(), 0)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Only students enrolled in the teacher's courses can make reviews.",
        )

    def test_teacher_review_POST_with_user_enrolled_in_teacher_course_update_review(
        self,
    ):
        TeacherReviewRating.objects.create(
            user=self.student,
            teacher=self.teacher,
            comment="Test comment on teacher",
            rating=5,
            is_active=True,
        )
        self.client.login(email="test@student.com", password="secret")
        response = self.client.post(
            reverse("teacher_review", kwargs={"username": self.teacher.username}),
            {"comment": "Test comment on teacher updated", "rating": 4},
        )

        self.assertEqual(response.status_code, 302)
        # Test that the review was updated in the database
        self.assertEqual(TeacherReviewRating.objects.count(), 1)
        teacher_review_rating = TeacherReviewRating.objects.first()
        self.assertEqual(teacher_review_rating.user, self.student)
        self.assertEqual(
            teacher_review_rating.comment, "Test comment on teacher updated"
        )
        self.assertEqual(teacher_review_rating.rating, 4)
        # Get the message from the response using wsgi
        # since response has no context
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Thank you! Your review has been updated successfully."
        )

    def test_teacher_review_POST_teacher_cannot_review_self(self):
        self.client.login(email="test@teacher.com", password="secret")
        response = self.client.post(
            reverse("teacher_review", kwargs={"username": self.teacher.username}),
            {"comment": "Test comment on teacher by self", "rating": 4},
        )

        self.assertEqual(response.status_code, 302)
        # Test that the review was updated in the database
        self.assertEqual(TeacherReviewRating.objects.count(), 0)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Only students enrolled in the teacher's courses can make reviews.",
        )
