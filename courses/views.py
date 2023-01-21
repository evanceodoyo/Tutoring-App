from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import (EmptyPage, InvalidPage, PageNotAnInteger,
                                   Paginator)
from django.db.models import Avg, Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from blog.models import Article
from enroll.models import EnrolledCourse
from events.models import Event, Sponsor

from .models import (Category, Course, CourseHit, CourseReviewRating,
                     HitDetail, Member, Tag, TeacherReviewRating)

User = get_user_model()


def home(request):
    """
    Render highly rated courses as `featured courses`.
    Count only teachers who have created at least one course.
    Count only students who have enrolled for courses.
    """
    courses = (
        Course.objects.annotate(avg_rating=Avg("course_reviews__rating"))
        .select_related("owner", "category")
        .filter(is_active=True)
        .order_by("avg_rating")[:4]
    )
    teacher_count = courses.aggregate(tc=Count("owner", distinct=True))
    student_count = EnrolledCourse.objects.aggregate(sc=Count("student", distinct=True))
    articles = Article.objects.select_related("category").filter(is_draft=False)[:3]
    return render(
        request,
        "index.html",
        {
            "courses": courses,
            "articles": articles,
            "teacher_count": teacher_count["tc"],
            "student_count": student_count["sc"],
        },
    )


def courseList(request):
    courses = Course.objects.select_related("owner", "category").filter(is_active=True)
    page = request.GET.get("page")
    paginator = Paginator(courses, 6)
    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except (EmptyPage, InvalidPage):
        courses = paginator.page(paginator.num_pages)

    return render(
        request,
        "courses.html",
        {"page_title": "Our Courses", "courses": courses, "paginator": paginator},
    )


def get_user_agent_details(request):
    if x_forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"):
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    try:
        return HitDetail.objects.get(ip=ip)
    except HitDetail.DoesNotExist:
        hit = HitDetail(
            ip=ip,
            device_type=request.user_agent,
            browser_type=request.user_agent.browser.family,
            browser_version=request.user_agent.browser.version_string,
            os_type=request.user_agent.os.family,
            os_version=request.user_agent.os.version_string,
        )
        hit.save()
        return hit


def courseDetail(request, course_slug):
    try:
        course = (
            Course.objects.annotate(avg_rating=Avg("course_reviews__rating"))
            .select_related("owner", "category")
            .get(slug=course_slug, is_active=True)
        )
        reviews = CourseReviewRating.objects.select_related("user").filter(
            course=course, is_active=True
        )
        course_members = (
            Member.objects.filter(course=course)
            .annotate(avg_rating=Avg("member__teacher_reviews__rating"))
            .select_related("member")
        )
        related_courses_ids = course.course_tags.values_list("tag_id", flat=True)
        related_courses = (
            Course.objects.filter(
                is_active=True, course_tags__tag_id__in=related_courses_ids
            )
            .annotate(avg_rating=Avg("course_reviews__rating"))
            .distinct()
            .exclude(pk=course.pk)
        )
        CourseHit.objects.get_or_create(
            hit=get_user_agent_details(request), course=course
        )

        return render(
            request,
            "course-details.html",
            {
                "page_title": course.title,
                "course": course,
                "reviews": reviews,
                "related_courses": related_courses,
                "course_members": course_members,
                "rating_range": reversed(range(1, 6)),
            },
        )
    except Course.DoesNotExist:
        raise Http404


@login_required
def myCourses(request):
    enrolled_courses = request.user.enrolled_courses.all()

    return render(request, "my-courses.html", {"enrolled_courses": enrolled_courses})


def team(request):
    """
    Get only teachers who own courses.
    """
    course_teachers = Course.objects.only("owner")
    testimonials = (
        TeacherReviewRating.objects.select_related("user", "teacher")
        .filter(is_active=True)
        .order_by("-rating")
    )
    sponsors = Sponsor.objects.only("logo")[:8]

    return render(
        request,
        "team.html",
        {
            "page_title": "Team",
            "course_teachers": course_teachers,
            "testimonials": testimonials,
            "sponsors": sponsors,
        },
    )


def teamDetail(request, username):
    try:
        teacher = User.objects.annotate(avg_rating=Avg("teacher_reviews__rating")).get(
            username=username
        )
        courses_taught = (
            Course.objects.annotate(avg_rating=Avg("course_reviews__rating"))
            .select_related("owner", "category")
            .filter(Q(owner=teacher) | Q(course_members__member_id__in=[teacher.id]))
        )
        core_courses = courses_taught.filter(owner=teacher)
        teacher_reviews = TeacherReviewRating.objects.select_related("user").filter(
            teacher=teacher, is_active=True
        )
        return render(
            request,
            "team-details.html",
            {
                "page_title": "Team Details",
                "teacher": teacher,
                "courses_taught": courses_taught,
                "core_courses": core_courses,
                "teacher_reviews": teacher_reviews,
            },
        )
    except User.DoesNotExist:
        raise Http404


@login_required
def courseReview(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    user = request.user
    if not user.enrolled_courses.filter(course=course).exists() or course.owner == user:
        messages.error(
            request,
            "Only students who are already enrolled in this course can make reviews.",
        )
        return redirect(course)

    if request.method == "POST":
        title = request.POST.get("title")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        try:
            # avoid multiple ratings by same user
            # update the existing review
            review = CourseReviewRating.objects.get(user=user, course=course)
            review.title = title
            review.rating = rating
            review.comment = comment
            review.save()
            messages.success(
                request, "Thank you! Your review has been updated successfully."
            )
            return redirect(course)

        except CourseReviewRating.DoesNotExist:
            CourseReviewRating.objects.create(
                user=user,
                course=course,
                title=title,
                rating=rating,
                comment=comment,
            )
            messages.success(
                request, "Thank you! Your review has been submitted successfully."
            )
            return redirect(course)

    return redirect(course)


@login_required
def teacherReview(request, username):
    teacher = get_object_or_404(User, username=username)
    user = request.user
    if (
        not user.enrolled_courses.filter(course__owner=teacher).exists()
        or teacher == user
    ):
        messages.error(
            request, "Only students enrolled in the teacher's courses can make reviews."
        )
        return redirect(teacher)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        try:
            review = TeacherReviewRating.objects.get(user=user, teacher=teacher)
            review.rating = rating
            review.comment = comment
            review.save()
            messages.success(
                request, "Thank you! Your review has been updated successfully."
            )
            return redirect(teacher)

        except TeacherReviewRating.DoesNotExist:
            review = TeacherReviewRating.objects.create(
                user=user,
                teacher=teacher,
                rating=rating,
                comment=comment,
            )
            messages.success(
                request, "Thank you! Your review has been submitted successfully."
            )
            return redirect(teacher)

    return redirect(teacher)


def about(request):
    try:
        courses = (
            Course.objects.annotate(avg_rating=Count("course_reviews__rating"))
            .select_related("owner", "category")
            .filter(is_active=True)
            .order_by("avg_rating")[:6]
        )
        testimonials = (
            CourseReviewRating.objects.select_related("user", "course")
            .filter(is_active=True)
            .order_by("-rating")[:8]
        )
        course_teachers = Course.objects.only("owner")[:4]
        sponsors = Sponsor.objects.all()[:8]
        return render(
            request,
            "about.html",
            {
                "page_title": "About",
                "courses": courses,
                "course_teachers": course_teachers,
                "testimonials": testimonials,
                "sponsors": sponsors,
            },
        )
    except Exception as e:
        return redirect("home")


def search(request):
    try:
        if request.method == "GET":
            query = request.GET.get("search")
            if query == "":
                messages.warning(request, "Enter a valid keyword.")
                return redirect(request.META.get("HTTP_REFERER"))
            results = (
                Course.objects.select_related("owner", "category")
                .filter(is_active=True)
                .filter(
                    Q(title__icontains=query)
                    | Q(overview__icontains=query)
                    | Q(category__title__icontains=query)
                    | Q(owner__name__icontains=query)
                )
                .distinct()
            )
        rc = results.count()
        page = request.GET.get("page")
        paginator = Paginator(results, 8)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except (EmptyPage, InvalidPage):
            results = paginator.page(paginator.num_pages)
        return render(
            request,
            "search.html",
            {
                "results": results,
                "rc": rc,
                "query": query,
            },
        )
    except Exception:
        return redirect("home")


def category(request, category_slug):
    try:
        category = Category.objects.prefetch_related(
            "events", "courses", "articles"
        ).get(slug=category_slug)
        return render(
            request,
            "category.html",
            {
                "page_title": category.title,
                "category": category,
            },
        )
    except Category.DoesNotExist:
        raise Http404


def tag(request, tag_slug):
    try:
        tag = Tag.objects.get(slug=tag_slug)
        courses = (
            Course.objects.select_related("owner")
            .filter(course_tags__tag_id__in=[tag.id])
            .distinct()
        )
        events = (
            Event.objects.select_related("organiser")
            .filter(event_tags__tag_id__in=[tag.id])
            .distinct()
        )
        articles = (
            Article.objects.select_related("author")
            .filter(article_tags__tag_id__in=[tag.id])
            .distinct()
        )
        # chain the querysets and paginate
        # results = list(
        #     sorted(
        #         chain(courses, events, articles),
        #         key=lambda objects: objects.created
        #     ))
        # paginator = Paginator(results, 1)
        return render(
            request,
            "tag.html",
            {
                "page_title": tag.title,
                "tag": tag,
                "courses": courses,
                "events": events,
                "articles": articles,
                # "paginator": paginator,
            },
        )
    except Tag.DoesNotExist:
        raise Http404
