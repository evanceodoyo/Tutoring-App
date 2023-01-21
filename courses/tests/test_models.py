from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from courses.models import Category, Course, Tag

User = get_user_model()


class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Test Category")

    def test_category_title(self):
        self.assertEqual(self.category.title, "Test Category")

    def test_create_category_with_duplicate_title_raises_integrity_error(self):
        # Try to create a duplicate category
        with self.assertRaises(IntegrityError) as cm:
            Category.objects.create(title="Test Category")

        # Check that the error message is correct
        self.assertEqual(
            str(cm.exception),
            'duplicate key value violates unique constraint "categories_title_key"\nDETAIL:  Key (title)=(Test Category) already exists.\n',
        )

    def test_category_assigned_correct_slug_on_creation(self):
        self.assertEqual(self.category.slug, "test-category")

    def test_category_get_absolute_url(self):
        self.assertEqual(self.category.get_absolute_url(), "/category/test-category/")


class TagModelTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(title="Test tag")

    def test_tag_title(self):
        self.assertEqual(self.tag.title, "Test tag")

    def test_create_tag_with_duplicate_title_raises_integrity_error(self):
        # Try to create a duplicate tag
        with self.assertRaises(IntegrityError) as cm:
            Tag.objects.create(title="Test tag")

        # Check that the error message is correct
        self.assertEqual(
            str(cm.exception),
            'duplicate key value violates unique constraint "tags_title_key"\nDETAIL:  Key (title)=(Test tag) already exists.\n',
        )

    def test_tag_assigned_correct_slug_on_creation(self):
        self.assertEqual(self.tag.slug, "test-tag")

    def test_tag_get_absolute_url(self):
        self.assertEqual(self.tag.get_absolute_url(), "/tag/test-tag/")


class CourseModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            name="testuser",
            email="testuser@mail.com",
            username="testuer",
            password="secret",
        )
        self.category = Category.objects.create(title="Test Category")
        self.course = Course.objects.create(
            owner=self.owner,
            title="Test Course",
            category=self.category,
            overview="The overview of test course.",
            language="English",
            old_price=100,
            price=95,
            thumbnail="courses/thumbnails/course_img.png",
        )

    def test_course_object_name_is_course_title(self):
        self.assertEqual(str(self.course), self.course.title)

    def test_number_of_lessons_label(self):
        field_label = self.course._meta.get_field("lessons").verbose_name
        self.assertEqual(field_label, "Number of Lessons")

    def test_number_of_weeks_label(self):
        field_label = self.course._meta.get_field("number_of_weeks").verbose_name
        self.assertEqual(field_label, "Number of Weeks")

    def test_course_title_and_(self):
        self.assertEqual(self.course.title, "Test Course")
        self.assertEqual(self.course.overview, "The overview of test course.")
        self.assertEqual(self.course.category, self.category)
        self.assertEqual(self.course.old_price, 100)
        self.assertEqual(self.course.price, 95)
        self.assertEqual(self.course.owner, self.owner)

    def test_course_default_weeks_and_lessons(self):
        self.assertEqual(self.course.lessons, 12)
        self.assertEqual(self.course.number_of_weeks, 8)

    def test_course_not_default_weeks_and_lessons(self):
        self.course.lessons = 25
        self.course.number_of_weeks = 12
        self.assertEqual(self.course.lessons, 25)
        self.assertEqual(self.course.number_of_weeks, 12)

    def test_correct_course_slug_generated_on_creation(self):
        self.assertEqual(self.course.slug, "test-course")

    def test_create_course_with_duplicate_title_raises_integrity_error(self):
        # Try to create a duplicate course
        with self.assertRaises(IntegrityError) as cm:
            Course.objects.create(
                owner=self.owner,
                title="Test Course",
                category=self.category,
                overview="The overview of duplicate test course.",
                language="English",
                old_price=200,
                price=150,
                thumbnail="courses/thumbnails/course_img.png",
            )

        # Check that the error message is correct
        self.assertEqual(
            str(cm.exception),
            'duplicate key value violates unique constraint "courses_title_key"\nDETAIL:  Key (title)=(Test Course) already exists.\n',
        )

    def test_course_get_absolute_url(self):
        self.assertEqual(self.course.get_absolute_url(), "/course/test-course/")

    def test_course_discount_method_returns_correct_percentage(self):
        expected_discount = round(
            (self.course.old_price - self.course.price) / self.course.old_price * 100
        )
        self.assertEqual(self.course.discount, expected_discount)

    def test_course_get_courses_id_method_returns_correct_courses(self):
        Course.objects.create(
            owner=self.owner,
            title="Test Course 1",
            category=self.category,
            overview="The overview of test course 1.",
            language="English",
            old_price=200,
            price=150,
            thumbnail="courses/thumbnails/course_img.png",
        )
        Course.objects.create(
            owner=self.owner,
            title="Test Course 2",
            category=self.category,
            overview="The overview of test course 2.",
            language="French",
            old_price=200,
            price=150,
            thumbnail="courses/thumbnails/course_img.png",
        )
        ids = [2, 3]
        course_qs_1 = Course.objects.filter(id__in=ids)
        course_qs_2 = Course.get_courses_by_id(ids)
        self.assertQuerysetEqual(course_qs_1, course_qs_2)
        # check correct courses return if order changes
        self.assertCountEqual(course_qs_1, course_qs_2)
        self.assertNotEqual(len(course_qs_2), len(Course.objects.all()))


# TODO test _meta fields
