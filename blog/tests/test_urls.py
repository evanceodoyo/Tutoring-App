from django.test import TestCase
from django.urls import reverse, resolve
from blog.views import articleDetail, postComment, articleSearch


class TestBlogUrls(TestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)

    def test_list_url_available_by_name(self):
        response = self.client.get(reverse("blog"))
        self.assertEqual(response.status_code, 200)

    def test_blog_homepage_template_name_correct(self):
        response = self.client.get(reverse("blog"))
        self.assertTemplateUsed(response, "articles.html")

    def test_article_detail_url(self):
        url = reverse("article_detail", kwargs={"article_slug": "some-article-slug"})
        self.assertEqual(url, "/blog/article/some-article-slug/")
        self.assertEqual(resolve(url).func, articleDetail)

    def test_post_comment_url(self):
        url = reverse("post_comment", kwargs={"article_slug": "some-article-slug"})
        self.assertEqual(url, "/blog/article/some-article-slug/comments/")
        self.assertEqual(resolve(url).func, postComment)

    def test_article_search_url(self):
        url = reverse("article_search")
        self.assertEqual(url, "/blog/search/")
        self.assertEqual(resolve(url).func, articleSearch)
