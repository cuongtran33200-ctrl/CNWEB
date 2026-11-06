from django.conf import settings
from django.db import models

from apps.blog.models import Post


class Comment(models.Model):
    post = models.ForeignKey(
        Post, verbose_name="Bài viết", related_name="comments", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Người bình luận",
        related_name="comments",
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name="Trả lời bình luận",
        related_name="replies",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    content = models.TextField("Nội dung", max_length=2000)
    is_approved = models.BooleanField("Đã duyệt", default=False)
    created_at = models.DateTimeField("Ngày gửi", auto_now_add=True)

    class Meta:
        verbose_name = "Bình luận"
        verbose_name_plural = "Bình luận"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "is_approved", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.post}"[:90]


class Reaction(models.Model):
    class Kind(models.TextChoices):
        LIKE = "like", "Thích"
        BOOKMARK = "bookmark", "Lưu"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Người dùng",
        related_name="reactions",
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post, verbose_name="Bài viết", related_name="reactions", on_delete=models.CASCADE
    )
    kind = models.CharField("Loại", max_length=10, choices=Kind.choices)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Tương tác"
        verbose_name_plural = "Tương tác"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post", "kind"], name="unique_user_post_reaction"
            )
        ]
        indexes = [models.Index(fields=["post", "kind"])]

    def __str__(self):
        return f"{self.user} {self.kind} {self.post}"[:90]