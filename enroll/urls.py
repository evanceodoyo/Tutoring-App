from django.urls import path

from .views import addToCart, applyCoupon, cart, checkout, wishlist

urlpatterns = [
    path("add-to-cart/", addToCart, name="add_to_cart"),
    path("cart/", cart, name="cart"),
    path("apply-coupon/", applyCoupon, name="apply_coupon"),
    path("checkout/", checkout, name="checkout"),
    path("wishlist/", wishlist, name="wishlist"),
]
