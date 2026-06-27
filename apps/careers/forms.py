from django import forms
from django.utils.translation import get_language

from .models import CareerEmailVerification, CareerPageSettings, JobApplication
from .validators import (
    ALLOWED_CAREER_DOCUMENT_EXTENSIONS,
    validate_career_cv_file,
    validate_career_document_file,
)



CAREER_FORM_TEXT = {
    "en": {
        "labels": {
            "full_name": "Full name", "email": "Email", "email_verification_code": "Email verification code",
            "phone": "Phone", "current_location": "Current location", "nationality": "Nationality",
            "work_authorization": "Work authorization", "years_experience": "Years of experience",
            "expected_salary": "Expected salary", "available_from": "Available from",
            "preferred_interview_time": "Preferred interview time", "linkedin_url": "LinkedIn URL",
            "portfolio_url": "Portfolio / website URL", "source": "How did you hear about us?",
            "cover_letter": "Cover letter", "cv": "CV / Resume", "extra_documents": "Additional documents",
            "supporting_document": "Supporting Document", "certificate_document": "Certificate / License",
            "consent": "I confirm that the information provided is accurate and SESCCO may contact me about this application.",
        },
        "placeholders": {
            "full_name": "Full name", "email": "Email address", "email_verification_code": "6-digit code",
            "phone": "Phone / WhatsApp number", "current_location": "Current city / country", "nationality": "Nationality",
            "years_experience": "Years of experience", "expected_salary": "Expected salary, if applicable",
            "available_from": "Notice period / available from", "preferred_interview_time": "Preferred interview time, if any",
            "linkedin_url": "LinkedIn profile URL", "portfolio_url": "Portfolio / website URL",
            "cover_letter": "Short message to HR",
        },
    },
    "ar": {
        "labels": {
            "full_name": "الاسم الكامل", "email": "البريد الإلكتروني", "email_verification_code": "رمز التحقق من البريد الإلكتروني",
            "phone": "رقم الهاتف", "current_location": "الموقع الحالي", "nationality": "الجنسية",
            "work_authorization": "تصريح العمل", "years_experience": "سنوات الخبرة",
            "expected_salary": "الراتب المتوقع", "available_from": "تاريخ التوفر",
            "preferred_interview_time": "وقت المقابلة المفضل", "linkedin_url": "رابط لينكدإن",
            "portfolio_url": "رابط الأعمال / الموقع", "source": "كيف عرفت عنا؟",
            "cover_letter": "خطاب التعريف", "cv": "السيرة الذاتية", "extra_documents": "مستندات إضافية",
            "supporting_document": "مستند داعم", "certificate_document": "شهادة / رخصة",
            "consent": "أؤكد أن المعلومات المقدمة صحيحة، ويمكن لـ SESCCO التواصل معي بخصوص هذا الطلب.",
        },
        "placeholders": {
            "full_name": "الاسم الكامل", "email": "عنوان البريد الإلكتروني", "email_verification_code": "رمز من 6 أرقام",
            "phone": "رقم الهاتف / واتساب", "current_location": "المدينة / الدولة الحالية", "nationality": "الجنسية",
            "years_experience": "سنوات الخبرة", "expected_salary": "الراتب المتوقع إن وجد",
            "available_from": "فترة الإشعار / تاريخ التوفر", "preferred_interview_time": "وقت المقابلة المفضل إن وجد",
            "linkedin_url": "رابط ملف لينكدإن", "portfolio_url": "رابط الأعمال / الموقع",
            "cover_letter": "رسالة قصيرة إلى الموارد البشرية",
        },
    },
    "zh-hans": {
        "labels": {
            "full_name": "姓名", "email": "电子邮箱", "email_verification_code": "邮箱验证码",
            "phone": "电话", "current_location": "当前所在地", "nationality": "国籍",
            "work_authorization": "工作许可", "years_experience": "工作年限",
            "expected_salary": "期望薪资", "available_from": "可入职时间",
            "preferred_interview_time": "偏好面试时间", "linkedin_url": "LinkedIn 链接",
            "portfolio_url": "作品集 / 网站链接", "source": "您是如何了解我们的？",
            "cover_letter": "求职说明", "cv": "简历", "extra_documents": "其他文件",
            "supporting_document": "支持文件", "certificate_document": "证书 / 执照",
            "consent": "我确认所提供的信息准确无误，并同意 SESCCO 就本次申请与我联系。",
        },
        "placeholders": {
            "full_name": "姓名", "email": "电子邮箱地址", "email_verification_code": "6 位验证码",
            "phone": "电话 / WhatsApp 号码", "current_location": "当前城市 / 国家", "nationality": "国籍",
            "years_experience": "工作年限", "expected_salary": "期望薪资（如适用）",
            "available_from": "通知期 / 可入职时间", "preferred_interview_time": "偏好面试时间（如有）",
            "linkedin_url": "LinkedIn 个人资料链接", "portfolio_url": "作品集 / 网站链接",
            "cover_letter": "给人力资源的简短说明",
        },
    },
}

CAREER_VALIDATION_TEXT = {
    "en": {
        "max_extra": "You can upload up to 6 additional documents.",
        "file_required": "This file is required.",
        "bad_code": "Enter the 6-digit verification code sent to your email.",
        "honeypot": "Application could not be submitted.",
        "closed": "This job is no longer accepting applications.",
        "verify_before_submit": "Please verify this email with the separate verification button before submitting the application.",
        "duplicate": "You have already applied to this post with this email. Please contact HR if you need to update your application.",
    },
    "ar": {
        "max_extra": "يمكنك رفع ما يصل إلى 6 مستندات إضافية.",
        "file_required": "هذا الملف مطلوب.",
        "bad_code": "أدخل رمز التحقق المكوّن من 6 أرقام المرسل إلى بريدك الإلكتروني.",
        "honeypot": "تعذر إرسال الطلب.",
        "closed": "لم تعد هذه الوظيفة تقبل الطلبات.",
        "verify_before_submit": "يرجى التحقق من هذا البريد الإلكتروني باستخدام زر التحقق المنفصل قبل إرسال الطلب.",
        "duplicate": "لقد قدمت بالفعل على هذه الوظيفة بهذا البريد الإلكتروني. يرجى التواصل مع الموارد البشرية إذا كنت بحاجة إلى تحديث طلبك.",
    },
    "zh-hans": {
        "max_extra": "最多可上传 6 个附加文件。",
        "file_required": "此文件为必填项。",
        "bad_code": "请输入发送到您邮箱的 6 位验证码。",
        "honeypot": "无法提交申请。",
        "closed": "该职位已不再接受申请。",
        "verify_before_submit": "请先使用单独的验证按钮完成邮箱验证，然后再提交申请。",
        "duplicate": "您已使用此邮箱申请过该职位。如需更新申请，请联系 HR。",
    },
}


def _career_lang():
    return get_language() or "en"


def _career_validation(key):
    lang = _career_lang()
    return CAREER_VALIDATION_TEXT.get(lang, CAREER_VALIDATION_TEXT["en"]).get(key, CAREER_VALIDATION_TEXT["en"].get(key, key))

ALLOWED_UPLOAD_EXTENSIONS = ALLOWED_CAREER_DOCUMENT_EXTENSIONS
CV_UPLOAD_EXTENSIONS = ALLOWED_CAREER_DOCUMENT_EXTENSIONS


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleFileField, self).clean(item, initial) for item in files]


class JobApplicationForm(forms.ModelForm):
    company_website = forms.CharField(required=False, widget=forms.HiddenInput, label="Leave this field empty")
    email_verification_code = forms.CharField(
        required=False,
        label="Email verification code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"placeholder": "6-digit code", "inputmode": "numeric", "autocomplete": "one-time-code"}),
        help_text="Send a code to your email, then enter the 6-digit code before submitting.",
    )
    consent = forms.BooleanField(
        required=True,
        label="I confirm that the information provided is accurate and SESCCO may contact me about this application.",
    )
    extra_documents = MultipleFileField(
        required=False,
        label="Additional documents",
        help_text="Optional: upload certificates, licenses, portfolio files or other supporting documents.",
    )

    class Meta:
        model = JobApplication
        fields = [
            "full_name",
            "email",
            "email_verification_code",
            "phone",
            "current_location",
            "nationality",
            "work_authorization",
            "years_experience",
            "expected_salary",
            "available_from",
            "preferred_interview_time",
            "linkedin_url",
            "portfolio_url",
            "source",
            "cover_letter",
            "cv",
            "extra_documents",
            "supporting_document",
            "certificate_document",
            "consent",
            "company_website",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone / WhatsApp number"}),
            "current_location": forms.TextInput(attrs={"placeholder": "Current city / country"}),
            "nationality": forms.TextInput(attrs={"placeholder": "Nationality"}),
            "work_authorization": forms.Select(),
            "years_experience": forms.NumberInput(attrs={"step": "0.5", "min": "0", "placeholder": "Years of experience"}),
            "expected_salary": forms.TextInput(attrs={"placeholder": "Expected salary, if applicable"}),
            "available_from": forms.TextInput(attrs={"placeholder": "Notice period / available from"}),
            "preferred_interview_time": forms.TextInput(attrs={"placeholder": "Preferred interview time, if any"}),
            "linkedin_url": forms.URLInput(attrs={"placeholder": "LinkedIn profile URL"}),
            "portfolio_url": forms.URLInput(attrs={"placeholder": "Portfolio / website URL"}),
            "source": forms.Select(),
            "cover_letter": forms.Textarea(attrs={"placeholder": "Short message to HR", "rows": 5}),
        }
        labels = {
            "work_authorization": "Work authorization",
            "preferred_interview_time": "Preferred interview time",
            "linkedin_url": "LinkedIn URL",
            "portfolio_url": "Portfolio / website URL",
            "cv": "CV / Resume",
            "supporting_document": "Supporting Document",
            "certificate_document": "Certificate / License",
        }

    def __init__(self, *args, job=None, career_settings=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = job
        self.career_settings = career_settings
        self.email_verification = None
        lang = _career_lang()
        localized_form_text = CAREER_FORM_TEXT.get(lang, CAREER_FORM_TEXT["en"])
        for field_name, label in localized_form_text.get("labels", {}).items():
            if field_name in self.fields:
                self.fields[field_name].label = label
        for field_name, placeholder in localized_form_text.get("placeholders", {}).items():
            if field_name in self.fields and placeholder:
                self.fields[field_name].widget.attrs["placeholder"] = placeholder

        choice_text = {
            "ar": {
                "Not specified": "غير محدد",
                "Saudi National": "مواطن سعودي",
                "Transferable Iqama": "إقامة قابلة للنقل",
                "Requires Company Sponsorship": "يتطلب كفالة الشركة",
                "Visit / Temporary Visa": "زيارة / تأشيرة مؤقتة",
                "Other": "أخرى",
                "Company Website": "موقع الشركة",
                "LinkedIn": "لينكدإن",
                "Employee Referral": "ترشيح موظف",
                "Job Board": "موقع وظائف",
                "Walk-in": "زيارة مباشرة",
            },
            "zh-hans": {
                "Not specified": "未指定",
                "Saudi National": "沙特公民",
                "Transferable Iqama": "可转移居留证",
                "Requires Company Sponsorship": "需要公司担保",
                "Visit / Temporary Visa": "访问 / 临时签证",
                "Other": "其他",
                "Company Website": "公司网站",
                "LinkedIn": "LinkedIn",
                "Employee Referral": "员工推荐",
                "Job Board": "招聘网站",
                "Walk-in": "现场咨询",
            },
        }.get(lang, {})
        for choice_field in ("work_authorization", "source"):
            if choice_field in self.fields and choice_text:
                self.fields[choice_field].choices = [(value, choice_text.get(str(label), label)) for value, label in self.fields[choice_field].choices]
        for field in self.fields.values():
            widget = field.widget
            css_class = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{css_class} career-form-control".strip()
        for field_name in ("cv", "supporting_document", "certificate_document", "extra_documents"):
            self.fields[field_name].widget.attrs.update({"accept": ".pdf,.doc,.docx"})

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if self.job and email:
            exists = JobApplication.objects.filter(job=self.job, email__iexact=email).exists()
            if exists:
                settings = self.career_settings
                message = _career_validation("duplicate")
                if settings and settings.duplicate_application_text:
                    message = settings.duplicate_application_text
                raise forms.ValidationError(message)
        return email

    def clean_cv(self):
        return self._validate_upload("cv", required=True, allowed_extensions=CV_UPLOAD_EXTENSIONS)

    def clean_supporting_document(self):
        return self._validate_upload("supporting_document", required=False)

    def clean_certificate_document(self):
        return self._validate_upload("certificate_document", required=False)

    def clean_extra_documents(self):
        files = self.cleaned_data.get("extra_documents") or []
        if len(files) > 6:
            raise forms.ValidationError(_career_validation("max_extra"))
        for upload in files:
            self._validate_file(upload, required=False)
        return files

    def _validate_upload(self, field_name, required=False, allowed_extensions=ALLOWED_UPLOAD_EXTENSIONS):
        upload = self.cleaned_data.get(field_name)
        return self._validate_file(upload, required=required, allowed_extensions=allowed_extensions)

    def _validate_file(self, upload, required=False, allowed_extensions=ALLOWED_UPLOAD_EXTENSIONS):
        if required and not upload:
            raise forms.ValidationError(_career_validation("file_required"))
        if not upload:
            return upload
        try:
            if allowed_extensions == CV_UPLOAD_EXTENSIONS:
                validate_career_cv_file(upload)
            else:
                validate_career_document_file(upload)
        except forms.ValidationError:
            raise
        except Exception as exc:
            raise forms.ValidationError(str(exc))
        return upload


    def clean_email_verification_code(self):
        code = (self.cleaned_data.get("email_verification_code") or "").strip()
        if code and (not code.isdigit() or len(code) != 6):
            raise forms.ValidationError(_career_validation("bad_code"))
        return code

    def clean_company_website(self):
        if self.cleaned_data.get("company_website"):
            raise forms.ValidationError(_career_validation("honeypot"))
        return ""

    def clean(self):
        cleaned = super().clean()
        if self.job and not self.job.is_open:
            raise forms.ValidationError(_career_validation("closed"))
        email = (cleaned.get("email") or "").strip().lower()
        if self.job and email and not self.errors.get("email"):
            verification = CareerEmailVerification.find_latest_verified(self.job, email)
            if not verification:
                self.add_error(
                    "email_verification_code",
                    _career_validation("verify_before_submit"),
                )
            else:
                self.email_verification = verification
        return cleaned


class ApplicationDashboardFilterForm(forms.Form):
    SORT_CHOICES = [
        ("newest", "Newest first"),
        ("oldest", "Oldest first"),
        ("status", "Status"),
        ("job", "Job title"),
        ("interview", "Interview date"),
    ]

    q = forms.CharField(required=False, label="Search", widget=forms.TextInput(attrs={"placeholder": "Name, email, phone or reference"}))
    job = forms.ModelChoiceField(required=False, label="Job", queryset=None, empty_label="All jobs")
    department = forms.ModelChoiceField(required=False, label="Department", queryset=None, empty_label="All departments")
    status = forms.ChoiceField(required=False, label="Status", choices=[("", "All statuses")] + JobApplication.STATUS_CHOICES)
    date_from = forms.DateField(required=False, label="From", widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, label="To", widget=forms.DateInput(attrs={"type": "date"}))
    sort = forms.ChoiceField(required=False, label="Sort", choices=SORT_CHOICES, initial="newest")

    def __init__(self, *args, **kwargs):
        from .models import CareerDepartment, JobOpening

        super().__init__(*args, **kwargs)
        self.fields["job"].queryset = JobOpening.objects.order_by("title")
        self.fields["department"].queryset = CareerDepartment.objects.order_by("sort_order", "name")
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} career-admin-control".strip()


class ApplicationBulkStatusForm(forms.Form):
    bulk_status = forms.ChoiceField(
        label="Move selected to",
        choices=JobApplication.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "career-admin-control"}),
    )


class ApplicationReviewForm(forms.ModelForm):
    interview_date = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = JobApplication
        fields = ["status", "internal_notes", "interview_date", "interview_mode", "interview_location", "interview_notes"]
        widgets = {
            "internal_notes": forms.Textarea(attrs={"rows": 5, "placeholder": "Private HR notes, screening result or follow-up action."}),
            "interview_location": forms.TextInput(attrs={"placeholder": "Office address, project site, phone number or meeting link"}),
            "interview_notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Interview instructions for the applicant."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.interview_date:
            self.initial["interview_date"] = self.instance.interview_date.strftime("%Y-%m-%dT%H:%M")
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} career-admin-control".strip()


class InterviewInvitationForm(forms.ModelForm):
    interview_date = forms.DateTimeField(
        required=True,
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )
    email_subject = forms.CharField(
        label="Email subject",
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Interview Invitation — {{ job.title }}"}),
    )
    email_body = forms.CharField(
        label="Email body",
        widget=forms.Textarea(attrs={"rows": 12, "placeholder": "Use {{ application.full_name }}, {{ job.title }}, {{ application.interview_date }}..."}),
        help_text="You can use Django template variables such as {{ application.full_name }}, {{ job.title }}, {{ application.interview_date }} and {{ application.interview_location }}.",
    )

    class Meta:
        model = JobApplication
        fields = ["interview_date", "interview_mode", "interview_location", "interview_notes"]
        widgets = {
            "interview_location": forms.TextInput(attrs={"placeholder": "Office address, phone number or online meeting link"}),
            "interview_notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Arrival instructions, required documents, contact person or meeting notes."}),
        }

    def __init__(self, *args, career_settings=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.career_settings = career_settings or CareerPageSettings.objects.first() or CareerPageSettings()
        if self.instance and self.instance.interview_date:
            self.initial["interview_date"] = self.instance.interview_date.strftime("%Y-%m-%dT%H:%M")
        self.fields["email_subject"].initial = self.career_settings.interview_email_subject
        self.fields["email_body"].initial = self.career_settings.interview_email_body
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} career-admin-control".strip()

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("interview_date"):
            self.add_error("interview_date", "Interview date/time is required before sending an invitation.")
        if not cleaned.get("interview_location"):
            self.add_error("interview_location", "Location, phone number or meeting link is required before sending an invitation.")
        if not cleaned.get("email_subject"):
            self.add_error("email_subject", "Email subject is required.")
        if not cleaned.get("email_body"):
            self.add_error("email_body", "Email body is required.")
        return cleaned


class RejectionEmailForm(forms.Form):
    email_subject = forms.CharField(label="Email subject", max_length=255)
    email_body = forms.CharField(
        label="Email body",
        widget=forms.Textarea(attrs={"rows": 10}),
        help_text="Use {{ application.full_name }}, {{ job.title }}, {{ application.application_reference }} and optional {{ rejection_reason }}.",
    )
    rejection_reason = forms.CharField(
        label="Private or applicant-facing note",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Optional reason or polite note. This appears only if your template includes {{ rejection_reason }}."}),
    )

    def __init__(self, *args, career_settings=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.career_settings = career_settings or CareerPageSettings.objects.first() or CareerPageSettings()
        self.fields["email_subject"].initial = self.career_settings.rejection_email_subject
        self.fields["email_body"].initial = self.career_settings.rejection_email_body
        for field in self.fields.values():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} career-admin-control".strip()
