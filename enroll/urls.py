from django.urls import path

from .views import addToCart, applyCoupon, cart, checkout, wishlist, directCourseEnroll

urlpatterns = [
    path("add-to-cart/", addToCart, name="add_to_cart"),
    path("cart/", cart, name="cart"),
    path("apply-coupon/", applyCoupon, name="apply_coupon"),
    path("checkout/", checkout, name="checkout"),
    path("<slug:course_slug>/", directCourseEnroll, name="direct_course_enroll"),
    path("wishlist/", wishlist, name="wishlist"),
]
