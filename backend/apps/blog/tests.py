from django.contrib.auth import get_user_model
from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from .models import Category, Post, Tag


User = get_user_model()


class BlogPublicViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPass123!",
            role=User.Role.AUTHOR,
        )
        self.category = Category.objects.create(name="Lập trình Web")
        self.tag = Tag.objects.create(name="Django")
        self.published = Post.objects.create(
            author=self.author,
            category=self.category,
            title="Django cho người mới",
            content="<p>Nội dung Django.</p>",
            status=Post.Status.PUBLISHED,
        )
        self.published.tags.add(self.tag)
        self.draft = Post.objects.create(
            author=self.author,
            category=self.category,
            title="Bài viết bản nháp",
            content="<p>Bản nháp.</p>",
            status=Post.Status.DRAFT,
        )

    def test_home_and_post_list_show_only_published_posts(self):
        home = self.client.get(reverse("home"))
        listing = self.client.get(reverse("blog:post_list"))

        self.assertEqual(home.status_code, 200)
        self.assertEqual(listing.status_code, 200)
        self.assertContains(home, self.published.title)
        self.assertNotContains(home, self.draft.title)
        self.assertContains(listing, self.published.title)
        self.assertNotContains(listing, self.draft.title)

    def test_detail_increments_view_once_per_session(self):
        url = reverse("blog:post_detail", args=[self.published.slug])

        first = self.client.get(url)
        second = self.client.get(url)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.published.refresh_from_db()
        self.assertEqual(self.published.views, 1)

    def test_draft_detail_is_hidden_from_public_but_visible_to_author(self):
        url = reverse("blog:post_detail", args=[self.draft.slug])

        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.author)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.draft.title)

    def test_author_cannot_edit_another_authors_post(self):
        other_author = User.objects.create_user(
            username="otherauthor",
            email="other@example.com",
            password="StrongPass123!",
            role=User.Role.AUTHOR,
        )
        other_post = Post.objects.create(
            author=other_author,
            category=self.category,
            title="Bài của tác giả khác",
            content="<p>Nội dung.</p>",
            status=Post.Status.DRAFT,
        )
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("author:post_update", args=[other_post.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_search_category_and_tag_filters(self):
        self.assertContains(
            self.client.get(reverse("blog:search") + "?q=Django"),
            self.published.title,
        )
        self.assertContains(
            self.client.get(reverse("blog:category", args=[self.category.slug])),
            self.published.title,
        )
        self.assertContains(
            self.client.get(reverse("blog:tag", args=[self.tag.slug])),
            self.published.title,
        )

    def test_seo_endpoints_are_available(self):
        robots = self.client.get(reverse("robots"))
        sitemap = self.client.get(reverse("sitemap"))

        self.assertEqual(robots.status_code, 200)
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, self.published.slug)

    def test_admin_stats_requires_staff_and_is_available_to_superuser(self):
        self.client.force_login(self.author)
        self.assertEqual(self.client.get(reverse("admin_stats")).status_code, 302)

        admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse("admin_stats")).status_code, 200)


class AuthorPermissionTests(TestCase):
    def setUp(self):
        self.reader = User.objects.create_user(
            username="reader",
            email="reader@example.com",
            password="StrongPass123!",
        )
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPass123!",
            role=User.Role.AUTHOR,
        )

    def test_reader_can_access_contributor_dashboard(self):
        self.client.force_login(self.reader)
        response = self.client.get(reverse("author:dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_author_can_access_dashboard(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse("author:dashboard"))

        self.assertEqual(response.status_code, 200)


class AdminActionTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPass123!",
        )
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPass123!",
            role=User.Role.AUTHOR,
        )
        category = Category.objects.create(name="Quản trị")
        self.posts = [
            Post.objects.create(
                author=self.author,
                category=category,
                title=f"Bài quản trị {index}",
                content="<p>Nội dung.</p>",
                status=Post.Status.DRAFT,
            )
            for index in range(2)
        ]
        self.post_admin = admin.site._registry[Post]
        self.request = self.client.request().wsgi_request
        self.request.user = self.admin_user

    def test_post_admin_actions_update_selected_posts(self):
        queryset = Post.objects.filter(pk__in=[post.pk for post in self.posts])

        self.post_admin.make_published(self.request, queryset)
        self.assertFalse(Post.objects.filter(status=Post.Status.DRAFT).exists())

        self.post_admin.make_featured(self.request, Post.objects.all())
        self.assertEqual(Post.objects.filter(is_featured=True).count(), 2)

        self.post_admin.remove_featured(self.request, Post.objects.all())
        self.assertFalse(Post.objects.filter(is_featured=True).exists())

        self.post_admin.make_draft(self.request, Post.objects.all())
        self.assertEqual(
            Post.objects.filter(status=Post.Status.DRAFT).count(), 2
        )
