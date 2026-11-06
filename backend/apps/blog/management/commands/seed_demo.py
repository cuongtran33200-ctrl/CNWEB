from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.blog.models import Category, Post, Tag
from apps.interactions.models import Comment, Reaction

User = get_user_model()

CATEGORIES = {
    "Lập trình": "Kiến thức, hướng dẫn và kinh nghiệm lập trình.",
    "Công nghệ": "Tin tức, xu hướng và công cụ công nghệ.",
    "Kinh nghiệm": "Chia sẻ kinh nghiệm học tập và làm việc.",
}

TAGS = ["Django", "Python", "ORM", "Web", "AI", "Sự nghiệp"]

POSTS = [
    {
        "title": "Django là gì? Vì sao nên học Django năm 2026",
        "category": "Lập trình",
        "tags": ["Django", "Python", "Web"],
        "featured": True,
        "days": 2,
        "views": 1250,
        "content": """
            <p>Django là framework web mã nguồn mở viết bằng Python, ra đời từ năm 2005
            và được duy trì bởi Django Software Foundation. Framework này nổi tiếng nhờ
            triết lý "batteries included": mọi thứ cần cho một website đều có sẵn.</p>
            <h2>Ưu điểm nổi bật</h2>
            <ul>
                <li>ORM mạnh mẽ, thao tác cơ sở dữ liệu bằng Python.</li>
                <li>Admin site tự động, tiết kiệm thời gian quản trị.</li>
                <li>Bảo mật tốt: chống SQL injection, CSRF, XSS mặc định.</li>
                <li>Cộng đồng lớn, tài liệu chi tiết và nhiều package hỗ trợ.</li>
            </ul>
            <p>Với sinh viên công nghệ thông tin, Django là lựa chọn phù hợp để xây dựng
            đồ án web hoàn chỉnh trong thời gian ngắn.</p>
        """,
    },
    {
        "title": "Hướng dẫn tạo project Django đầu tiên",
        "category": "Lập trình",
        "tags": ["Django", "Python", "Web"],
        "featured": True,
        "days": 5,
        "views": 980,
        "content": """
            <p>Bài viết hướng dẫn từng bước khởi tạo một project Django mới, từ việc
            tạo môi trường ảo đến chạy server phát triển.</p>
            <h2>Các bước cơ bản</h2>
            <ol>
                <li>Tạo môi trường ảo và cài đặt Django.</li>
                <li>Chạy lệnh khởi tạo project và app.</li>
                <li>Cấu hình database, template và static files.</li>
                <li>Chạy migrate và tạo tài khoản quản trị.</li>
            </ol>
            <p>Sau khi hoàn tất, bạn đã có bộ khung vững chắc để phát triển tính năng.</p>
        """,
    },
    {
        "title": "Tối ưu truy vấn ORM với select_related và prefetch_related",
        "category": "Lập trình",
        "tags": ["Django", "ORM", "Python"],
        "featured": False,
        "days": 8,
        "views": 760,
        "content": """
            <p>Vấn đề N+1 query là lỗi hiệu năng phổ biến khi làm việc với ORM. Mỗi lần
            truy cập quan hệ ngoại lai, Django có thể phát sinh thêm một truy vấn.</p>
            <h2>Khi nào dùng gì?</h2>
            <ul>
                <li><strong>select_related</strong> cho quan hệ một-nhiều hoặc một-một.</li>
                <li><strong>prefetch_related</strong> cho quan hệ nhiều-nhiều hoặc đảo ngược.</li>
            </ul>
            <p>Chỉ cần thêm hai phương thức này vào queryset, số truy vấn có thể giảm từ
            hàng trăm xuống còn vài truy vấn.</p>
        """,
    },
    {
        "title": "5 xu hướng công nghệ đáng chú ý trong năm 2026",
        "category": "Công nghệ",
        "tags": ["AI", "Web"],
        "featured": False,
        "days": 12,
        "views": 640,
        "content": """
            <p>Năm 2026 chứng kiến sự bùng nổ của các công cụ hỗ trợ bởi trí tuệ nhân tạo
            trong mọi lĩnh vực, từ lập trình đến thiết kế và vận hành hệ thống.</p>
            <h2>Những xu hướng chính</h2>
            <ul>
                <li>Trợ lý lập trình AI tích hợp sâu vào IDE.</li>
                <li>Điện toán biên giúp giảm độ trễ ứng dụng.</li>
                <li>Kiến trúc serverless ngày càng trưởng thành.</li>
                <li>Bảo mật lấy dữ liệu làm trung tâm.</li>
                <li>WebAssembly mở rộng khả năng của trình duyệt.</li>
            </ul>
        """,
    },
    {
        "title": "Kinh nghiệm phỏng vấn Backend fresher",
        "category": "Kinh nghiệm",
        "tags": ["Sự nghiệp", "Web"],
        "featured": False,
        "days": 15,
        "views": 520,
        "content": """
            <p>Buổi phỏng vấn fresher backend thường tập trung vào kiến thức nền tảng
            hơn là các bài toán quá phức tạp.</p>
            <h2>Chuẩn bị gì?</h2>
            <ul>
                <li>Nắm chắc cấu trúc dữ liệu và giải thuật cơ bản.</li>
                <li>Hiểu HTTP, REST, mã trạng thái và cách thiết kế API.</li>
                <li>Biết viết truy vấn SQL và đọc explain plan.</li>
                <li>Chuẩn bị một project cá nhân để trình bày.</li>
            </ul>
            <p>Hãy luyện nói rõ ràng về những gì bạn đã làm và bài học rút ra.</p>
        """,
    },
    {
        "title": "TinyMCE hay CKEditor cho trang blog?",
        "category": "Công nghệ",
        "tags": ["Web", "Django"],
        "featured": False,
        "days": 20,
        "views": 410,
        "content": """
            <p>Cả hai đều là trình soạn thảo WYSIWYG phổ biến, nhưng có khác biệt về
            giấy phép và mức độ hỗ trợ.</p>
            <h2>So sánh nhanh</h2>
            <ul>
                <li>TinyMCE có phiên bản cộng đồng, tài liệu tốt, dễ tích hợp.</li>
                <li>CKEditor 4 đã ngừng hỗ trợ và có cảnh báo bảo mật.</li>
                <li>CKEditor 5 mạnh nhưng điều khoản giấy phép phức tạp hơn.</li>
            </ul>
            <p>Với đồ án sinh viên, TinyMCE là lựa chọn cân bằng giữa tính năng và
            chi phí.</p>
        """,
    },
    {
        "title": "Lộ trình học Django trong 8 tuần",
        "category": "Lập trình",
        "tags": ["Django", "Python", "Sự nghiệp"],
        "featured": False,
        "days": 0,
        "views": 0,
        "status": "draft",
        "content": """
            <p>Bài viết nháp phác thảo lộ trình học Django từ cơ bản đến khi hoàn thiện
            một dự án web hoàn chỉnh.</p>
            <p>Nội dung chi tiết sẽ được cập nhật trước khi xuất bản.</p>
        """,
    },
]


class Command(BaseCommand):
    help = "Tạo dữ liệu mẫu cho blog: danh mục, tag, tác giả và bài viết."

    def handle(self, *args, **options):
        author, created = User.objects.get_or_create(
            username="tacgia",
            defaults={
                "email": "tacgia@cuoikycnweb.local",
                "first_name": "Việt",
                "last_name": "Cường",
                "role": User.Role.AUTHOR,
                "bio": "Tác giả nội dung cho SBCB Blog.",
            },
        )
        if created:
            author.set_password("Tacgia@123")
            author.save()

        reader, created = User.objects.get_or_create(
            username="docgia",
            defaults={
                "email": "docgia@cuoikycnweb.local",
                "first_name": "Minh",
                "last_name": "Anh",
                "role": User.Role.READER,
                "bio": "Độc giả quan tâm đến lập trình web.",
            },
        )
        if created:
            reader.set_password("Docgia@123")
            reader.save()

        categories = {}
        for name, description in CATEGORIES.items():
            category, _ = Category.objects.get_or_create(
                name=name, defaults={"description": description}
            )
            categories[name] = category

        tags = {}
        for name in TAGS:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags[name] = tag

        created_count = 0
        for data in POSTS:
            if Post.objects.filter(title=data["title"]).exists():
                continue
            status = data.get("status", Post.Status.PUBLISHED)
            published_at = (
                timezone.now() - timedelta(days=data["days"])
                if status == Post.Status.PUBLISHED
                else None
            )
            post = Post.objects.create(
                author=author,
                category=categories[data["category"]],
                title=data["title"],
                content=data["content"],
                status=status,
                is_featured=data["featured"],
                views=data["views"],
                published_at=published_at,
            )
            post.tags.set([tags[name] for name in data["tags"]])
            created_count += 1

        admin_user = User.objects.filter(is_superuser=True).first() or author
        comment_count = 0

        post1 = Post.objects.filter(
            title="Django là gì? Vì sao nên học Django năm 2026"
        ).first()
        if post1:
            first_comment, created = Comment.objects.get_or_create(
                post=post1,
                user=author,
                content="Bài viết rất hữu ích cho người mới bắt đầu. Cảm ơn tác giả!",
                defaults={"is_approved": True},
            )
            comment_count += int(created)
            _, created = Comment.objects.get_or_create(
                post=post1,
                user=admin_user,
                content="Mình đồng ý, phần ORM nên có thêm ví dụ thực tế.",
                defaults={"is_approved": True, "parent": first_comment},
            )
            comment_count += int(created)

        post2 = Post.objects.filter(
            title="Hướng dẫn tạo project Django đầu tiên"
        ).first()
        if post2:
            _, created = Comment.objects.get_or_create(
                post=post2,
                user=admin_user,
                content="Hướng dẫn chi tiết, mình đã làm theo và chạy được.",
                defaults={"is_approved": True},
            )
            comment_count += int(created)
            _, created = Comment.objects.get_or_create(
                post=post2,
                user=reader,
                content="Cảm ơn tác giả, bài viết rất dễ hiểu với người mới.",
                defaults={"is_approved": True},
            )
            comment_count += int(created)
            _, created = Comment.objects.get_or_create(
                post=post2,
                user=author,
                content="Bình luận này đang chờ quản trị viên duyệt.",
                defaults={"is_approved": False},
            )
            comment_count += int(created)

        post3 = Post.objects.filter(
            title="Tối ưu truy vấn ORM với select_related và prefetch_related"
        ).first()
        reaction_count = 0
        reaction_seed = [
            (reader, post1, Reaction.Kind.LIKE),
            (author, post1, Reaction.Kind.LIKE),
            (reader, post2, Reaction.Kind.LIKE),
            (admin_user, post2, Reaction.Kind.BOOKMARK),
            (reader, post3, Reaction.Kind.BOOKMARK),
        ]
        for user_obj, post_obj, kind in reaction_seed:
            if post_obj and user_obj:
                _, created = Reaction.objects.get_or_create(
                    user=user_obj, post=post_obj, kind=kind
                )
                reaction_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Đã tạo {created_count} bài viết, "
                f"{len(categories)} danh mục, {len(tags)} tag, "
                f"{comment_count} bình luận và {reaction_count} tương tác."
            )
        )