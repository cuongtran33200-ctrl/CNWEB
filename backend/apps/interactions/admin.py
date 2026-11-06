from django.contrib import admin

from .models import Comment, Reaction


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "parent", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("content", "user__username", "post__title")
    list_per_page = 30
    list_editable = ("is_approved",)
    actions = ("approve_comments", "reject_comments")

    @admin.action(description="Duyệt bình luận đã chọn")
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"Đã duyệt {updated} bình luận.")

    @admin.action(description="Bỏ duyệt bình luận đã chọn")
    def reject_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"Đã bỏ duyệt {updated} bình luận.")


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "kind", "created_at")
    list_filter = ("kind", "created_at")
    search_fields = ("user__username", "post__title")