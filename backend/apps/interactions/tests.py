from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import Category, Post

from .models import Comment, Reaction


User = get_user_model()


class InteractionTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            email="author@example.com",
            password="StrongPass123!",
            role=User.Role.AUTHOR,
        )
        self.reader = User.objects.create_user(
            username="reader",
            email="reader@example.com",
            password="StrongPass123!",
        )
        self.category = Category.objects.create(name="Công nghệ")
        self.post = Post.objects.create(
            author=self.author,
            category=self.category,
            title="Bài viết tương tác",
            content="<p>Nội dung.</p>",
            status=Post.Status.PUBLISHED,
        )
        self.comment_url = reverse(
            "interactions:add_comment", args=[self.post.slug]
        )
        self.like_url = reverse(
            "interactions:toggle_reaction",
            args=[self.post.slug, Reaction.Kind.LIKE],
        )
        self.bookmark_url = reverse(
            "interactions:toggle_reaction",
            args=[self.post.slug, Reaction.Kind.BOOKMARK],
        )

    def test_reader_comment_waits_for_moderation(self):
        self.client.force_login(self.reader)
        response = self.client.post(self.comment_url, {"content": "Bài viết hay."})

        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get()
        self.assertFalse(comment.is_approved)

    def test_author_comment_is_approved_automatically(self):
        self.client.force_login(self.author)
        self.client.post(self.comment_url, {"content": "Cảm ơn bạn đọc."})

        comment = Comment.objects.get()
        self.assertTrue(comment.is_approved)

    def test_like_and_bookmark_toggle(self):
        self.client.force_login(self.reader)

        self.client.post(self.like_url)
        self.assertTrue(
            Reaction.objects.filter(
                user=self.reader, post=self.post, kind=Reaction.Kind.LIKE
            ).exists()
        )
        self.client.post(self.like_url)
        self.assertFalse(
            Reaction.objects.filter(
                user=self.reader, post=self.post, kind=Reaction.Kind.LIKE
            ).exists()
        )

        self.client.post(self.bookmark_url)
        response = self.client.get(reverse("interactions:bookmarks"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_comment_and_reaction_require_login(self):
        self.assertEqual(self.client.post(self.comment_url).status_code, 302)
        self.assertEqual(self.client.post(self.like_url).status_code, 302)
