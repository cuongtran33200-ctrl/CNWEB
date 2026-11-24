from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.test.utils import override_settings
from re import search

from .models import User
from .validators import MAX_IMAGE_SIZE, validate_image_upload


class AccountFlowTests(TestCase):
    def test_register_creates_reader_and_redirects_to_login(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newreader",
                "email": "reader@example.com",
                "first_name": "New",
                "last_name": "Reader",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(username="newreader")
        self.assertEqual(user.role, User.Role.READER)
        self.assertTrue(user.check_password("StrongPass123!"))

    def test_login_redirects_authenticated_user_to_home(self):
        User.objects.create_user(
            username="reader",
            email="reader@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "reader", "password": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("home"))

    def test_profile_and_password_change_require_login(self):
        self.assertRedirects(
            self.client.get(reverse("accounts:profile")),
            f'{reverse("accounts:login")}?next={reverse("accounts:profile")}',
        )
        self.assertRedirects(
            self.client.get(reverse("accounts:password_change")),
            f'{reverse("accounts:login")}?next={reverse("accounts:password_change")}',
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_email_and_confirm_flow(self):
        User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="OldStrongPass123!",
        )

        reset_url = reverse("accounts:password_reset")
        self.assertEqual(self.client.get(reset_url).status_code, 200)
        response = self.client.post(reset_url, {"email": "reset@example.com"})

        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn("Đặt lại mật khẩu SBCB Blog", message.subject)
        match = search(r"/accounts/password-reset/(\S+)/([\w-]+)/", message.body)
        self.assertIsNotNone(match)

        confirm_url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": match.group(1), "token": match.group(2)},
        )
        confirm_response = self.client.get(confirm_url, follow=True)
        self.assertEqual(confirm_response.status_code, 200)
        confirm_url = confirm_response.request["PATH_INFO"]
        response = self.client.post(
            confirm_url,
            {
                "new_password1": "NewStrongPass123!",
                "new_password2": "NewStrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("accounts:password_reset_complete"))

        self.assertTrue(
            self.client.login(
                username="resetuser", password="NewStrongPass123!"
            )
        )


class ImageValidationTests(TestCase):
    def test_image_validator_rejects_oversized_file(self):
        upload = SimpleUploadedFile(
            "avatar.png",
            b"x" * (MAX_IMAGE_SIZE + 1),
            content_type="image/png",
        )

        with self.assertRaisesMessage(ValidationError, "không quá 2 MB"):
            validate_image_upload(upload)

    def test_image_validator_rejects_unsupported_content_type(self):
        upload = SimpleUploadedFile(
            "avatar.gif", b"image", content_type="image/gif"
        )

        with self.assertRaisesMessage(ValidationError, "Chỉ chấp nhận ảnh"):
            validate_image_upload(upload)
