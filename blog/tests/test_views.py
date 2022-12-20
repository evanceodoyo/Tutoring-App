from django.test import TestCase
from django.contrib.auth import get_user_model
from blog.models import Article, Comment
from django.urls import reverse
from courses.models import Category, Tag

User = get_user_model()


class ArticleListView(TestCase):
    def setUp(self):
        self.url = reverse("blog")
        # Create articles to test pagination.
        self.articles = [
            Article.objects.create(
                title=f"Sample article {article_id} title",
                content=f"The content of the article for article {article_id}.",
                thumbnail="blog/images/default.jpeg",
            )
            for article_id in range(1, 21)
        ]
        self.categories = [
            Category.objects.create(title=f"Category {category_id}")
            for category_id in range(1, 11)
        ]
        self.tags = [
            Tag.objects.create(title=f"Tag {tag_id}") for tag_id in range(1, 11)
        ]

    def test_pagination_is_six(self):
        response = self.client.get(self.url)
        articles = response.context["articles"]
        self.assertEqual(response.status_code, 200)
        # check that the page has the correct number of items.
        self.assertEqual(articles.paginator.per_page, 4)
        # check that the page has correct items.
        self.assertEqual(list(articles)[::-1], self.articles[-4:])

    def test_pagination_with_GET_page(self):
        response = self.client.get(self.url, {"page": 2})
        articles = response.context["articles"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(articles.paginator.per_page, 4)
        self.assertEqual(list(articles)[::-1], self.articles[-8:-4])

    def test_all_articles_in_list_not_draft(self):
        for article in self.articles:
            self.assertIs(article.is_draft, False)

        response = self.client.get(self.url)
        articles = response.context["articles"]
        for article in list(articles):
            self.assertIs(article.is_draft, False)

    def test_list_only_categories_with_at_least_one_article(self):
        categories_with_articles = []
        for article, category in zip(self.articles[:5], self.categories[:5]):
            article.category = category
            article.save()
            categories_with_articles.append(category)
        response = self.client.get(reverse("blog"))
        categories = response.context["categories"]
        # Check that the list of categories
        # contains only categories with articles.
        self.assertEqual(list(categories), categories_with_articles)
        for category in categories_with_articles:
            self.assertTrue(category.articles.all())
        for category in self.categories[5:]:
            self.assertFalse(category.articles.all())

    def test_only_eight_tags_are_shown(self):
        response = self.client.get(self.url)
        tags = response.context["tags"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tags.count(), 8)


class ArticleDetailViewTests(TestCase):
    def setUp(self):
        self.article_1 = Article.objects.create(
            title="Article 1 title",
            content="The content of aricle 1.",
            thumbnail="blog/images/default.jpeg",
        )
        self.article_2 = Article.objects.create(
            title="Article 2 title",
            content="The content of aricle 2.",
            thumbnail="blog/images/default.jpeg",
        )
        self.testuser = User.objects.create_user(
            name="testuser",
            email="testuser@mail.com",
            username="testuser",
            password="secret",
        )

        self.url = reverse(
            "article_detail", kwargs={"article_slug": self.article_1.slug}
        )

    def test_article_detail_GET(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_title"], self.article_1.title)
        self.assertEqual(response.context["article"], self.article_1)
        self.assertTemplateUsed(response, "article-details.html")

    def test_article_detail_with_hardcoded_url(self):
        response = self.client.get(
            reverse("article_detail", kwargs={"article_slug": "article-1-title"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["article"], self.article_1)
        self.assertTemplateUsed(response, "article-details.html")

    def test_article_detail_with_invalid_slug_returns_404(self):
        response = self.client.get(
            reverse(
                "article_detail",
                kwargs={"article_slug": "wrong-or-unavailable-article-slug"},
            )
        )
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

    def test_article_not_draft(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIs(self.article_1.is_draft, False)
        self.assertEqual(response.context["article"].is_draft, False)

    def test_article_detail_view_with_draft_article(self):
        # Create a draft article
        Article.objects.create(
            title="Draft Article",
            content="This is a draft article",
            author=self.testuser,
            is_draft=True,
        )

        # Send a GET request to the view with the slug of draft article
        response = self.client.get(
            reverse("article_detail", kwargs={"article_slug": "draft-article"})
        )

        # Check that the response is 404 (Not Found)
        self.assertEqual(response.status_code, 404)

    def test_comment_belongs_to_article(self):
        comment = Comment.objects.create(
            author=self.testuser, article=self.article_1, body="A comment on article 1"
        )
        response = self.client.get(self.url)
        self.assertTrue(comment in self.article_1.comments.all())
        self.assertEqual(response.context["comments"].first(), comment)
        self.assertEqual(response.context["comments"].first().is_active, True)

    def test_post_comment_POST(self):
        self.client.login(email="testuser@mail.com", password="secret")
        response = self.client.post(
            reverse("post_comment", kwargs={"article_slug": self.article_1.slug}),
            {"body": "This is a test comment", "website": "http://test.com"},
        )

        self.assertEqual(response.status_code, 302)

        # Check that the comment was actually added to the database
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.author, self.testuser)
        self.assertEqual(comment.article, self.article_1)
        self.assertEqual(comment.body, "This is a test comment")
        self.assertEqual(comment.website, "http://test.com")

    def test_post_comment_POST_no_data(self):
        response = self.client.post(
            reverse("post_comment", kwargs={"article_slug": self.article_1.slug})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.article_1.comments.count(), 0)
