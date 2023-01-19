from django import template
from enroll.models import EnrolledCourse
from courses.models import Course
from django.db.models import Count, Q

# from courses.tasks import astudent_count, adetailed_rating

register = template.Library()


@register.filter(name="currency")
def currency(price):
    return f"${int(price):,}" if int(price) > 0 else "FREE"


@register.filter(name="is_in_cart")
def is_in_cart(course, cart):
    for id in cart.keys():  # sourcery skip
        if int(id) == course.id:
            return True
    return False


@register.filter(name="quantity_in_cart")
def quantity_in_cart(course, cart):
    return next((cart.get(id) for id in cart.keys() if int(id) == course.id), 0)


@register.filter(name="total_amount")
def total_amount(total):
    return f"KES {int(total):,}"


@register.filter("student_count")
def student_count(course_id):
    """
    Count number of students  based on the enrolled course.
    """
    s_count = EnrolledCourse.objects.filter(pk=course_id).aggregate(
        student_count=Count("student")
    )
    return s_count["student_count"]


@register.filter("already_enrolled")
def already_enrolled(course, user):
    """
    Check if the student is enrolled in the course.
    """
    return (
        user.is_authenticated and user.enrolled_courses.filter(course=course).exists()
    )


@register.filter(name="detailed_rating")
def detailed_rating(course_id, rating):
    """
    Detailed rating for each course.
    """
    try:
        rating_count = Course.objects.annotate(
            r_count=Count(
                "course_reviews__rating", filter=Q(course_reviews__rating__exact=rating)
            ),
            total_count=Count("course_reviews__rating"),
        ).get(pk=course_id)
        return f"{(rating_count.r_count / rating_count.total_count) * 100:.2f}"
    except ZeroDivisionError:
        return 0


@register.filter(name="silently_add_to_cart")
def silently_add_to_cart(course_id, session_dict):
    if "cart" in session_dict:
        session_dict["cart"].update({course_id: 1})
    session_dict["cart"] = {course_id: 1}
    session_dict.save()
