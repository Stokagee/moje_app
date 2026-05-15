"""API endpoints for order management.

This module provides the complete order lifecycle:
create, dispatch, pickup, deliver, cancel.

SECURITY:
- All endpoints require an OAuth2 Bearer token (PKCE flow)
- pickup/deliver require the "courier" or "admin" role
- delete requires the "admin" role
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
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
from app.core.auth import (
    get_current_user,
    get_current_courier,
    get_current_admin,
    CurrentUser
)
from app.core.csrf import validate_csrf_or_raise
from app.core.config import settings


from app.database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="""
Creates a new order in the system.

## What happens
1. A new order record is created
2. The order starts in `CREATED` status
3. It waits for a courier assignment (dispatch)

## Next steps
To assign a courier, call `POST /dispatch/auto/{order_id}`.

## GPS coordinates
- **pickup_lat/pickup_lng** - Pickup location (restaurant)
- **delivery_lat/delivery_lng** - Delivery location (customer)

## VIP orders
Set `is_vip: true` for priority processing.
VIP orders prefer couriers with the `vip` tag.

## Courier requirements (tags)
The `required_tags` field specifies what specializations the courier must have.
E.g. `["fragile_ok"]` means the courier must have the `fragile_ok` tag.

## Example
```json
{
    "customer_name": "Marie Svobodová",
    "customer_phone": "+420606123456",
    "pickup_address": "Restaurace U Malířů, Národní 25",
    "pickup_lat": 50.0815,
    "pickup_lng": 14.4195,
    "delivery_address": "Vinohradská 50, Praha 2",
    "delivery_lat": 50.0755,
    "delivery_lng": 14.4378,
    "is_vip": false,
    "required_tags": []
}
```
    """,
    responses={
        201: {
            "description": "Order created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 42,
                        "customer_name": "Marie Svobodová",
                        "customer_phone": "+420606123456",
                        "pickup_address": "Národní 25, Praha 1",
                        "pickup_lat": 50.0815,
                        "pickup_lng": 14.4195,
                        "delivery_address": "Vinohradská 50, Praha 2",
                        "delivery_lat": 50.0755,
                        "delivery_lng": 14.4378,
                        "is_vip": False,
                        "required_tags": [],
                        "status": "CREATED",
                        "courier_id": None,
                        "created_at": "2024-01-15T12:00:00",
                        "updated_at": None
                    }
                }
            }
        },
        422: {
            "description": "Invalid data format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "customer_phone"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Creates a new order. Requires authentication."""
    return order_crud.create_order(db, order)


@router.get(
    "/",
    response_model=List[OrderResponse],
    summary="Get list of all orders",
    description="""
Returns a paginated list of all orders in the system.

## Parameters
- `skip` - Number of records to skip
- `limit` - Maximum number of records to return

## Ordering
Orders are sorted by creation date (newest first).

## Tip
To filter by status, use `/orders/by-status/{status}`.
    """,
    responses={
        200: {
            "description": "List of orders"
        }
    }
)
def get_orders(
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max number of records"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Returns a list of all orders. Requires authentication."""
    return order_crud.get_orders(db, skip=skip, limit=limit)


@router.get(
    "/pending",
    response_model=List[OrderResponse],
    summary="Get orders waiting for a courier",
    description="""
Returns a list of orders in `SEARCHING` status — waiting for a courier assignment.

## When is an order in SEARCHING status?
- After a failed auto dispatch (no courier in range)
- The order is waiting for a retry

## Use cases
- Dispatcher dashboard for manual assignment
- Monitoring unassigned orders
- Alert system for long-waiting orders
    """,
    responses={
        200: {
            "description": "List of pending orders"
        }
    }
)
def get_pending_orders(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Returns orders waiting for courier assignment. Requires authentication."""
    return order_crud.get_pending_orders(db)


@router.get(
    "/by-status/{status}",
    response_model=List[OrderResponse],
    summary="Get orders by status",
    description="""
Returns a list of all orders in the given status.

## Possible statuses

| Status | Description |
|--------|-------------|
| `CREATED` | Newly created, waiting for dispatch |
| `SEARCHING` | Looking for a courier |
| `ASSIGNED` | Courier assigned, heading to pickup |
| `PICKED` | Courier picked up the parcel |
| `DELIVERED` | Delivered to customer |
| `CANCELLED` | Cancelled |

## Examples
- `/orders/by-status/ASSIGNED` - Active orders with a courier
- `/orders/by-status/DELIVERED` - Completed orders
- `/orders/by-status/CANCELLED` - Cancelled orders
    """,
    responses={
        200: {
            "description": "List of orders in the given status"
        }
    }
)
def get_orders_by_status(
    status: OrderStatus = Path(..., description="Order status to filter by"),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max number of records"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Returns orders filtered by status. Requires authentication."""
    return order_crud.get_orders_by_status(db, status, skip=skip, limit=limit)


@router.get(
    "/{order_id}",
    response_model=OrderWithCourier,
    summary="Get order detail",
    description="""
Returns complete information about an order including the assigned courier details.

## Returned information
- All order data (customer, addresses, GPS)
- Current status
- Courier ID + name and phone (if assigned)
- Timestamps

## Use cases
- Tracking order status
- Displaying courier contact
- Customer detail view

## Errors
- **404 Not Found** - Order does not exist
    """,
    responses={
        200: {
            "description": "Order detail with courier"
        },
        404: {
            "description": "Order not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
def get_order(
    order_id: int = Path(..., ge=1, description="Order ID"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Returns order detail including courier. Requires authentication."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    response = OrderWithCourier.model_validate(order)
    if order.courier_id:
        courier = courier_crud.get_courier(db, order.courier_id)
        if courier:
            response.courier_name = courier.name
            response.courier_phone = courier.phone

    return response


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status (admin)",
    description="""
Administrative endpoint for directly changing an order's status.

## Note
For normal operations use the dedicated endpoints:
- `/orders/{id}/pickup` - Courier picked up
- `/orders/{id}/deliver` - Courier delivered
- `/orders/{id}/cancel` - Cancellation

This endpoint is intended for **exceptional situations** and corrections.

## Errors
- **404 Not Found** - Order does not exist
    """,
    responses={
        200: {
            "description": "Status updated"
        },
        404: {
            "description": "Order not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
def update_order_status(
    order_id: int = Path(..., ge=1, description="Order ID"),
    status_update: OrderStatusUpdate = ...,
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(get_current_admin)
):
    """Updates order status (administrative operation). Requires admin role."""
    updated = order_crud.update_order_status(db, order_id, status_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return updated


@router.post(
    "/{order_id}/pickup",
    response_model=OrderResponse,
    summary="Mark order as picked up",
    description="""
The courier marks that they have picked up the order from the restaurant/shop.

## What happens
1. Status changes from `ASSIGNED` to `PICKED`
2. The courier is now transporting the parcel to the customer

## Prerequisites
- Order must be in `ASSIGNED` status
- A courier must be assigned

## Next step
After delivery, call `POST /orders/{id}/deliver`.

## Errors
- **404 Not Found** - Order does not exist
- **400 Bad Request** - Order is not in ASSIGNED status
    """,
    responses={
        200: {
            "description": "Order marked as picked up",
            "content": {
                "application/json": {
                    "example": {
                        "id": 42,
                        "status": "PICKED",
                        "courier_id": 5
                    }
                }
            }
        },
        400: {
            "description": "Invalid status for pickup",
            "content": {
                "application/json": {
                    "example": {"detail": "Order cannot be picked up (status: CREATED)"}
                }
            }
        },
        404: {
            "description": "Order not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
async def mark_order_picked(
    order_id: int = Path(..., ge=1, description="Order ID"),
    db: Session = Depends(get_db),
    courier: CurrentUser = Depends(get_current_courier)
):
    """Marks the order as picked up by the courier. Requires courier role and ownership."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Kontrola vlastnictví - kurýr může vyzvednout jen své objednávky
    if courier.role != "admin" and order.courier_id != courier.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only pickup orders assigned to you"
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


@router.post(
    "/{order_id}/deliver",
    response_model=OrderResponse,
    summary="Mark order as delivered",
    description="""
The courier marks that they have delivered the order to the customer.

## What happens
1. Status changes from `PICKED` to `DELIVERED`
2. The courier automatically returns to `available` status
3. The courier can accept another order

## Prerequisites
- Order must be in `PICKED` status

## Note
This is the **final status** of an order. After delivery the status cannot be changed.

## Errors
- **404 Not Found** - Order does not exist
- **400 Bad Request** - Order is not in PICKED status
    """,
    responses={
        200: {
            "description": "Order delivered",
            "content": {
                "application/json": {
                    "example": {
                        "id": 42,
                        "status": "DELIVERED",
                        "courier_id": 5
                    }
                }
            }
        },
        400: {
            "description": "Invalid status for delivery",
            "content": {
                "application/json": {
                    "example": {"detail": "Order cannot be delivered (status: ASSIGNED)"}
                }
            }
        },
        404: {
            "description": "Order not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
async def mark_order_delivered(
    order_id: int = Path(..., ge=1, description="Order ID"),
    db: Session = Depends(get_db),
    courier: CurrentUser = Depends(get_current_courier)
):
    """Marks the order as delivered. Requires courier role and ownership."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Kontrola vlastnictví - kurýr může doručit jen své objednávky
    if courier.role != "admin" and order.courier_id != courier.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only deliver orders assigned to you"
        )

    if order.status != OrderStatus.PICKED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be delivered (status: {order.status})"
        )

    updated_order = order_crud.update_order_status(
        db, order_id,
        OrderStatusUpdate(status=OrderStatus.DELIVERED)
    )

    # Uvolnit kurýra
    if order.courier_id:
        from app.schemas.courier import CourierStatusUpdate
        from app.models.courier import CourierStatus
        courier_crud.update_courier_status(
            db, order.courier_id,
            CourierStatusUpdate(status=CourierStatus.available)
        )

    return updated_order


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel an order",
    description="""
Cancels an order and releases the courier (if assigned).

## What happens
1. Status changes to `CANCELLED`
2. If a courier was assigned, they return to `available`
3. The order is terminated

## When can an order be cancelled
- `CREATED` - Yes
- `SEARCHING` - Yes
- `ASSIGNED` - Yes (courier is released)
- `PICKED` - Yes (courier is released)
- `DELIVERED` - **No** (already delivered)
- `CANCELLED` - **No** (already cancelled)

## Reasons for cancellation
- Customer changed their mind
- Restaurant cannot prepare the order
- Technical issue

## Errors
- **404 Not Found** - Order does not exist
- **400 Bad Request** - Order cannot be cancelled (DELIVERED/CANCELLED)
    """,
    responses={
        200: {
            "description": "Order cancelled",
            "content": {
                "application/json": {
                    "example": {
                        "id": 42,
                        "status": "CANCELLED",
                        "courier_id": 5
                    }
                }
            }
        },
        400: {
            "description": "Order cannot be cancelled",
            "content": {
                "application/json": {
                    "example": {"detail": "Order cannot be cancelled (status: DELIVERED)"}
                }
            }
        },
        404: {
            "description": "Order not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
async def cancel_order(
    order_id: int = Path(..., ge=1, description="Order ID"),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Cancels an order. Requires authentication."""
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

    # Uvolnit kurýra pokud byl přiřazen
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


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an order",
    description="""
Permanently deletes an order from the system.

## Warning
- This action is **irreversible**!
- Use only for testing or error correction
- For normal order termination use `/orders/{id}/cancel`

## Recommendation
In production, do not delete orders — they serve as history and reporting data.

## Errors
- **404 Not Found** - Order does not exist
    """,
    responses={
        204: {
            "description": "Order deleted"
        },
        404: {
            "description": "Order not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
async def delete_order(
    order_id: int = Path(..., ge=1, description="Order ID"),
    db: Session = Depends(get_db),
    admin: CurrentUser = Depends(get_current_admin)
):
    """Deletes an order (admin only). Requires admin role."""
    deleted = order_crud.delete_order(db, order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return None
