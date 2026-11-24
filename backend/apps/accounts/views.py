from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import Friendship, User


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, "Đăng ký thành công. Bạn có thể đăng nhập ngay bây giờ."
        )
        return response


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Xin chào, {self.request.user}!")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Cập nhật hồ sơ thành công.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["friend_requests"] = Friendship.objects.filter(
            recipient=self.request.user,
            status=Friendship.Status.PENDING,
        ).select_related("requester")
        return context


class PublicProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = "accounts/public_profile.html"
    http_method_names = ["get"]

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        profile_user = self.object
        current = self.request.user
        friendship = None
        if current != profile_user:
            friendship = Friendship.objects.filter(
                requester=current, recipient=profile_user
            ).first() or Friendship.objects.filter(
                requester=profile_user, recipient=current
            ).first()
        friends = User.objects.filter(
            sent_friend_requests__recipient=profile_user,
            sent_friend_requests__status=Friendship.Status.ACCEPTED,
        ) | User.objects.filter(
            received_friend_requests__requester=profile_user,
            received_friend_requests__status=Friendship.Status.ACCEPTED,
        )
        context.update({
            "profile_user": profile_user,
            "friendship": friendship,
            "is_own_profile": current == profile_user,
            "friends": friends.distinct(),
        })
        return context


class UserSearchView(LoginRequiredMixin, ListView):
    template_name = "accounts/user_search.html"
    context_object_name = "users"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if not query:
            return User.objects.none()
        return User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        ).order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class FriendRequestView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, username):
        recipient = get_object_or_404(User, username=username)
        if recipient == request.user:
            messages.error(request, "Bạn không thể kết bạn với chính mình.")
            return redirect("accounts:public_profile", username=username)
        friendship = Friendship.objects.filter(
            requester=request.user, recipient=recipient
        ).first()
        reverse_request = Friendship.objects.filter(
            requester=recipient, recipient=request.user
        ).first()
        if reverse_request and reverse_request.status == Friendship.Status.PENDING:
            reverse_request.status = Friendship.Status.ACCEPTED
            reverse_request.save(update_fields=["status", "updated_at"])
            messages.success(request, "Hai bạn đã trở thành bạn bè.")
        elif not friendship:
            Friendship.objects.create(requester=request.user, recipient=recipient)
            messages.success(request, "Đã gửi lời mời kết bạn.")
        elif friendship.status == Friendship.Status.REJECTED:
            friendship.status = Friendship.Status.PENDING
            friendship.save(update_fields=["status", "updated_at"])
            messages.success(request, "Đã gửi lại lời mời kết bạn.")
        return redirect("accounts:public_profile", username=username)


class FriendResponseView(LoginRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk, action):
        friendship = get_object_or_404(
            Friendship, pk=pk, recipient=request.user, status=Friendship.Status.PENDING
        )
        if action == "accept":
            friendship.status = Friendship.Status.ACCEPTED
            messages.success(request, "Đã chấp nhận lời mời kết bạn.")
        else:
            friendship.status = Friendship.Status.REJECTED
            messages.info(request, "Đã từ chối lời mời kết bạn.")
        friendship.save(update_fields=["status", "updated_at"])
        return redirect("accounts:profile")


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, "Đổi mật khẩu thành công.")
        return super().form_valid(form)
