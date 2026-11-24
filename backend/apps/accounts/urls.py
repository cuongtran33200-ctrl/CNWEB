from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    CustomLoginView,
    CustomPasswordChangeView,
    ProfileView,
    PublicProfileView,
    FriendRequestView,
    FriendResponseView,
    RegisterView,
)
from django.contrib.auth.views import LogoutView

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("users/<str:username>/", PublicProfileView.as_view(), name="public_profile"),
    path("users/<str:username>/friend/", FriendRequestView.as_view(), name="friend_request"),
    path("friend-requests/<int:pk>/<str:action>/", FriendResponseView.as_view(), name="friend_response"),
    path(
        "password-change/",
        CustomPasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
            success_url="/accounts/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/password-reset/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
