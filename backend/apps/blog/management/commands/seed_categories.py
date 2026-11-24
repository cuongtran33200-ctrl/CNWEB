from django.core.management.base import BaseCommand

from apps.blog.models import Category


CATEGORIES = {
    "Lập trình": "Kiến thức, hướng dẫn và kinh nghiệm lập trình.",
    "Công nghệ": "Tin tức, xu hướng và công cụ công nghệ.",
    "Kinh nghiệm": "Chia sẻ kinh nghiệm học tập và làm việc.",
}


class Command(BaseCommand):
    help = "Tạo các danh mục mặc định nếu database chưa có danh mục."

    def handle(self, *args, **options):
        created = 0
        for name, description in CATEGORIES.items():
            _, was_created = Category.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Đã tạo {created} danh mục mới."))
