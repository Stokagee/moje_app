"""Order API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    OrderWithCourier
)
from app.models.order import OrderStatus
from app.crud import order as order_crud
from app.crud import courier as courier_crud

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order."""
    return order_crud.create_order(db, order)


@router.get("/", response_model=List[OrderResponse])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all orders."""
    return order_crud.get_orders(db, skip=skip, limit=limit)


@router.get("/pending", response_model=List[OrderResponse])
def get_pending_orders(db: Session = Depends(get_db)):
    """Get orders waiting for courier assignment (SEARCHING status)."""
    return order_crud.get_pending_orders(db)


@router.get("/by-status/{status}", response_model=List[OrderResponse])
def get_orders_by_status(status: OrderStatus, db: Session = Depends(get_db)):
    """Get orders by status."""
    return order_crud.get_orders_by_status(db, status)


@router.get("/{order_id}", response_model=OrderWithCourier)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get order by ID with courier details."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Add courier details if assigned
    response = OrderWithCourier.model_validate(order)
    if order.courier_id:
        courier = courier_crud.get_courier(db, order.courier_id)
        if courier:
            response.courier_name = courier.name
            response.courier_phone = courier.phone

    return response


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update order status."""
    updated = order_crud.update_order_status(db, order_id, status_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return updated


@router.post("/{order_id}/pickup", response_model=OrderResponse)
def mark_order_picked(order_id: int, db: Session = Depends(get_db)):
    """Mark order as picked up by courier."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status != OrderStatus.ASSIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be picked up (status: {order.status})"
        )

    return order_crud.update_order_status(
        db, order_id,
        OrderStatusUpdate(status=OrderStatus.PICKED)
    )


@router.post("/{order_id}/deliver", response_model=OrderResponse)
def mark_order_delivered(order_id: int, db: Session = Depends(get_db)):
    """Mark order as delivered."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status != OrderStatus.PICKED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be delivered (status: {order.status})"
        )

    # Update order status
    updated_order = order_crud.update_order_status(
        db, order_id,
        OrderStatusUpdate(status=OrderStatus.DELIVERED)
    )

    # Free up the courier
    if order.courier_id:
        from app.schemas.courier import CourierStatusUpdate
        from app.models.courier import CourierStatus
        courier_crud.update_courier_status(
            db, order.courier_id,
            CourierStatusUpdate(status=CourierStatus.available)
        )

    return updated_order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel an order."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be cancelled (status: {order.status})"
        )

    # Free up courier if assigned
    if order.courier_id and order.status in [OrderStatus.ASSIGNED, OrderStatus.PICKED]:
        from app.schemas.courier import CourierStatusUpdate
        from app.models.courier import CourierStatus
        courier_crud.update_courier_status(
            db, order.courier_id,
            CourierStatusUpdate(status=CourierStatus.available)
        )

    return order_crud.update_order_status(
        db, order_id,
        OrderStatusUpdate(status=OrderStatus.CANCELLED)
    )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order."""
    deleted = order_crud.delete_order(db, order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return None
