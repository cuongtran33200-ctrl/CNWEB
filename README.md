# SBCB Blog — Đồ án cuối kỳ Công nghệ Web

Website blog/tin tức xây dựng bằng **Django 5.2 + MariaDB/MySQL**, giao diện **Django Templates + Bootstrap 5**.
Frontend và backend được tách thư mục rõ ràng trong cùng một project để dễ quản lý.

## Chức năng

### Người đọc
- Trang chủ: bài nổi bật, bài mới, sidebar danh mục/tag/bài xem nhiều
- Danh sách bài theo danh mục, tag; tìm kiếm; phân trang
- Chi tiết bài: nội dung rich-text, ảnh bìa, tác giả, lượt xem, bài liên quan
- Bình luận có trả lời, like và lưu bài
- Đăng ký, đăng nhập, hồ sơ cá nhân, đổi mật khẩu
- Trang giới thiệu, liên hệ, trang lỗi 404/500

### Tác giả
- Dashboard thống kê bài viết của mình
- CRUD bài viết, upload ảnh bìa, chọn danh mục/tag
- Lưu nháp hoặc xuất bản, soạn thảo bằng TinyMCE

### Quản trị
- Duyệt bài, duyệt/ẩn bình luận, quản lý người dùng
- Quản lý danh mục, tag
- Dashboard thống kê: số bài, lượt xem, top bài, biểu đồ theo tháng

## Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3.11, Django 5.2 |
| Database | MariaDB 10.11 (tương thích MySQL), driver `mysqlclient` |
| Frontend | Django Templates, Bootstrap 5, crispy-forms |
| Soạn thảo | django-tinymce |
| Ảnh | Pillow |
| Cấu hình | python-decouple (`.env`) |
| Static | WhiteNoise |

## Cấu trúc thư mục

```
cuoikycnweb/
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── apps/
│       ├── accounts/        # người dùng, xác thực, hồ sơ
│       ├── blog/            # danh mục, tag, bài viết
│       └── interactions/    # bình luận, like, bookmark, liên hệ
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── partials/
│   │   ├── blog/
│   │   ├── accounts/
│   │   └── pages/
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── media/                   # ảnh upload (không commit)
├── scripts/
│   └── init_db.sql
├── docs/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Cài đặt

### 1. Yêu cầu
- Python 3.11+
- MariaDB 10.11+ hoặc MySQL 8+
- Git

### 2. Tạo môi trường ảo và cài thư viện

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường

```powershell
Copy-Item .env.example .env
```

Mở `.env` và cập nhật `SECRET_KEY`, thông tin database. Máy này MariaDB chạy ở port **3307** (không phải 3306), nên giữ `DB_PORT=3307`.

### 4. Tạo database

```powershell
& "C:\Program Files\MariaDB 10.11\bin\mysql.exe" -u root -p -e "source D:/cuoikycnweb/scripts/init_db.sql"
```

Mặc định script tạo database `blogdb` và user `bloguser` (mật khẩu đổi trong `.env`).

### 5. Migrate và chạy

```powershell
cd backend
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py createsuperuser
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8025
```

Mở http://127.0.0.1:8025

Dự án dùng cổng **8025** để tránh xung đột với project khác đang chạy cổng 8000. Có thể chạy bằng script tự tìm cổng trống:

```powershell
.\scripts\run_server.ps1
```

## Lệnh thường dùng

```powershell
..\.venv\Scripts\python.exe manage.py makemigrations
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py createsuperuser
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8025
..\.venv\Scripts\python.exe manage.py test
..\.venv\Scripts\python.exe manage.py collectstatic
```

## Lộ trình thực hiện

- [x] Phase 0 — Môi trường, thư viện, cấu hình, README
- [x] Phase 1 — Khởi tạo project, settings, MySQL, static/media
- [x] Phase 2 — Accounts: người dùng, đăng nhập, phân quyền
- [x] Phase 3 — Blog core: model, admin, dữ liệu mẫu
- [x] Phase 4 — Giao diện public: trang chủ, danh sách, chi tiết, tìm kiếm
- [x] Phase 5 — Tương tác: bình luận, like, bookmark, lượt xem
- [x] Phase 6 — Author dashboard: CRUD bài viết, TinyMCE
- [x] Phase 7 — Quản trị và thống kê
- [ ] Phase 8 — Hoàn thiện: responsive, SEO, test, seed data
- [ ] Phase 9 — Triển khai và báo cáo

## Quy ước code

- Mỗi app có `urls.py` riêng với `app_name` và namespace.
- CBV cho CRUD, FBV cho trang đơn giản.
- Form đặt trong `forms.py`, logic nghiệp vụ trong `services.py`.
- Template kế thừa `base.html`, tách partial dùng lại.
- Commit theo phase: `feat(blog): ...`, `fix(accounts): ...`.