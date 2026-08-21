"""Admin email template endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import admin_guard
from kiosk.schemas.email_template import (
    EmailTemplateCreate,
    EmailTemplateRead,
    EmailTemplateUpdate,
)
from kiosk.services import email_templates as service

admin_router = APIRouter(
    prefix="/admin/email-templates",
    tags=["admin:email-templates"],
    dependencies=[Depends(admin_guard)],
)


@admin_router.get("", response_model=list[EmailTemplateRead])
def list_templates(
    venue_id: int | None = None,
    session: Session = Depends(get_session),
) -> list[EmailTemplateRead]:
    """List email templates, optionally filtered by venue."""
    return service.list_templates(session, venue_id=venue_id)


@admin_router.post("", response_model=EmailTemplateRead, status_code=201)
def create_template(
    data: EmailTemplateCreate,
    session: Session = Depends(get_session),
) -> EmailTemplateRead:
    """Create a new email template.
    
    Returns 422 if placeholders contain unknown {names}.
    """
    try:
        return service.create_template(session, data)
    except Exception as exc:
        # PerformanceError with status_code=422 from validation
        if hasattr(exc, "status_code") and exc.status_code == 422:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        raise


@admin_router.get("/{template_id}", response_model=EmailTemplateRead)
def get_template(
    template_id: int,
    session: Session = Depends(get_session),
) -> EmailTemplateRead:
    """Get a template by ID."""
    template = service.get_template(session, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@admin_router.patch("/{template_id}", response_model=EmailTemplateRead)
def update_template(
    template_id: int,
    data: EmailTemplateUpdate,
    session: Session = Depends(get_session),
) -> EmailTemplateRead:
    """Update a template.
    
    Returns 422 if placeholders contain unknown {names}.
    """
    template = service.get_template(session, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        return service.update_template(session, template, data)
    except Exception as exc:
        if hasattr(exc, "status_code") and exc.status_code == 422:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        raise


@admin_router.delete("/{template_id}", status_code=204)
def delete_template(
    template_id: int,
    session: Session = Depends(get_session),
) -> None:
    """Delete a template."""
    template = service.get_template(session, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    service.delete_template(session, template)


@admin_router.post("/{template_id}/preview", response_model=dict)
def preview_template(
    template_id: int,
    session: Session = Depends(get_session),
) -> dict:
    """Preview the template with sample data."""
    template = service.get_template(session, template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    
    sample_context = {
        "name": "Jane Doe",
        "song": "Bohemian Rhapsody",
        "recording_url": "https://example.com/recording.mp4",
        "venue": "Neon Nights Karaoke",
    }
    subject, body = service.render(
        template.subject, template.body, **sample_context
    )
    return {"subject": subject, "body": body}
