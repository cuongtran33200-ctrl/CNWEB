from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path("post/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path(
        "post/<slug:slug>/react/<str:kind>/",
        views.toggle_reaction,
        name="toggle_reaction",
    ),
    path("bookmarks/", views.BookmarkListView.as_view(), name="bookmarks"),
]