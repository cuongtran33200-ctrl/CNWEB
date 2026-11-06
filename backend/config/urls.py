from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from apps.blog.admin_views import stats_dashboard
from apps.blog.sitemaps import CategorySitemap, PostSitemap, TagSitemap
from apps.blog.views import HomeView

sitemaps = {
    "posts": PostSitemap,
    "categories": CategorySitemap,
    "tags": TagSitemap,
}

admin.site.site_header = "Quản trị SBCB Blog"
admin.site.site_title = "SBCB Blog"
admin.site.index_title = "Bảng điều khiển"
admin.site.index_template = "admin/custom_index.html"

urlpatterns = [
    path("admin/stats/", admin.site.admin_view(stats_dashboard), name="admin_stats"),
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
    path("tinymce/", include("tinymce.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("blog/", include("apps.blog.urls")),
    path("author/", include("apps.blog.author_urls")),
    path("", include("apps.interactions.urls")),
    path("", HomeView.as_view(), name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)