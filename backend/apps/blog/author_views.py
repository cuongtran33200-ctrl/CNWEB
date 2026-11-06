from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.accounts.permissions import AuthorRequiredMixin
from apps.interactions.models import Comment

from .forms import PostForm
from .models import Post


def visible_posts(user):
    queryset = Post.objects.select_related("category", "author")
    if user.is_superuser:
        return queryset
    return queryset.filter(author=user)


class DashboardView(AuthorRequiredMixin, TemplateView):
    template_name = "author/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = visible_posts(self.request.user)
        context["stats"] = {
            "total": posts.count(),
            "published": posts.filter(status=Post.Status.PUBLISHED).count(),
            "drafts": posts.filter(status=Post.Status.DRAFT).count(),
            "views": posts.aggregate(total=Sum("views"))["total"] or 0,
            "comments": Comment.objects.filter(
                post__in=posts, is_approved=True
            ).count(),
        }
        context["recent_posts"] = posts.order_by("-updated_at")[:5]
        return context


class MyPostListView(AuthorRequiredMixin, ListView):
    template_name = "author/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        queryset = visible_posts(self.request.user).order_by("-updated_at")
        self.status_filter = self.request.GET.get("status", "")
        if self.status_filter in Post.Status.values:
            queryset = queryset.filter(status=self.status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.status_filter
        context["statuses"] = Post.Status.choices
        return context


class PostCreateView(AuthorRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "author/post_form.html"
    success_url = reverse_lazy("author:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Đã tạo bài viết mới.")
        return super().form_valid(form)


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "author/post_form.html"
    success_url = reverse_lazy("author:post_list")

    def get_queryset(self):
        return visible_posts(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Đã cập nhật bài viết.")
        return super().form_valid(form)


class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model = Post
    template_name = "author/post_confirm_delete.html"
    success_url = reverse_lazy("author:post_list")

    def get_queryset(self):
        return visible_posts(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Đã xoá bài viết.")
        return super().form_valid(form)