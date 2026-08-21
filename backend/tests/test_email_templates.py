"""Email template CRUD and rendering tests."""

from __future__ import annotations


def test_create_template_success(client, venue):
    """Creating a valid template succeeds."""
    created = client.post(
        "/api/admin/email-templates",
        json={
            "venue_id": venue.id,
            "slug": "test",
            "name": "Test Template",
            "subject": "Test: {name} at {venue}",
            "body": "Hi {name}, you sang {song}!",
        },
    ).json()
    
    assert created["id"]
    assert created["slug"] == "test"
    assert created["subject"] == "Test: {name} at {venue}"


def test_create_template_invalid_placeholder(client, venue):
    """Creating a template with unknown placeholder fails with 422."""
    resp = client.post(
        "/api/admin/email-templates",
        json={
            "venue_id": venue.id,
            "slug": "bad",
            "name": "Bad Template",
            "subject": "Subject",
            "body": "Hi {name}, you sang {unknown_field}!",
        },
    )
    
    assert resp.status_code == 422
    assert "unknown_field" in resp.text.lower() or "unknown" in resp.text.lower()


def test_list_templates_by_venue(client, venue):
    """Listing templates can filter by venue."""
    client.post(
        "/api/admin/email-templates",
        json={
            "venue_id": venue.id,
            "slug": "test1",
            "name": "Template 1",
            "subject": "Subject",
            "body": "Body {name}",
        },
    )
    
    # Create another venue and template
    venue2 = client.post(
        "/api/admin/venues",
        json={"name": "Other Venue"},
    ).json()
    client.post(
        "/api/admin/email-templates",
        json={
            "venue_id": venue2["id"],
            "slug": "test2",
            "name": "Template 2",
            "subject": "Subject",
            "body": "Body {song}",
        },
    )
    
    # List all
    all_templates = client.get("/api/admin/email-templates").json()
    assert len(all_templates) == 2
    
    # List venue 1 only
    venue1_templates = client.get(f"/api/admin/email-templates?venue_id={venue.id}").json()
    assert len(venue1_templates) == 1
    assert venue1_templates[0]["venue_id"] == venue.id


def test_update_template_validation(client, venue):
    """Updating a template validates placeholders."""
    created = client.post(
        "/api/admin/email-templates",
        json={
            "venue_id": venue.id,
            "slug": "test",
            "name": "Template",
            "subject": "Good: {name}",
            "body": "Good: {song}",
        },
    ).json()
    
    # Try to update with bad placeholder
    resp = client.patch(
        f"/api/admin/email-templates/{created['id']}",
        json={"body": "Bad: {nonexistent}"},
    )
    assert resp.status_code == 422


def test_preview_template(client, venue):
    """Previewing renders the template with sample data."""
    created = client.post(
        "/api/admin/email-templates",
        json={
            "venue_id": venue.id,
            "slug": "test",
            "name": "Template",
            "subject": "Recording: {song} by {name}",
            "body": "Watch at {recording_url}",
        },
    ).json()
    
    preview = client.post(f"/api/admin/email-templates/{created['id']}/preview").json()
    
    assert "Bohemian Rhapsody" in preview["subject"]  # sample song
    assert "Jane Doe" in preview["subject"]  # sample name
    assert "example.com" in preview["body"]  # sample recording URL


def test_delete_template(client, venue):
    """Deleting a template removes it."""
    created = client.post(
        "/api/admin/email-templates",
        json={
            "venue_id": venue.id,
            "slug": "test",
            "name": "Template",
            "subject": "Subject",
            "body": "Body",
        },
    ).json()
    
    client.delete(f"/api/admin/email-templates/{created['id']}")
    
    # Try to fetch it
    resp = client.get(f"/api/admin/email-templates/{created['id']}")
    assert resp.status_code == 404


def test_render_safe_on_malformed_braces(client, session):
    """Rendering handles malformed braces gracefully."""
    from kiosk.services import email_templates
    
    # Malformed brace
    subject, body = email_templates.render(
        "Hi {name} {", 
        "Body {song}"
    )
    # Should not raise, returns originals or partial
    assert subject
    assert body
