"""Courier API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.courier import (
    CourierCreate,
    CourierUpdate,
    CourierResponse,
    CourierLocationUpdate,
    CourierStatusUpdate
)
from app.crud import courier as courier_crud

router = APIRouter(prefix="/couriers", tags=["couriers"])


@router.post("/", response_model=CourierResponse, status_code=status.HTTP_201_CREATED)
def create_courier(courier: CourierCreate, db: Session = Depends(get_db)):
    """Create a new courier."""
    # Check if email already exists
    existing = courier_crud.get_courier_by_email(db, courier.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Courier with this email already exists"
        )
    return courier_crud.create_courier(db, courier)


@router.get("/", response_model=List[CourierResponse])
def get_couriers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all couriers."""
    return courier_crud.get_couriers(db, skip=skip, limit=limit)


@router.get("/available", response_model=List[CourierResponse])
def get_available_couriers(db: Session = Depends(get_db)):
    """Get all available couriers."""
    return courier_crud.get_available_couriers(db)


@router.get("/{courier_id}", response_model=CourierResponse)
def get_courier(courier_id: int, db: Session = Depends(get_db)):
    """Get courier by ID."""
    courier = courier_crud.get_courier(db, courier_id)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return courier


@router.put("/{courier_id}", response_model=CourierResponse)
def update_courier(courier_id: int, courier: CourierUpdate, db: Session = Depends(get_db)):
    """Update courier details."""
    updated = courier_crud.update_courier(db, courier_id, courier)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.patch("/{courier_id}/location", response_model=CourierResponse)
def update_courier_location(
    courier_id: int,
    location: CourierLocationUpdate,
    db: Session = Depends(get_db)
):
    """Update courier GPS location."""
    updated = courier_crud.update_courier_location(db, courier_id, location)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.patch("/{courier_id}/status", response_model=CourierResponse)
def update_courier_status(
    courier_id: int,
    status_update: CourierStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update courier status (available/busy/offline)."""
    updated = courier_crud.update_courier_status(db, courier_id, status_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.delete("/{courier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_courier(courier_id: int, db: Session = Depends(get_db)):
    """Delete a courier."""
    deleted = courier_crud.delete_courier(db, courier_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return None
