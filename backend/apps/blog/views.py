from django.db.models import Count, F, Prefetch, Q, Sum
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from apps.interactions.forms import CommentForm
from apps.interactions.models import Comment, Reaction

from .models import Category, Post, Tag


def post_queryset():
    return (
        Post.objects.published()
        .select_related("author", "category")
        .prefetch_related("tags")
    )


class SidebarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(
            total=Count("posts", filter=Q(posts__status=Post.Status.PUBLISHED))
        ).order_by("name")
        context["popular_tags"] = (
            Tag.objects.annotate(
                total=Count("posts", filter=Q(posts__status=Post.Status.PUBLISHED))
            )
            .filter(total__gt=0)
            .order_by("-total", "name")[:12]
        )
        context["popular_posts"] = (
            Post.objects.published()
            .select_related("category", "author")
            .order_by("-views")[:5]
        )
        return context


class HomeView(SidebarMixin, ListView):
    template_name = "blog/home.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        return post_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured = list(post_queryset().filter(is_featured=True)[:4])
        context["featured_posts"] = featured
        context["hero_post"] = featured[0] if featured else None
        context["stats"] = {
            "posts": Post.objects.published().count(),
            "categories": Category.objects.count(),
            "views": Post.objects.published().aggregate(total=Sum("views"))[
                "total"
            ]
            or 0,
        }
        context["page_title"] = "Trang chủ"
        return context


class BasePostListView(SidebarMixin, ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6
    page_title = "Bài viết"
    page_description = "Tất cả bài viết đã xuất bản."

    def get_queryset(self):
        return post_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["page_description"] = self.page_description
        return context


class CategoryPostListView(BasePostListView):
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Danh mục: {self.category.name}"
        context["page_description"] = self.category.description
        return context


class TagPostListView(BasePostListView):
    tag = None

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return super().get_queryset().filter(tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Tag: {self.tag.name}"
        context["page_description"] = f"Các bài viết gắn với tag {self.tag.name}."
        return context


class SearchView(BasePostListView):
    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        queryset = super().get_queryset()
        if not self.query:
            return queryset.none()
        return queryset.filter(
            Q(title__icontains=self.query)
            | Q(excerpt__icontains=self.query)
            | Q(content__icontains=self.query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        context["page_title"] = "Tìm kiếm"
        context["page_description"] = (
            f'Kết quả cho "{self.query}"' if self.query else "Nhập từ khoá để tìm bài viết."
        )
        return context


class PostDetailView(SidebarMixin, DetailView):
    template_name = "blog/post_detail.html"

    def get_queryset(self):
        queryset = (
            Post.objects.select_related("author", "category")
            .prefetch_related("tags")
        )
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return queryset
            return queryset.filter(
                Q(status=Post.Status.PUBLISHED) | Q(author=user)
            )
        return queryset.filter(status=Post.Status.PUBLISHED)

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        session_key = f"viewed_post_{post.pk}"
        if post.status == Post.Status.PUBLISHED and not self.request.session.get(
            session_key
        ):
            Post.objects.filter(pk=post.pk).update(views=F("views") + 1)
            post.views += 1
            self.request.session[session_key] = True
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context["page_title"] = post.title
        context["page_description"] = post.excerpt
        context["related_posts"] = (
            post_queryset()
            .filter(category=post.category)
            .exclude(pk=post.pk)[:3]
        )

        approved_replies = Prefetch(
            "replies",
            queryset=Comment.objects.filter(is_approved=True).select_related("user"),
            to_attr="approved_replies",
        )
        context["comments"] = (
            Comment.objects.filter(
                post=post, parent__isnull=True, is_approved=True
            )
            .select_related("user")
            .prefetch_related(approved_replies)
        )
        context["comment_count"] = Comment.objects.filter(
            post=post, is_approved=True
        ).count()
        context["comment_form"] = CommentForm()
        context["like_count"] = Reaction.objects.filter(
            post=post, kind=Reaction.Kind.LIKE
        ).count()
        context["bookmark_count"] = Reaction.objects.filter(
            post=post, kind=Reaction.Kind.BOOKMARK
        ).count()
        if self.request.user.is_authenticated:
            context["user_reactions"] = set(
                Reaction.objects.filter(
                    user=self.request.user, post=post
                ).values_list("kind", flat=True)
            )
        else:
            context["user_reactions"] = set()
        return context