from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course
from enroll.models import Coupon, EnrolledCourse, Enrollment


def addToCart(request):
    course_id = request.GET.get("course_id")
    cart = request.session.get("cart")
    user = request.user
    course = get_object_or_404(Course, id=course_id)
    if user.is_authenticated and user.enrolled_courses.filter(course=course).exists():
        messages.info(request, "You are already enrolled for this course.")
        return redirect("my_courses")
    if not cart:
        cart = {course_id: 1}
    elif not cart.get(course_id):
        cart[course_id] = 1
    messages.success(request, f"{course.title} added to cart successfully.")
    request.session["cart"] = cart
    return redirect(course)


def getCartTotal(request):
    cart_courses = Course.get_courses_by_id(list(request.session.get("cart").keys()))
    cart_total = sum(course.price for course in cart_courses)
    return (cart_courses, cart_total)


def cart(request):
    context = {"page_title": "Cart"}
    if request.session.get("cart"):
        cart_courses, cart_total = getCartTotal(request)
        context["cart_courses"] = cart_courses
        context["cart_total"] = cart_total

        if course_id := request.GET.get("course_id"):
            request.session.get("cart").pop(course_id)
            request.session.save()
            messages.info(request, "Course removed from cart successfully.")
            return redirect("cart")
    return render(request, "cart.html", context)


@login_required
def applyCoupon(request):
    """
    TODO : implement after creating a Cart Model
    """
    pass
    # try:
    #     url = request.META.get("HTTP_REFERER")
    #     if request.method == "POST":
    #         coupon = Coupon.objects.get(
    #             code=request.POST.get("coupon_code"), user=request.user
    #         )
    #         if not coupon or coupon.is_used:
    #             messages.error(request, "Your coupon code is invalid.")
    #         else:
    #             _, cart_total = getCartTotal(request)
    #             if coupon.discount > cart_total:
    #                 coupon_bal = coupon.discount - cart_total
    #                 cart_total = 0
    #                 coupon.user = request.user
    #                 coupon.discount = coupon_bal
    #             else:
    #                 cart_total -= coupon.discount
    #                 coupon.user = request.user
    #                 coupon.is_used = True
    #             coupon.save()
    #             messages.info(request, "Your cart balance updated successfully.")
    #         return redirect(url)
    # except Coupon.DoesNotExist:
    #     messages.info(request, "The coupon code you entered is invalid.")
    #     return redirect(url)
    # except Exception as e:
    #     print(e)
    #     return redirect("cart")


@login_required
def checkout(request):
    user = request.user
    if request.session.get("cart"):
        cart_courses, cart_total = getCartTotal(request)

        for course in cart_courses:
            if user.enrolled_courses.filter(course=course).exists():
                request.session.get("cart").pop(str(course.pk))
                request.session.save()
                messages.info(
                    request,
                    f"{course.title } removed. You are enrolled for the course already!",
                )
                return redirect("checkout")
        if request.method == "POST":
            phone = request.POST.get("phone")  # Use for M-Pesa integration.
            enrollCourse(cart_courses, cart_total, user)
            request.session["cart"] = {}
            messages.success(request, "Enrollment successful. Thank you!")
            return redirect("my_courses")

        return render(
            request,
            "checkout.html",
            {
                "page_title": "Checkout",
                "cart_courses": cart_courses,
                "cart_total": cart_total,
            },
        )
    else:
        messages.info(request, "Please select course(s) to enroll first.")
        return redirect("courses")


def enrollCourse(cart_courses, total, user):
    enrollment = Enrollment(student=user, amount=total)
    enrollment.save()
    for course in cart_courses:
        EnrolledCourse.objects.create(
            enrollment=enrollment, student=user, course=course
        )


def wishlist(request):
    return render(request, "wishlist.html")
