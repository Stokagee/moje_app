"""Dispatch API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.dispatch import DispatchAssign, DispatchResult, DispatchLogResponse
from app.services.dispatch_service import (
    auto_dispatch_order,
    manual_dispatch_order,
    get_available_couriers_for_order
)
from app.crud import dispatch_log as dispatch_log_crud

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


@router.post("/auto/{order_id}", response_model=DispatchResult)
def dispatch_order_auto(order_id: int, db: Session = Depends(get_db)):
    """
    Automatically dispatch an order to the best available courier.

    Algorithm:
    - Phase 1: Search within 2km radius
    - Phase 2: If no match, expand to 5km radius
    - VIP orders prioritize VIP couriers
    - Tags must match order requirements
    """
    success, message, courier_id = auto_dispatch_order(db, order_id)
    return DispatchResult(
        success=success,
        message=message,
        order_id=order_id,
        courier_id=courier_id
    )


@router.post("/manual", response_model=DispatchResult)
def dispatch_order_manual(assign: DispatchAssign, db: Session = Depends(get_db)):
    """
    Manually assign a specific courier to an order.

    Used when operator wants to override automatic dispatch.
    """
    success, message = manual_dispatch_order(db, assign.order_id, assign.courier_id)
    return DispatchResult(
        success=success,
        message=message,
        order_id=assign.order_id,
        courier_id=assign.courier_id if success else None
    )


@router.get("/available-couriers/{order_id}")
def get_couriers_for_order(
    order_id: int,
    radius_km: float = 10.0,
    db: Session = Depends(get_db)
):
    """
    Get list of available couriers suitable for an order.

    Returns couriers sorted by distance, with VIP couriers prioritized for VIP orders.
    Useful for manual dispatch selection.
    """
    couriers = get_available_couriers_for_order(db, order_id, radius_km)
    if not couriers:
        return {
            "order_id": order_id,
            "radius_km": radius_km,
            "couriers": [],
            "message": "No available couriers found"
        }
    return {
        "order_id": order_id,
        "radius_km": radius_km,
        "couriers": couriers,
        "count": len(couriers)
    }


@router.get("/logs/order/{order_id}", response_model=List[DispatchLogResponse])
def get_dispatch_logs_for_order(order_id: int, db: Session = Depends(get_db)):
    """Get dispatch history for an order."""
    return dispatch_log_crud.get_dispatch_logs_for_order(db, order_id)


@router.get("/logs/courier/{courier_id}", response_model=List[DispatchLogResponse])
def get_dispatch_logs_for_courier(courier_id: int, db: Session = Depends(get_db)):
    """Get dispatch history for a courier."""
    return dispatch_log_crud.get_dispatch_logs_for_courier(db, courier_id)
