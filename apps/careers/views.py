from django.conf import settings as django_settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language

from .forms import JobApplicationForm
from .models import (
    CareerBenefit,
    CareerDepartment,
    CareerPageSettings,
    CareerProcessStep,
    CareerStat,
    CareerEmailVerification,
    JobApplication,
    JobApplicationDocument,
    JobOpening,
)


CAREER_VIEW_TEXT = {
    "en": {
        "already_applied_short": "You have already applied to this post.",
        "too_many_applications": "Too many application attempts were submitted from this connection. Please try again later or contact HR directly.",
        "submitted_success": "Your application has been submitted successfully. Our HR team will review it and contact shortlisted candidates.",
        "enter_email": "Enter your email address first.",
        "valid_email": "Enter a valid email address.",
        "duplicate": "You have already applied to this post with this email. Please contact HR if you need to update your application.",
        "already_verified": "Email is already verified. You can submit this application.",
        "email_can_be_used": "This email can be used for this job application.",
        "too_many_codes": "Too many verification codes were requested. Please try again later.",
        "email_not_sent": "Verification email could not be sent",
        "code_sent_prefix": "Verification code sent to",
        "code_sent_suffix": "It expires in {minutes} minutes.",
        "bad_code": "Enter the 6-digit verification code sent to your email.",
        "send_code_first": "Please send a verification code to this email first.",
        "email_verified": "Email verified successfully. You can now submit the application.",
    },
    "ar": {
        "already_applied_short": "لقد قدمت بالفعل على هذه الوظيفة.",
        "too_many_applications": "تم إرسال محاولات تقديم كثيرة من هذا الاتصال. يرجى المحاولة لاحقاً أو التواصل مع الموارد البشرية مباشرة.",
        "submitted_success": "تم إرسال طلبك بنجاح. سيقوم فريق الموارد البشرية بمراجعته والتواصل مع المرشحين المختارين.",
        "enter_email": "أدخل عنوان بريدك الإلكتروني أولاً.",
        "valid_email": "أدخل عنوان بريد إلكتروني صحيحاً.",
        "duplicate": "لقد قدمت بالفعل على هذه الوظيفة بهذا البريد الإلكتروني. يرجى التواصل مع الموارد البشرية إذا كنت بحاجة إلى تحديث طلبك.",
        "already_verified": "تم التحقق من البريد الإلكتروني مسبقاً. يمكنك إرسال الطلب الآن.",
        "email_can_be_used": "يمكن استخدام هذا البريد الإلكتروني لهذا الطلب.",
        "too_many_codes": "تم طلب رموز تحقق كثيرة. يرجى المحاولة لاحقاً.",
        "email_not_sent": "تعذر إرسال رسالة التحقق",
        "code_sent_prefix": "تم إرسال رمز التحقق إلى",
        "code_sent_suffix": "تنتهي صلاحيته خلال {minutes} دقيقة.",
        "bad_code": "أدخل رمز التحقق المكوّن من 6 أرقام المرسل إلى بريدك الإلكتروني.",
        "send_code_first": "يرجى إرسال رمز تحقق إلى هذا البريد الإلكتروني أولاً.",
        "email_verified": "تم التحقق من البريد الإلكتروني بنجاح. يمكنك الآن إرسال الطلب.",
    },
    "zh-hans": {
        "already_applied_short": "您已申请过该职位。",
        "too_many_applications": "来自此连接的申请尝试过多。请稍后再试或直接联系 HR。",
        "submitted_success": "您的申请已成功提交。我们的 HR 团队将进行审核，并联系入围候选人。",
        "enter_email": "请先输入电子邮箱地址。",
        "valid_email": "请输入有效的电子邮箱地址。",
        "duplicate": "您已使用此邮箱申请过该职位。如需更新申请，请联系 HR。",
        "already_verified": "邮箱已验证。您可以提交申请。",
        "email_can_be_used": "此邮箱可用于本职位申请。",
        "too_many_codes": "验证码请求次数过多。请稍后再试。",
        "email_not_sent": "无法发送验证邮件",
        "code_sent_prefix": "验证码已发送至",
        "code_sent_suffix": "有效期为 {minutes} 分钟。",
        "bad_code": "请输入发送到您邮箱的 6 位验证码。",
        "send_code_first": "请先向此邮箱发送验证码。",
        "email_verified": "邮箱验证成功。您现在可以提交申请。",
    },
}


def cvt(key):
    lang = get_language() or "en"
    return CAREER_VIEW_TEXT.get(lang, CAREER_VIEW_TEXT["en"]).get(key, CAREER_VIEW_TEXT["en"].get(key, key))


def career_settings():
    return CareerPageSettings.objects.first() or CareerPageSettings()


def public_jobs_queryset():
    today = timezone.localdate()
    return JobOpening.objects.filter(is_active=True, status="published").filter(
        Q(application_deadline__isnull=True) | Q(application_deadline__gte=today)
    )


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def application_rate_limited(request, job):
    """Small public-form throttle to reduce repeated career form spam."""
    limit = int(getattr(django_settings, "CAREER_APPLICATION_RATE_LIMIT_COUNT", 5))
    window = int(getattr(django_settings, "CAREER_APPLICATION_RATE_LIMIT_WINDOW", 60 * 60))
    if limit <= 0:
        return False
    ip = get_client_ip(request) or "unknown"
    key = f"career_application_submit:{job.pk}:{ip}"
    current = cache.get(key, 0)
    if current >= limit:
        return True
    cache.set(key, current + 1, window)
    return False




CAREER_SESSION_APPLIED_KEY = "career_applied_jobs"


def get_session_applied_jobs(request):
    data = request.session.get(CAREER_SESSION_APPLIED_KEY, {})
    return data if isinstance(data, dict) else {}


def get_session_applied_record(request, job):
    return get_session_applied_jobs(request).get(str(job.pk))


def remember_session_application(request, application):
    data = get_session_applied_jobs(request).copy()
    data[str(application.job_id)] = {
        "slug": application.job.slug,
        "reference": application.application_reference,
        "title": application.job.title,
        "applied_at": timezone.now().isoformat(),
    }
    request.session[CAREER_SESSION_APPLIED_KEY] = data
    request.session.modified = True


def mark_jobs_with_session_application(request, jobs):
    data = get_session_applied_jobs(request)
    for job in jobs:
        record = data.get(str(job.pk))
        job.applied_reference = record.get("reference") if record else ""
    return jobs


def email_code_rate_limited(request, job, email):
    limit = int(getattr(django_settings, "CAREER_EMAIL_OTP_RATE_LIMIT_COUNT", 5))
    window = int(getattr(django_settings, "CAREER_EMAIL_OTP_RATE_LIMIT_WINDOW", 60 * 60))
    if limit <= 0:
        return False
    ip = get_client_ip(request) or "unknown"
    normalized_email = CareerEmailVerification.normalize_email(email)
    key = f"career_email_otp:{job.pk}:{normalized_email}:{ip}"
    current = cache.get(key, 0)
    if current >= limit:
        return True
    cache.set(key, current + 1, window)
    return False

def career_list(request):
    settings = career_settings()
    departments = CareerDepartment.objects.filter(is_active=True)
    jobs = public_jobs_queryset().select_related("department")

    query = request.GET.get("q", "").strip()
    department_slug = request.GET.get("department", "").strip()
    employment_type = request.GET.get("type", "").strip()
    sort = request.GET.get("sort", "featured")

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query)
            | Q(job_code__icontains=query)
            | Q(summary__icontains=query)
            | Q(job_description__icontains=query)
            | Q(location__icontains=query)
            | Q(requirements__icontains=query)
            | Q(qualifications__icontains=query)
            | Q(skills__icontains=query)
        )
    if department_slug:
        jobs = jobs.filter(department__slug=department_slug)
    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)

    if sort == "newest":
        jobs = jobs.order_by("-published_at", "-created_at")
    elif sort == "deadline":
        jobs = jobs.order_by("application_deadline", "sort_order", "title")
    else:
        jobs = jobs.order_by("-is_featured", "sort_order", "title")

    jobs = mark_jobs_with_session_application(request, list(jobs))

    context = {
        "career_settings": settings,
        "departments": departments,
        "jobs": jobs,
        "query": query,
        "active_department": department_slug,
        "active_type": employment_type,
        "sort": sort,
        "employment_types": JobOpening.EMPLOYMENT_TYPES,
        "career_stats": CareerStat.objects.filter(is_active=True),
        "hero_stats": CareerStat.objects.filter(is_active=True, show_on_hero=True)[:3],
        "career_benefits": CareerBenefit.objects.filter(is_active=True),
        "process_steps": CareerProcessStep.objects.filter(is_active=True),
        "meta_title": "Careers at SESCCO",
        "meta_description": "Explore active SESCCO career opportunities and apply online for engineering, project, civil, fitout and support roles.",
    }
    return render(request, "careers/career_list.html", context)


def job_detail(request, slug):
    settings = career_settings()
    job = get_object_or_404(public_jobs_queryset().select_related("department"), slug=slug)
    applied_record = get_session_applied_record(request, job)
    applied_reference = applied_record.get("reference") if applied_record else ""
    related_jobs = mark_jobs_with_session_application(
        request,
        list(public_jobs_queryset().exclude(id=job.id).select_related("department")[:3]),
    )
    return render(
        request,
        "careers/job_detail.html",
        {
            "career_settings": settings,
            "job": job,
            "related_jobs": related_jobs,
            "applied_reference": applied_reference,
            "already_applied": bool(applied_reference),
            "meta_title": f"{job.title} | SESCCO Careers",
            "meta_description": job.summary or f"Apply for {job.title} at SESCCO.",
        },
    )


def apply_job(request, slug):
    settings = career_settings()
    job = get_object_or_404(public_jobs_queryset(), slug=slug)
    applied_record = get_session_applied_record(request, job)
    if applied_record and applied_record.get("reference"):
        messages.info(request, settings.duplicate_application_text or cvt("already_applied_short"))
        success_url = reverse("career_application_success", kwargs={"slug": job.slug})
        return redirect(f"{success_url}?ref={applied_record['reference']}")
    if job.external_application_url:
        return redirect(job.external_application_url)
    if request.method == "POST":
        if application_rate_limited(request, job):
            messages.error(request, cvt("too_many_applications"))
            form = JobApplicationForm(job=job, career_settings=settings)
            return render(request, "careers/job_apply.html", {"career_settings": settings, "job": job, "form": form, "meta_title": f"Apply for {job.title} | SESCCO Careers", "meta_description": job.summary or f"Submit your application for {job.title}."})
        form = JobApplicationForm(request.POST, request.FILES, job=job, career_settings=settings)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            if getattr(form, "email_verification", None):
                application.email_verified = True
                application.email_verified_at = form.email_verification.verified_at or timezone.now()
            application.submitted_ip = get_client_ip(request)
            application.user_agent = request.META.get("HTTP_USER_AGENT", "")[:2000]
            application.save()
            for upload in form.cleaned_data.get("extra_documents", []):
                JobApplicationDocument.objects.create(
                    application=application,
                    title=upload.name,
                    file=upload,
                    document_type="supporting",
                    uploaded_by_applicant=True,
                )
            if getattr(form, "email_verification", None):
                form.email_verification.mark_used()
            remember_session_application(request, application)
            messages.success(request, cvt("submitted_success"))
            success_url = reverse("career_application_success", kwargs={"slug": job.slug})
            return redirect(f"{success_url}?ref={application.application_reference}")
    else:
        form = JobApplicationForm(job=job, career_settings=settings)
    return render(request, "careers/job_apply.html", {"career_settings": settings, "job": job, "form": form, "meta_title": f"Apply for {job.title} | SESCCO Careers", "meta_description": job.summary or f"Submit your application for {job.title}."})



@require_GET
def check_application_email(request, slug):
    settings = career_settings()
    job = get_object_or_404(public_jobs_queryset(), slug=slug)
    email = (request.GET.get("email") or "").strip().lower()
    if not email:
        return JsonResponse({"ok": False, "message": cvt("enter_email")}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"ok": False, "message": cvt("valid_email")}, status=400)
    existing = JobApplication.objects.filter(job=job, email__iexact=email).only("application_reference", "created_at").first()
    if existing:
        message = settings.duplicate_application_text or cvt("duplicate")
        return JsonResponse({"ok": True, "applied": True, "message": message, "reference": existing.application_reference})
    verified = CareerEmailVerification.find_latest_verified(job, email)
    if verified:
        return JsonResponse({"ok": True, "applied": False, "verified": True, "message": cvt("already_verified")})
    return JsonResponse({"ok": True, "applied": False, "verified": False, "message": cvt("email_can_be_used")})


@require_POST
def send_application_email_code(request, slug):
    settings = career_settings()
    job = get_object_or_404(public_jobs_queryset(), slug=slug)
    email = (request.POST.get("email") or "").strip().lower()
    if not email:
        return JsonResponse({"ok": False, "message": cvt("enter_email")}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"ok": False, "message": cvt("valid_email")}, status=400)
    existing = JobApplication.objects.filter(job=job, email__iexact=email).only("application_reference").first()
    if existing:
        message = settings.duplicate_application_text or cvt("duplicate")
        return JsonResponse({"ok": False, "duplicate": True, "message": message, "reference": existing.application_reference}, status=409)
    if email_code_rate_limited(request, job, email):
        return JsonResponse({"ok": False, "message": cvt("too_many_codes")}, status=429)
    try:
        CareerEmailVerification.create_and_send(job, email, request=request, career_settings=settings)
    except Exception as exc:
        return JsonResponse({"ok": False, "message": f"{cvt('email_not_sent')}: {exc}"}, status=500)
    expiry_minutes = int(getattr(django_settings, "CAREER_EMAIL_OTP_EXPIRY_MINUTES", 15))
    return JsonResponse({"ok": True, "message": f"{cvt('code_sent_prefix')} {email}. {cvt('code_sent_suffix').format(minutes=expiry_minutes)}"})


@require_POST
def verify_application_email_code(request, slug):
    job = get_object_or_404(public_jobs_queryset(), slug=slug)
    email = (request.POST.get("email") or "").strip().lower()
    code = (request.POST.get("code") or request.POST.get("email_verification_code") or "").strip()
    if not email:
        return JsonResponse({"ok": False, "message": cvt("enter_email")}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"ok": False, "message": cvt("valid_email")}, status=400)
    if JobApplication.objects.filter(job=job, email__iexact=email).exists():
        settings = career_settings()
        message = settings.duplicate_application_text or cvt("duplicate")
        return JsonResponse({"ok": False, "duplicate": True, "message": message}, status=409)
    if not code or not code.isdigit() or len(code) != 6:
        return JsonResponse({"ok": False, "message": cvt("bad_code")}, status=400)
    verification = CareerEmailVerification.find_latest(job, email)
    if not verification:
        return JsonResponse({"ok": False, "message": cvt("send_code_first")}, status=400)
    ok, message = verification.verify(code)
    if not ok:
        return JsonResponse({"ok": False, "message": message}, status=400)
    return JsonResponse({"ok": True, "verified": True, "message": cvt("email_verified")})


def application_success(request, slug):
    settings = career_settings()
    job = get_object_or_404(JobOpening, slug=slug)
    application = None
    reference = request.GET.get("ref", "").strip()
    if reference:
        application = JobApplication.objects.filter(job=job, application_reference=reference).first()
        if application:
            remember_session_application(request, application)
    return render(request, "careers/application_success.html", {"career_settings": settings, "job": job, "application": application, "meta_title": "Application Submitted | SESCCO Careers", "meta_description": "Your SESCCO career application submission status."})
