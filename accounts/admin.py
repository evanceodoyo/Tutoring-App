from django.contrib import admin

from .models import Designation, NewsLetterSubscriber, User


class UserAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "is_student", "date_joined", "last_login"]
    search_fields = ["name", "email"]


class NewsLetterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "date_subscribed"]
    search_fields = ["email"]


admin.site.register(User, UserAdmin)
admin.site.register(Designation)
admin.site.register(NewsLetterSubscriber, NewsLetterSubscriberAdmin)
