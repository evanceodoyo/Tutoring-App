from django.shortcuts import redirect
from courses.models import Course
from django.contrib import messages

def student_required(get_response):
    def middleware(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_student:
            messages.info(
                request,
                "Only students are allowed to use this use this functionality.",
            )
            return redirect("profile")
        return get_response(request, *args, **kwargs)
    return middleware

def only_enrolled_students_required(get_response):
    def middleware(request, *args, **kwargs):
        course = Course.objects.get(slug=kwargs["course_slug"])
        if course.student_id != request.user.id:
            messages.info(
                request,
                "Only students registered in the course are allowed to do reviews",
            )
            return redirect("my_courses")
        return get_response(request, *args, **kwargs)
    return middleware

def unauthenticated_user_required(get_response):
    def middleware(request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                return redirect(request.META.get('HTTP_REFERER'))
            return get_response(request, *args, **kwargs)
        except Exception:
            return redirect('home')
    return middleware
