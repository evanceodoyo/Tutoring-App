from django.urls import path

from .views import articleDetail, articles, articleSearch, postComment

urlpatterns = [
    path("", articles, name="blog"),
    path("article/<slug:article_slug>/", articleDetail, name="article_detail"),
    path("article/<slug:article_slug>/comments/", postComment, name="post_comment"),
    path("search/", articleSearch, name="article_search"),
]
