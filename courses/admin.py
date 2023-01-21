from django.contrib import admin

from .models import (Audience, Category, Course, CourseAudience, CourseContent,
                     CourseHit, CourseReviewRating, CourseTag, CourseWeek,
                     HitDetail, Member, Tag, TeacherReviewRating,
                     WeeklyCourseContent)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "created"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}


class TagAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "created"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}


class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "owner",
        "title",
        "category",
        "created",
        "updated",
    ]
    list_filter = ["title", "owner", "category", "updated"]
    search_fields = ["title", "overview"]
    prepopulated_fields = {"slug": ("title",)}


class HitDetailAdmin(admin.ModelAdmin):
    list_display = ["ip", "device_type", "os_type", "ip", "created"]


class CourseReviewRatingAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "course",
        "title",
        "rating",
    ]


class CourseHitAdmin(admin.ModelAdmin):
    list_display = ["hit", "course"]


class CourseContentAdmin(admin.ModelAdmin):
    list_display = ["content_type", "title", "length", "created"]


class WeeklyCourseContentAdmin(admin.ModelAdmin):
    list_display = ["course_week", "content", "created"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(CourseTag)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseReviewRating, CourseReviewRatingAdmin)
admin.site.register(TeacherReviewRating)
admin.site.register(Audience)
admin.site.register(CourseAudience)
admin.site.register(HitDetail, HitDetailAdmin)
admin.site.register(CourseHit, CourseHitAdmin)
admin.site.register(Member)
admin.site.register(CourseWeek)
admin.site.register(CourseContent, CourseContentAdmin)
admin.site.register(WeeklyCourseContent, WeeklyCourseContentAdmin)
