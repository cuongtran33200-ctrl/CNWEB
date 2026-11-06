from django.urls import path

from .views import (
    BasePostListView,
    CategoryPostListView,
    PostDetailView,
    SearchView,
    TagPostListView,
)

app_name = "blog"

urlpatterns = [
    path("", BasePostListView.as_view(), name="post_list"),
    path("search/", SearchView.as_view(), name="search"),
    path("category/<slug:slug>/", CategoryPostListView.as_view(), name="category"),
    path("tag/<slug:slug>/", TagPostListView.as_view(), name="tag"),
    path("<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
]