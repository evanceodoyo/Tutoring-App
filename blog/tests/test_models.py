from django.test import TestCase
from blog.models import Article, ArticleTag, Comment
from courses.models import Category, Tag
from django.contrib.auth import get_user_model

User = get_user_model()


class ArticleModelTests(TestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="Test article", content="The content of the article."
        )
        self.article_1 = Article.objects.create(
            title="Test article", content="The content of the second article."
        )

    def test_article_title(self):
        self.assertEqual(self.article.title, "Test article")

    def test_article_content(self):
        self.assertEqual(self.article.content, "The content of the article.")

    def test_article_assigned_correct_slug_on_creation(self):
        self.assertEqual(self.article.slug, "test-article")

    def test_two_articles_with_same_title_have_different_slug(self):
        self.assertNotEqual(self.article.slug, self.article_1.slug)

    def test_get_absolute_url(self):
        self.assertEqual(self.article.get_absolute_url(), "/blog/article/test-article/")

    def test_article_is_not_draft_by_default(self):
        self.assertIs(self.article.is_draft, False)

    def test_object_name_is_part_of_title_and_name_of_author(self):
        author = User.objects.create(
            email="example@mail.com", name="John Doe", username="john_doe"
        )
        self.article.author = author
        expected_obj_name = f"{self.article.title[:20]}... by {self.article.author}"
        self.assertEqual(str(self.article), expected_obj_name)

    def test_article_category_title(self):
        category = Category.objects.create(title="article category")
        self.article.category = category
        self.article.save()
        self.assertEqual(self.article.category.title, "article category")

    def test_article_can_only_belong_to_one_category(self):
        category = Category.objects.create(title="article category")
        self.article.category = category
        self.article.save()
        # Override the previous category/(article category update).
        category2 = Category.objects.create(title="article category 2")
        self.article.category = category2
        self.article.save()
        self.assertEqual(self.article.category.title, "article category 2")
        self.assertEqual(self.article.category, category2)


class CommentModelTests(TestCase):
    def setUp(self):
        self.comment_author = User.objects.create(
            email="testuser@mail.com", name="testuser", username="testuser"
        )
        self.article = Article.objects.create(
            title="Test article", content="The content of the article."
        )
        self.comment = Comment.objects.create(
            author=self.comment_author, article=self.article, body="A test comment"
        )

    def test_article_object_name_is_body_and_author_name(self):
        expected_obj_name = f"{self.comment.body} by {self.comment.author}"
        self.assertEqual(str(self.comment), expected_obj_name)

    def test_comment_author_email(self):
        self.assertEqual(self.comment.author.email, self.comment_author.email)
        self.assertEqual(self.comment.author.email, "testuser@mail.com")

    def test_comment_is_active_by_default(self):
        self.assertTrue(self.comment.is_active)

    def test_comment_is_active_label(self):
        field_label = self.comment._meta.get_field("is_active").verbose_name
        self.assertEqual(field_label, "Active")


class ArticleTagModelTestS(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(title="article tag")
        self.tag2 = Tag.objects.create(title="second article tag")
        self.article = Article.objects.create(
            title="Test article", content="The content of the article."
        )
        self.article_tag = ArticleTag.objects.create(article=self.article, tag=self.tag)
        self.article_tag2 = ArticleTag.objects.create(
            article=self.article, tag=self.tag2
        )

    def test_article_tag_title(self):
        self.assertEqual(self.article_tag.tag, self.tag)
        self.assertEqual(self.article_tag.tag.title, "article tag")

    def test_object_name_is_tag_title(self):
        self.assertEqual(str(self.article_tag), "article tag")
        self.assertEqual(str(self.article_tag), self.tag.title)

    def test_article_can_have_more_than_one_tag(self):
        artilce_tags = self.article.article_tags.all()
        self.assertEqual(len(artilce_tags), 2)
