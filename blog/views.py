from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, InvalidPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Category, Tag
from courses.views import get_user_agent_details

from .models import Article, ArticleHit, Comment


def articles(request):
    try:
        articles = Article.objects.select_related("category").filter(is_draft=False)
        categories = Category.objects.annotate(num_articles=Count("articles")).filter(
            num_articles__gte=1
        )[:5]
        tags = Tag.objects.only("title")[:8]
        page = request.GET.get("page")
        paginator = Paginator(articles, 4)
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except (EmptyPage, InvalidPage):
            articles = paginator.page(paginator.num_pages)
        return render(
            request,
            "articles.html",
            {
                "page_title": "Blog",
                "articles": articles,
                "categories": categories,
                "tags": tags,
            },
        )
    except Exception as e:
        print(e)
        return redirect("blog")


def articleDetail(request, article_slug):
    try:
        article = Article.objects.select_related("author").get(
            slug=article_slug, is_draft=False
        )
        comments = Comment.objects.filter(article=article, is_active=True)
        recent_articles = Article.objects.filter(is_draft=False).exclude(pk=article.pk)[
            :4
        ]

        categories = Category.objects.annotate(num_articles=Count("articles")).filter(
            num_articles__gte=1
        )[:5]
        tags = Tag.objects.only("title", "slug")[:8]
        ArticleHit.objects.get_or_create(
            hit=get_user_agent_details(request), article=article
        )

        return render(
            request,
            "article-details.html",
            {
                "page_title": article.title,
                "tags": tags,
                "article": article,
                "recent_articles": recent_articles,
                "comments": comments,
                "categories": categories,
            },
        )
    except Article.DoesNotExist:
        raise Http404


@login_required
def postComment(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug, is_draft=False)
    if request.method == "POST":
        body = request.POST.get("body")
        website = request.POST.get("website")
        Comment.objects.create(
            author=request.user, article=article, body=body, website=website
        )
        messages.success(request, "Your reply has been submitted successfully.")
        return redirect(article)
    return redirect(article)


def articleSearch(request):
    try:
        if request.method == "GET":
            query = request.GET.get("search")
            if query == "":
                return redirect(request.META.get("HTTP_REFERER"))
            articles = (
                Article.objects.filter(is_draft=False)
                .filter(
                    Q(title__icontains=query)
                    | Q(content__icontains=query)
                    | Q(category__title__icontains=query)
                    | Q(slug__icontains=query)
                    | Q(author__name__icontains=query)
                )
                .distinct()
            )
            page = request.GET.get("page")
            paginator = Paginator(articles, 6)
            try:
                articles = paginator.page(page)
            except PageNotAnInteger:
                articles = paginator.page(1)
            except (EmptyPage, InvalidPage):
                articles = paginator.page(paginator.num_pages)
            return render(
                request,
                "article-search-results.html",
                {"page_title": "Blog Search Results", "articles": articles},
            )
    except Exception:
        return redirect("blog")
