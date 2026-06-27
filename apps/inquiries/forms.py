from django import forms
from django.utils.translation import get_language
from .models import ContactInquiry


CONTACT_FORM_TEXT = {
    "en": {
        "full_name": ("Full name", "Enter your full name"),
        "company_name": ("Company name", "Enter company name"),
        "email": ("Email", "Enter your email address"),
        "phone": ("Phone", "Enter your phone number"),
        "subject": ("Subject", ""),
        "message": ("Message", "Tell us about your project or inquiry..."),
        "consent": ("I agree to be contacted.", ""),
    },
    "ar": {
        "full_name": ("الاسم الكامل", "أدخل اسمك الكامل"),
        "company_name": ("اسم الشركة", "أدخل اسم الشركة"),
        "email": ("البريد الإلكتروني", "أدخل بريدك الإلكتروني"),
        "phone": ("رقم الهاتف", "أدخل رقم الهاتف"),
        "subject": ("الموضوع", ""),
        "message": ("الرسالة", "اكتب تفاصيل مشروعك أو استفسارك..."),
        "consent": ("أوافق على التواصل معي.", ""),
    },
    "zh-hans": {
        "full_name": ("姓名", "请输入您的姓名"),
        "company_name": ("公司名称", "请输入公司名称"),
        "email": ("电子邮箱", "请输入您的电子邮箱"),
        "phone": ("电话", "请输入您的电话号码"),
        "subject": ("主题", ""),
        "message": ("留言", "请说明您的项目或咨询内容..."),
        "consent": ("我同意被联系。", ""),
    },
}


CONTACT_VALIDATION_TEXT = {
    "en": {
        "contact_required": "Please provide at least an email or phone number.",
        "consent_required": "You must agree to be contacted.",
    },
    "ar": {
        "contact_required": "يرجى إدخال البريد الإلكتروني أو رقم الهاتف على الأقل.",
        "consent_required": "يجب الموافقة على التواصل معك.",
    },
    "zh-hans": {
        "contact_required": "请至少提供电子邮箱或电话号码。",
        "consent_required": "您必须同意被联系。",
    },
}


def contact_text(key):
    lang = get_language() or "en"
    return CONTACT_VALIDATION_TEXT.get(lang, CONTACT_VALIDATION_TEXT["en"]).get(key, CONTACT_VALIDATION_TEXT["en"].get(key, key))


class ContactInquiryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = get_language() or "en"
        labels = CONTACT_FORM_TEXT.get(lang, CONTACT_FORM_TEXT["en"])

        self.fields["email"].required = False
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            if name in labels:
                label, placeholder = labels[name]
                field.label = label
                if placeholder:
                    field.widget.attrs["placeholder"] = placeholder

    class Meta:
        model = ContactInquiry
        fields = ["full_name", "company_name", "email", "phone", "subject", "message", "consent"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
            "consent": forms.CheckboxInput(),
        }

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        phone = cleaned.get("phone")
        if not email and not phone:
            raise forms.ValidationError(contact_text("contact_required"))
        if not cleaned.get("consent"):
            raise forms.ValidationError(contact_text("consent_required"))
        return cleaned
