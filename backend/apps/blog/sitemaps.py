from django.contrib.sitemaps import Sitemap

from .models import Category, Post, Tag


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class TagSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.4

    def items(self):
        return (
            Tag.objects.filter(posts__status=Post.Status.PUBLISHED)
            .distinct()
        )

    def location(self, obj):
        return obj.get_absolute_url()