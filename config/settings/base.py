from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django_ckeditor_5",
    "apps.core",
    "apps.pages",
    "apps.services",
    "apps.projects",
    "apps.clients",
    "apps.documents",
    "apps.careers",
    "apps.inquiries",
    "apps.dashboard",
    "apps.seo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "apps.seo.middleware.RedirectRuleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_context",
                "apps.seo.context_processors.schema_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DATABASE_CONN_MAX_AGE", default=60)

# Header/footer settings are shared by every public route. A short in-process
# cache removes repeated database round trips while keeping admin edits fresh.
SITE_CONTEXT_CACHE_SECONDS = env.int("SITE_CONTEXT_CACHE_SECONDS", default=60)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("ar", "Arabic"),
    ("zh-hans", "Chinese"),
]
PARLER_LANGUAGES = {
    None: (
        {"code": "en"},
        {"code": "ar"},
        {"code": "zh-hans"},
    ),
    "default": {
        "fallbacks": ["en"],
        "hide_untranslated": False,
    },
}
LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "Asia/Riyadh"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = env("MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / env("MEDIA_ROOT", default="media")

# Career application hardening. Keep uploads small and serve applicant files only
# through staff-only dashboard download views in production.
CAREER_MAX_UPLOAD_SIZE = env.int("CAREER_MAX_UPLOAD_SIZE", default=8 * 1024 * 1024)
CAREER_APPLICATION_RATE_LIMIT_COUNT = env.int("CAREER_APPLICATION_RATE_LIMIT_COUNT", default=5)
CAREER_APPLICATION_RATE_LIMIT_WINDOW = env.int("CAREER_APPLICATION_RATE_LIMIT_WINDOW", default=60 * 60)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
customColorPalette = [
    {"color": "hsl(218, 94%, 44%)", "label": "Primary Blue"},
    {"color": "hsl(215, 92%, 20%)", "label": "Deep Navy"},
    {"color": "hsl(195, 100%, 44%)", "label": "Cyan"},
]
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "link", "bulletedList", "numberedList",
            "blockQuote", "insertTable", "undo", "redo"
        ],
    },
    "extends": {
        "toolbar": [
            "heading", "|", "bold", "italic", "underline", "link",
            "bulletedList", "numberedList", "blockQuote", "insertTable",
            "imageUpload", "mediaEmbed", "undo", "redo"
        ],
        "image": {
            "toolbar": ["imageTextAlternative", "|", "imageStyle:alignLeft", "imageStyle:full", "imageStyle:alignRight"]
        },
        "table": {
            "contentToolbar": ["tableColumn", "tableRow", "mergeTableCells"]
        },
    },
}

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_TIMEOUT = env.int("EMAIL_TIMEOUT", default=15)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
