from django.contrib import admin

from .models import Coupon, EnrolledCourse, Enrollment, Wishlist


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "enrollment_id", "date_enrolled"]
    search_fields = ["student__name", "enrollment_id"]


class EnrolledCourseAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "course"]
    search_fields = ["enrollment__enrollemnt_id", "course__title"]


admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(EnrolledCourse, EnrolledCourseAdmin)
admin.site.register(Wishlist)
admin.site.register(Coupon)
