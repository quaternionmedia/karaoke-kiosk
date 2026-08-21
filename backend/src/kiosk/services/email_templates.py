"""Email template CRUD, validation, and rendering."""

from __future__ import annotations

import re
from collections import defaultdict
from sqlmodel import Session, select

from kiosk.models.email_template import EmailTemplate
from kiosk.schemas.email_template import EmailTemplateCreate, EmailTemplateUpdate

# Allowed placeholders that can be used in templates
ALLOWED_PLACEHOLDERS = frozenset({"name", "song", "recording_url", "venue"})

# Module-level defaults (fallback when no template is found)
DEFAULT_SHARE_SUBJECT = "Your performance at {venue}!"
DEFAULT_SHARE_BODY = "Hi {name}, here is your recording of {song}: {recording_url}"


def validate_placeholders(text: str) -> tuple[bool, str | None]:
    """Check that all {placeholders} in text are known.
    
    Returns (is_valid, error_message).
    """
    # Find all {placeholder} patterns
    placeholders = set(re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', text))
    unknown = placeholders - ALLOWED_PLACEHOLDERS
    if unknown:
        return False, f"Unknown placeholders: {', '.join(sorted(unknown))}"
    
    # Also check for malformed braces
    try:
        # Try a dummy format to catch ValueError for mismatched braces
        text.format_map(defaultdict(str))
    except ValueError as e:
        return False, f"Malformed template: {e}"
    
    return True, None


def render(subject: str, body: str, **context) -> tuple[str, str]:
    """Render subject and body templates with safe placeholder handling.
    
    Unknown placeholders are replaced with empty strings, never raises KeyError.
    """
    ctx = defaultdict(str, context)
    try:
        rendered_subject = subject.format_map(ctx)
        rendered_body = body.format_map(ctx)
        return rendered_subject, rendered_body
    except ValueError:
        # Malformed braces; return originals rather than failing
        return subject, body


def list_templates(session: Session, venue_id: int | None = None) -> list[EmailTemplate]:
    stmt = select(EmailTemplate)
    if venue_id is not None:
        stmt = stmt.where(EmailTemplate.venue_id == venue_id)
    return list(session.exec(stmt).all())


def get_template(session: Session, template_id: int) -> EmailTemplate | None:
    return session.get(EmailTemplate, template_id)


def get_template_by_slug(
    session: Session, venue_id: int, slug: str
) -> EmailTemplate | None:
    """Look up a template by venue and slug."""
    return session.exec(
        select(EmailTemplate).where(
            EmailTemplate.venue_id == venue_id,
            EmailTemplate.slug == slug,
        )
    ).first()


def create_template(
    session: Session, data: EmailTemplateCreate
) -> EmailTemplate:
    # Validate placeholders before saving
    is_valid, error = validate_placeholders(data.subject + data.body)
    if not is_valid:
        from kiosk.services.performances import PerformanceError
        raise PerformanceError(f"Template validation failed: {error}", status_code=422)
    
    template = EmailTemplate(**data.model_dump())
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


def update_template(
    session: Session, template: EmailTemplate, data: EmailTemplateUpdate
) -> EmailTemplate:
    # Validate placeholders if subject or body is being updated
    subject = data.subject if data.subject is not None else template.subject
    body = data.body if data.body is not None else template.body
    is_valid, error = validate_placeholders(subject + body)
    if not is_valid:
        from kiosk.services.performances import PerformanceError
        raise PerformanceError(f"Template validation failed: {error}", status_code=422)
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


def delete_template(session: Session, template: EmailTemplate) -> None:
    session.delete(template)
    session.commit()
