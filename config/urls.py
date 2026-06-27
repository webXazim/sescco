from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from apps.seo.sitemaps import StaticViewSitemap, PageSitemap, ServiceSitemap, ProjectSitemap, DocumentSitemap, CareerSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "pages": PageSitemap,
    "services": ServiceSitemap,
    "projects": ProjectSitemap,
    "documents": DocumentSitemap,
    "careers": CareerSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include("apps.seo.urls")),
]

urlpatterns += i18n_patterns(
    path("", include("apps.pages.urls")),
    path("services/", include("apps.services.urls")),
    path("projects/", include("apps.projects.urls")),
    path("clients-certifications/", include("apps.clients.urls")),
    path("downloads/", include("apps.documents.urls")),
    path("careers/", include("apps.careers.urls")),
    path("contact/", include("apps.inquiries.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "apps.pages.views.error_404"
handler500 = "apps.pages.views.error_500"
