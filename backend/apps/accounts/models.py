from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    class Role(models.TextChoices):
        READER = "reader", "Độc giả"
        AUTHOR = "author", "Tác giả"
        ADMIN = "admin", "Quản trị"

    email = models.EmailField("Email", unique=True)
    avatar = CloudinaryField("Ảnh đại diện", blank=True, null=True)
    bio = models.TextField("Giới thiệu", max_length=500, blank=True)
    role = models.CharField(
        "Vai trò", max_length=10, choices=Role.choices, default=Role.READER
    )
    created_at = models.DateTimeField("Ngày tham gia", auto_now_add=True)

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_author(self):
        return self.role in {self.Role.AUTHOR, self.Role.ADMIN} or self.is_superuser

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class Friendship(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Đang chờ"
        ACCEPTED = "accepted", "Đã kết bạn"
        REJECTED = "rejected", "Đã từ chối"

    requester = models.ForeignKey(
        User, related_name="sent_friend_requests", on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        User, related_name="received_friend_requests", on_delete=models.CASCADE
    )
    status = models.CharField(
        "Trạng thái", max_length=10, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField("Ngày gửi", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("requester", "recipient"), name="unique_friend_request"
            )
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.requester} -> {self.recipient} ({self.status})"
