from django.urls import path

from . import author_views

app_name = "author"

urlpatterns = [
    path("", author_views.DashboardView.as_view(), name="dashboard"),
    path("posts/", author_views.MyPostListView.as_view(), name="post_list"),
    path("posts/new/", author_views.PostCreateView.as_view(), name="post_create"),
    path(
        "posts/<int:pk>/edit/",
        author_views.PostUpdateView.as_view(),
        name="post_update",
    ),
    path(
        "posts/<int:pk>/delete/",
        author_views.PostDeleteView.as_view(),
        name="post_delete",
    ),
    path("moderation/posts/<int:pk>/approve/", author_views.approve_post, name="approve_post"),
    path("moderation/posts/<int:pk>/reject/", author_views.reject_post, name="reject_post"),
    path("moderation/comments/<int:pk>/approve/", author_views.approve_comment, name="approve_comment"),
    path("moderation/comments/<int:pk>/reject/", author_views.reject_comment, name="reject_comment"),
]
