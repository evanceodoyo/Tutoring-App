from django.test import TestCase
from django.urls import reverse, resolve
from courses.views import (
    courseDetail,
    courseReview,
    myCourses,
    teamDetail,
    teacherReview,
    tag,
    category,
)


class CourseRouteTests(TestCase):
    def test_home_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_url_available_by_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_blog_homepage_template_used_correct(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "index.html")

    def test_courses_list_url(self):
        response = self.client.get(reverse("courses"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courses.html")

    def test_courses_list_at_correct_location(self):
        response = self.client.get("/courses/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "courses.html")

    def test_course_detail_url(self):
        url = reverse("course_detail", kwargs={"course_slug": "test-course-slug"})
        self.assertEqual(url, "/course/test-course-slug/")
        self.assertEqual(resolve(url).func, courseDetail)

    def test_course_review_url(self):
        url = reverse("course_review", kwargs={"course_slug": "test-course-slug"})
        self.assertEqual(url, "/course/review/test-course-slug/")
        self.assertEqual(resolve(url).func, courseReview)

    def test_my_courses_list_url(self):
        url = reverse("my_courses")
        self.assertEqual(resolve(url).func, myCourses)

    def test_team_url_available_at_correct_url(self):
        response = self.client.get("/team/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "team.html")

    def test_team_url_available_by_name(self):
        response = self.client.get(reverse("team"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "team.html")

    def test_team_detail_url(self):
        url = reverse("team_detail", kwargs={"username": "testuser"})
        self.assertEqual(url, "/team/testuser/")
        self.assertEqual(resolve(url).func, teamDetail)

    def test_team_review_url(self):
        url = reverse("teacher_review", kwargs={"username": "testteacher"})
        self.assertEqual(url, "/team/review/testteacher/")
        self.assertEqual(resolve(url).func, teacherReview)

    def test_category_detail_url(self):
        url = reverse("category", kwargs={"category_slug": "test-category"})
        self.assertEqual(url, "/category/test-category/")
        self.assertEqual(resolve(url).func, category)

    def test_tag_detail_url(self):
        url = reverse("tag", kwargs={"tag_slug": "test-tag"})
        self.assertEqual(url, "/tag/test-tag/")
        self.assertEqual(resolve(url).func, tag)

    def test_about_url_available_at_correct_url(self):
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")

    def test_about_url_available_by_name(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")
