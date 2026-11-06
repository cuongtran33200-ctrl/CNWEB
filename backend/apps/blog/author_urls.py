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
]