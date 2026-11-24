from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.accounts.permissions import ContributorRequiredMixin
from apps.interactions.models import Comment

from .forms import PostForm
from .models import Post


def visible_posts(user):
    queryset = Post.objects.select_related("category", "author")
    if user.is_superuser:
        return queryset
    return queryset.filter(author=user)


class DashboardView(ContributorRequiredMixin, TemplateView):
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
        if self.request.user.is_admin_role:
            context["pending_posts"] = Post.objects.filter(
                status=Post.Status.DRAFT
            ).select_related("author", "category").order_by("-updated_at")
            context["pending_comments"] = Comment.objects.filter(
                is_approved=False
            ).select_related("user", "post").order_by("-created_at")
        return context


class MyPostListView(ContributorRequiredMixin, ListView):
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


class PostCreateView(ContributorRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "author/post_form.html"
    success_url = reverse_lazy("author:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.status = Post.Status.DRAFT
        messages.success(self.request, "Đã gửi bài viết. Bài viết đang chờ quản trị viên kiểm duyệt.")
        return super().form_valid(form)


class PostUpdateView(ContributorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "author/post_form.html"
    success_url = reverse_lazy("author:post_list")

    def get_queryset(self):
        return visible_posts(self.request.user)

    def form_valid(self, form):
        form.instance.status = Post.Status.DRAFT
        messages.success(self.request, "Đã cập nhật bài viết và gửi lại chờ kiểm duyệt.")
        return super().form_valid(form)


class PostDeleteView(ContributorRequiredMixin, DeleteView):
    model = Post
    template_name = "author/post_confirm_delete.html"
    success_url = reverse_lazy("author:post_list")

    def get_queryset(self):
        return visible_posts(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Đã xoá bài viết.")
        return super().form_valid(form)


def admin_only(view):
    return login_required(user_passes_test(lambda user: user.is_admin_role)(view))


@admin_only
@require_POST
def approve_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = Post.Status.PUBLISHED
    post.save(update_fields=["status", "published_at", "updated_at"])
    messages.success(request, f'Đã duyệt bài viết "{post.title}".')
    return redirect("author:dashboard")


@admin_only
@require_POST
def reject_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.status = Post.Status.DRAFT
    post.save(update_fields=["status", "updated_at"])
    messages.info(request, f'Đã từ chối bài viết "{post.title}".')
    return redirect("author:dashboard")


@admin_only
@require_POST
def approve_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.is_approved = True
    comment.save(update_fields=["is_approved"])
    messages.success(request, "Đã duyệt bình luận.")
    return redirect("author:dashboard")


@admin_only
@require_POST
def reject_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    messages.info(request, "Đã từ chối và xóa bình luận.")
    return redirect("author:dashboard")
