from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

ALLOWED_CAREER_DOCUMENT_EXTENSIONS = (".pdf", ".doc", ".docx")
CAREER_DOCUMENT_SIGNATURES = {
    ".pdf": (b"%PDF",),
    ".doc": (b"\xd0\xcf\x11\xe0",),
    ".docx": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
}
DEFAULT_MAX_UPLOAD_SIZE = 8 * 1024 * 1024


def career_max_upload_size():
    return int(getattr(settings, "CAREER_MAX_UPLOAD_SIZE", DEFAULT_MAX_UPLOAD_SIZE))


def allowed_career_extensions_display():
    return ", ".join(ext.upper().replace(".", "") for ext in ALLOWED_CAREER_DOCUMENT_EXTENSIONS)


def validate_career_document_file(upload):
    """Validate public career uploads before they are stored.

    Career documents are intentionally limited to common document formats.
    Images and archives are not accepted because applicant media should be
    private, easy for HR to review, and safer to store long term.
    """
    if not upload:
        return

    extension = Path(upload.name or "").suffix.lower()
    if extension not in ALLOWED_CAREER_DOCUMENT_EXTENSIONS:
        raise ValidationError(f"Allowed file types: {allowed_career_extensions_display()}.")

    max_size = career_max_upload_size()
    if upload.size and upload.size > max_size:
        raise ValidationError(f"Each file must be {filesizeformat(max_size)} or smaller.")

    position = None
    try:
        position = upload.tell()
    except Exception:
        position = None

    header = b""
    try:
        upload.seek(0)
        header = upload.read(8) or b""
    except Exception:
        header = b""
    finally:
        try:
            upload.seek(position or 0)
        except Exception:
            pass

    signatures = CAREER_DOCUMENT_SIGNATURES.get(extension, ())
    if header and signatures and not any(header.startswith(signature) for signature in signatures):
        raise ValidationError("The uploaded file content does not match the selected document type.")


def validate_career_cv_file(upload):
    validate_career_document_file(upload)
