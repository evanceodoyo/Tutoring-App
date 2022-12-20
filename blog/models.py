from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField
from utils.utils import slug_generator
from django_resized import ResizedImageField


class Article(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        "courses.Category",
        on_delete=models.SET_NULL,
        related_name="articles",
        null=True,
    )
    slug = models.SlugField(max_length=255, unique=True)
    thumbnail = ResizedImageField(
        size=[600, 400], upload_to="blog/images/", default="blog/images/placeholder.png"
    )
    content = HTMLField()
    is_draft = models.BooleanField("Draft", default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_articles"
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        self.slug = slug_generator(self)
        super(Article, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title[:20]}... by {self.author}"

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"article_slug": self.slug})


class ArticleTag(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="article_tags"
    )
    tag = models.ForeignKey("courses.Tag", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "article_tags"

    def __str__(self):
        return self.tag.title


class Comment(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments"
    )
    website = models.CharField(max_length=100, blank=True, default="")
    body = models.TextField()
    is_active = models.BooleanField("Active", default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "article_comments"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.body} by {self.author}"


class ArticleHit(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.SET_NULL, related_name="article_hits", null=True
    )
    hit = models.ForeignKey("courses.HitDetail", on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "article_hits"

    def __str__(self):
        return f"{self.hit} for {self.article}"
