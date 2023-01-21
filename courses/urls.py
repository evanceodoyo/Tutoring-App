from django.urls import path

from .views import (about, category, courseDetail, courseList, courseReview,
                    home, myCourses, search, tag, teacherReview, team,
                    teamDetail)

urlpatterns = [
    path("", home, name="home"),
    path("courses/", courseList, name="courses"),
    path("course/<slug:course_slug>/", courseDetail, name="course_detail"),
    path("course/review/<slug:course_slug>/", courseReview, name="course_review"),
    path("my-courses/", myCourses, name="my_courses"),
    path("team/<username>/", teamDetail, name="team_detail"),
    path("team/review/<username>/", teacherReview, name="teacher_review"),
    path("category/<slug:category_slug>/", category, name="category"),
    path("tag/<slug:tag_slug>/", tag, name="tag"),
    path("team/", team, name="team"),
    path("about/", about, name="about"),
    path("search/", search, name="search"),
]
