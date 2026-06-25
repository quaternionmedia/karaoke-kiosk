"""Venue endpoints: public kiosk config + admin CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from kiosk.db import get_session
from kiosk.deps import admin_guard
from kiosk.schemas.venue import VenueConfig, VenueCreate, VenueRead, VenueUpdate
from kiosk.services import venues as service

# Public kiosk config.
router = APIRouter(tags=["venue"])

admin_router = APIRouter(
    prefix="/admin/venues", tags=["admin:venues"], dependencies=[Depends(admin_guard)]
)


@router.get("/venue", response_model=VenueConfig)
def kiosk_config(session: Session = Depends(get_session)) -> VenueConfig:
    venue = service.get_default_venue(session)
    if venue is None:
        raise HTTPException(status_code=404, detail="No venue configured")
    return VenueConfig.from_venue(venue)


@admin_router.get("", response_model=list[VenueRead])
def list_venues(session: Session = Depends(get_session)) -> list[VenueRead]:
    return service.list_venues(session)


@admin_router.post("", response_model=VenueRead, status_code=201)
def create_venue(
    data: VenueCreate, session: Session = Depends(get_session)
) -> VenueRead:
    return service.create_venue(session, data)


@admin_router.get("/{venue_id}", response_model=VenueRead)
def get_venue(venue_id: int, session: Session = Depends(get_session)) -> VenueRead:
    venue = service.get_venue(session, venue_id)
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue


@admin_router.patch("/{venue_id}", response_model=VenueRead)
def update_venue(
    venue_id: int, data: VenueUpdate, session: Session = Depends(get_session)
) -> VenueRead:
    venue = service.get_venue(session, venue_id)
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    return service.update_venue(session, venue, data)


@admin_router.delete("/{venue_id}", status_code=204)
def delete_venue(venue_id: int, session: Session = Depends(get_session)) -> None:
    venue = service.get_venue(session, venue_id)
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    service.delete_venue(session, venue)
