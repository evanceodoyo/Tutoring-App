from django.contrib import admin

from .models import Article, ArticleHit, ArticleTag, Comment


class ArticleAdmin(admin.ModelAdmin):
    list_display = ["author", "title", "slug", "is_draft", "created", "updated"]
    search_fields = ["author", "title"]
    prepopulated_fields = {"slug": ("title",)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "body", "created", "is_active"]
    search_fields = ["author", "body"]


class ArticleHitAdmin(admin.ModelAdmin):
    list_display = ["hit", "article", "created"]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ArticleTag)
admin.site.register(ArticleHit, ArticleHitAdmin)
