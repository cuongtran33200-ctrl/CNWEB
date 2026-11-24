from django.core.exceptions import ValidationError


MAX_IMAGE_SIZE = 2 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def validate_image_upload(uploaded_file):
    if uploaded_file.size > MAX_IMAGE_SIZE:
        raise ValidationError("Ảnh phải có dung lượng không quá 2 MB.")

    content_type = getattr(uploaded_file, "content_type", "")
    if content_type and content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError("Chỉ chấp nhận ảnh JPG, PNG hoặc WebP.")
