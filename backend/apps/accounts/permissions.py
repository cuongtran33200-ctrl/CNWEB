from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_author

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Bạn không có quyền thực hiện thao tác này.")
        return super().handle_no_permission()


class ContributorRequiredMixin(LoginRequiredMixin):
    """Allow every authenticated user to submit content for moderation."""


class AdminRoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin_role

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "Bạn không có quyền thực hiện thao tác này.")
        return super().handle_no_permission()
