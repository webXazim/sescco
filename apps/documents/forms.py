from django import forms
from django.utils.translation import get_language
from .models import DocumentRequest


DOC_FORM_TEXT = {
    "en": {
        "name": ("Name", "Enter your name"),
        "email": ("Email", "Enter your email"),
        "phone": ("Phone", "Enter your phone"),
        "company": ("Company", "Enter company name"),
        "requested_document": ("Requested document", "Example: Company Profile, HSE Policy"),
        "message": ("Message", "Tell us which document you need..."),
    },
    "ar": {
        "name": ("الاسم", "أدخل اسمك"),
        "email": ("البريد الإلكتروني", "أدخل بريدك الإلكتروني"),
        "phone": ("رقم الهاتف", "أدخل رقم الهاتف"),
        "company": ("الشركة", "أدخل اسم الشركة"),
        "requested_document": ("المستند المطلوب", "مثال: ملف الشركة، سياسة السلامة"),
        "message": ("الرسالة", "اكتب اسم المستند الذي تحتاجه..."),
    },
    "zh-hans": {
        "name": ("姓名", "请输入您的姓名"),
        "email": ("电子邮箱", "请输入您的电子邮箱"),
        "phone": ("电话", "请输入您的电话"),
        "company": ("公司", "请输入公司名称"),
        "requested_document": ("所需文件", "例如：公司简介、HSE 政策"),
        "message": ("留言", "请说明您需要的文件..."),
    },
}


class DocumentRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = get_language() or "en"
        labels = DOC_FORM_TEXT.get(lang, DOC_FORM_TEXT["en"])
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            if name in labels:
                label, placeholder = labels[name]
                field.label = label
                if placeholder:
                    field.widget.attrs["placeholder"] = placeholder

    class Meta:
        model = DocumentRequest
        fields = ["name", "email", "phone", "company", "requested_document", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }
