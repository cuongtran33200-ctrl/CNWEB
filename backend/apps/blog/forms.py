from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            "title",
            "category",
            "tags",
            "thumbnail",
            "excerpt",
            "content",
            "status",
        )
        widgets = {
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "tags": forms.CheckboxSelectMultiple(),
        }
        labels = {
            "title": "Tiêu đề",
            "category": "Danh mục",
            "tags": "Tag",
            "thumbnail": "Ảnh bìa",
            "excerpt": "Tóm tắt",
            "content": "Nội dung",
            "status": "Trạng thái",
        }
        help_texts = {
            "excerpt": "Để trống để tự sinh từ nội dung.",
            "thumbnail": "Ảnh JPG/PNG/WebP, không quá 2 MB.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in {"content", "tags", "thumbnail"}:
                continue
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")
