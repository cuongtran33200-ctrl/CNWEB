from datetime import date

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.shortcuts import render

from apps.interactions.models import Comment

from .models import Category, Post

User = get_user_model()


@staff_member_required
def stats_dashboard(request):
    posts = Post.objects.all()
    published = posts.filter(status=Post.Status.PUBLISHED)

    today = date.today()
    month_labels = []
    month_counts = []
    for offset in range(5, -1, -1):
        month = today.month - offset
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        month_labels.append(f"{month:02d}/{year}")
        month_counts.append(
            published.filter(
                published_at__year=year, published_at__month=month
            ).count()
        )

    categories = list(
        Category.objects.annotate(total=Count("posts")).order_by("-total", "name")
    )

    context = {
        "title": "Thống kê hệ thống",
        "total_posts": posts.count(),
        "published_posts": published.count(),
        "draft_posts": posts.filter(status=Post.Status.DRAFT).count(),
        "total_views": posts.aggregate(total=Sum("views"))["total"] or 0,
        "total_users": User.objects.count(),
        "total_comments": Comment.objects.count(),
        "pending_comments": Comment.objects.filter(is_approved=False).count(),
        "month_labels": month_labels,
        "month_counts": month_counts,
        "category_labels": [category.name for category in categories],
        "category_counts": [category.total for category in categories],
        "top_posts": published.select_related("category", "author").order_by(
            "-views"
        )[:5],
        "pending_comment_list": Comment.objects.filter(is_approved=False)
        .select_related("user", "post")[:5],
    }
    return render(request, "admin/stats_dashboard.html", context)