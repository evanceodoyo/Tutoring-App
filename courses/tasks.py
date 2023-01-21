from celery import shared_task
from django.db.models import Count, Q

from courses.models import Course
from enroll.models import EnrolledCourse

# """
# The prefix `a` for every task denotes `async`.
# """


# @shared_task
# def astudent_count(course_id):
#     """
#     Count number of students  based on the enrolled course.
#     """
#     s_count = EnrolledCourse.objects.filter(pk=course_id).aggregate(
#         student_count=Count("student")
#     )
#     return s_count["student_count"]


# @shared_task
# def adetailed_rating(course_id, rating):
#     """
#     Detailed rating for each course.
#     """
#     try:
#         rating_count = Course.objects.annotate(
#             r_count=Count(
#                 "course_reviews__rating", filter=Q(course_reviews__rating__exact=rating)
#             ),
#             total_count=Count("course_reviews__rating"),
#         ).get(pk=course_id)
#         return f"{(rating_count.r_count / rating_count.total_count) * 100:.2f}"
#     except ZeroDivisionError:
#         return 0
