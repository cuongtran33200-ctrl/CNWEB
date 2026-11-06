from django.contrib import admin
from django.db.models import Count

from .models import Category, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "post_count")
    list_filter = ("parent",)
    search_fields = ("name",)
    readonly_fields = ("slug", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(total_posts=Count("posts"))

    @admin.display(description="Số bài", ordering="total_posts")
    def post_count(self, obj):
        return obj.total_posts


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    readonly_fields = ("slug",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "status",
        "is_featured",
        "views",
        "published_at",
    )
    list_filter = ("status", "category", "is_featured", "author")
    search_fields = ("title", "excerpt", "content")
    filter_horizontal = ("tags",)
    readonly_fields = ("slug", "views", "created_at", "updated_at", "published_at")
    date_hierarchy = "published_at"
    list_per_page = 20
    list_editable = ("status", "is_featured")
    save_on_top = True
    actions = ("make_published", "make_draft", "make_featured", "remove_featured")
    fieldsets = (
        ("Nội dung", {"fields": ("title", "slug", "category", "tags", "excerpt")}),
        ("Bài viết", {"fields": ("author", "thumbnail", "content")}),
        ("Xuất bản", {"fields": ("status", "is_featured", "published_at")}),
        ("Thống kê", {"fields": ("views", "created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="Xuất bản bài đã chọn")
    def make_published(self, request, queryset):
        updated = queryset.update(status=Post.Status.PUBLISHED)
        self.message_user(request, f"Đã xuất bản {updated} bài viết.")

    @admin.action(description="Chuyển bài đã chọn về nháp")
    def make_draft(self, request, queryset):
        updated = queryset.update(status=Post.Status.DRAFT)
        self.message_user(request, f"Đã chuyển {updated} bài về nháp.")

    @admin.action(description="Đánh dấu nổi bật")
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"Đã đánh dấu {updated} bài nổi bật.")

    @admin.action(description="Bỏ đánh dấu nổi bật")
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"Đã bỏ nổi bật {updated} bài.")