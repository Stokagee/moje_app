"""Courier CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.courier import Courier, CourierStatus
from app.schemas.courier import CourierCreate, CourierUpdate, CourierLocationUpdate, CourierStatusUpdate


def create_courier(db: Session, courier: CourierCreate) -> Courier:
    """Create a new courier."""
    db_courier = Courier(
        name=courier.name,
        phone=courier.phone,
        email=courier.email,
        tags=courier.tags,
        status=CourierStatus.offline
    )
    db.add(db_courier)
    db.commit()
    db.refresh(db_courier)
    return db_courier


def get_courier(db: Session, courier_id: int) -> Optional[Courier]:
    """Get courier by ID."""
    return db.query(Courier).filter(Courier.id == courier_id).first()


def get_courier_by_email(db: Session, email: str) -> Optional[Courier]:
    """Get courier by email."""
    return db.query(Courier).filter(Courier.email == email).first()


def get_couriers(db: Session, skip: int = 0, limit: int = 100) -> List[Courier]:
    """Get all couriers."""
    return db.query(Courier).offset(skip).limit(limit).all()


def get_available_couriers(db: Session) -> List[Courier]:
    """Get all available couriers."""
    return db.query(Courier).filter(Courier.status == CourierStatus.available).all()


def update_courier(db: Session, courier_id: int, courier: CourierUpdate) -> Optional[Courier]:
    """Update courier details."""
    db_courier = get_courier(db, courier_id)
    if not db_courier:
        return None

    update_data = courier.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_courier, field, value)

    db.commit()
    db.refresh(db_courier)
    return db_courier


def update_courier_location(db: Session, courier_id: int, location: CourierLocationUpdate) -> Optional[Courier]:
    """Update courier GPS location."""
    db_courier = get_courier(db, courier_id)
    if not db_courier:
        return None

    db_courier.lat = location.lat
    db_courier.lng = location.lng
    db.commit()
    db.refresh(db_courier)
    return db_courier


def update_courier_status(db: Session, courier_id: int, status_update: CourierStatusUpdate) -> Optional[Courier]:
    """Update courier status."""
    db_courier = get_courier(db, courier_id)
    if not db_courier:
        return None

    db_courier.status = status_update.status
    db.commit()
    db.refresh(db_courier)
    return db_courier


def delete_courier(db: Session, courier_id: int) -> bool:
    """Delete courier."""
    db_courier = get_courier(db, courier_id)
    if not db_courier:
        return False

    db.delete(db_courier)
    db.commit()
    return True
