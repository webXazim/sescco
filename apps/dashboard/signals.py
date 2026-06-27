from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.clients.models import Certificate, Client
from apps.documents.models import DownloadDocument, DocumentRequest
from apps.inquiries.models import ContactInquiry
from apps.pages.models import Page
from apps.projects.models import Project
from apps.services.models import Service
from .models import ActivityLog


TRACKED_MODELS = {
    Page: "Pages",
    Service: "Services",
    Project: "Projects",
    Client: "Clients",
    Certificate: "Certificates",
    DownloadDocument: "Documents",
    ContactInquiry: "Inquiries",
    DocumentRequest: "Document Requests",
}


def title_for(instance):
    for attr in ["title", "name", "full_name", "requested_document"]:
        value = getattr(instance, attr, None)
        if value:
            return str(value)
    return str(instance)


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender not in TRACKED_MODELS:
        return
    ActivityLog.objects.create(
        action="Created" if created else "Updated",
        module=TRACKED_MODELS[sender],
        object_title=title_for(instance),
        description=f"{TRACKED_MODELS[sender]} item was {'created' if created else 'updated'}.",
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender not in TRACKED_MODELS:
        return
    ActivityLog.objects.create(
        action="Deleted",
        module=TRACKED_MODELS[sender],
        object_title=title_for(instance),
        description=f"{TRACKED_MODELS[sender]} item was deleted.",
    )
