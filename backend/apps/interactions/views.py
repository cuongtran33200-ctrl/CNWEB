from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from apps.blog.models import Post

from .forms import CommentForm
from .models import Comment, Reaction


def post_url(post, anchor=""):
    url = reverse("blog:post_detail", args=[post.slug])
    return f"{url}{anchor}"


@login_required
@require_POST
def add_comment(request, slug):
    post = get_object_or_404(Post.objects.published(), slug=slug)
    form = CommentForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Bình luận không hợp lệ, vui lòng thử lại.")
        return redirect(post_url(post, "#comments"))

    comment = form.save(commit=False)
    comment.post = post
    comment.user = request.user

    parent_id = request.POST.get("parent")
    if parent_id:
        parent = Comment.objects.filter(pk=parent_id, post=post).first()
        if parent:
            comment.parent = parent

    comment.is_approved = request.user.is_staff or request.user == post.author
    comment.save()

    if comment.is_approved:
        messages.success(request, "Đã gửi bình luận.")
    else:
        messages.info(request, "Bình luận đã được gửi và đang chờ duyệt.")
    return redirect(post_url(post, "#comments"))


@login_required
@require_POST
def toggle_reaction(request, slug, kind):
    if kind not in Reaction.Kind.values:
        raise Http404("Loại tương tác không hợp lệ.")
    post = get_object_or_404(Post.objects.published(), slug=slug)
    reaction, created = Reaction.objects.get_or_create(
        user=request.user, post=post, kind=kind
    )
    if not created:
        reaction.delete()
    return redirect(post_url(post, "#reactions"))


class BookmarkListView(LoginRequiredMixin, ListView):
    template_name = "interactions/bookmarks.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        return (
            Post.objects.published()
            .filter(
                reactions__user=self.request.user,
                reactions__kind=Reaction.Kind.BOOKMARK,
            )
            .select_related("author", "category")
            .prefetch_related("tags")
        )