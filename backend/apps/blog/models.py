
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify
from tinymce.models import HTMLField
from cloudinary.models import CloudinaryField

from apps.accounts.models import User


def build_slug(value, model, instance_pk=None, max_length=180):
    base = slugify(
        value.replace("đ", "d").replace("Đ", "D")
    )[:max_length]

    base = base or "bai-viet"
    slug = base
    counter = 2

    queryset = model.objects.filter(slug=slug)

    if instance_pk:
        queryset = queryset.exclude(pk=instance_pk)

    while queryset.exists():
        slug = f"{base}-{counter}"
        counter += 1

        queryset = model.objects.filter(slug=slug)

        if instance_pk:
            queryset = queryset.exclude(pk=instance_pk)

    return slug


class Category(models.Model):
    name = models.CharField(
        "Tên danh mục",
        max_length=120,
        unique=True
    )

    slug = models.SlugField(
        "Slug",
        max_length=140,
        unique=True,
        blank=True
    )

    description = models.TextField(
        "Mô tả",
        blank=True
    )

    parent = models.ForeignKey(
        "self",
        verbose_name="Danh mục cha",
        related_name="children",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = build_slug(
                self.name,
                Category,
                self.pk
            )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category", args=[self.slug])


class Tag(models.Model):
    name = models.CharField(
        "Tên tag",
        max_length=60,
        unique=True
    )

    slug = models.SlugField(
        "Slug",
        max_length=80,
        unique=True,
        blank=True
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tag"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = build_slug(
                self.name,
                Tag,
                self.pk
            )

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:tag", args=[self.slug])


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status=Post.Status.PUBLISHED
        )


class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Nháp"
        PUBLISHED = "published", "Đã xuất bản"

    objects = PostQuerySet.as_manager()

    author = models.ForeignKey(
        User,
        verbose_name="Tác giả",
        related_name="posts",
        on_delete=models.CASCADE,
    )

    category = models.ForeignKey(
        Category,
        verbose_name="Danh mục",
        related_name="posts",
        on_delete=models.PROTECT,
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name="Tag",
        related_name="posts",
        blank=True
    )

    title = models.CharField(
        "Tiêu đề",
        max_length=220
    )

    slug = models.SlugField(
        "Slug",
        max_length=240,
        unique=True,
        blank=True
    )

    # Ảnh bìa lưu trực tiếp trên Cloudinary
    thumbnail = CloudinaryField(
        "Ảnh bìa",
        folder="sbcb-blog/posts",
        blank=True,
        null=True
    )

    excerpt = models.CharField(
        "Tóm tắt",
        max_length=320,
        blank=True
    )

    content = HTMLField("Nội dung")

    status = models.CharField(
        "Trạng thái",
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    is_featured = models.BooleanField(
        "Nổi bật",
        default=False
    )

    views = models.PositiveIntegerField(
        "Lượt xem",
        default=0,
        editable=False
    )

    created_at = models.DateTimeField(
        "Ngày tạo",
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        "Cập nhật",
        auto_now=True
    )

    published_at = models.DateTimeField(
        "Ngày xuất bản",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Bài viết"
        verbose_name_plural = "Bài viết"
        ordering = ["-published_at", "-created_at"]

        indexes = [
            models.Index(
                fields=["status", "published_at"]
            ),
            models.Index(
                fields=["created_at"]
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = build_slug(
                self.title,
                Post,
                self.pk,
                max_length=220
            )

        if not self.excerpt:
            self.excerpt = " ".join(
                strip_tags(self.content).split()
            )[:300]

        if (
            self.status == self.Status.PUBLISHED
            and not self.published_at
        ):
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            args=[self.slug]
        )
