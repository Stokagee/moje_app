"""API endpoints for dispatch.

This module handles assigning couriers to orders.
Supports automatic dispatch (algorithm) and manual dispatch (operator).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
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


@router.post(
    "/auto/{order_id}",
    response_model=DispatchResult,
    summary="Auto-assign a courier to an order",
    description="""
Automatically finds and assigns the nearest suitable courier to an order.

## How the algorithm works

### Step 1: Find candidates
- Selects all couriers in `available` status
- Must have a valid GPS location

### Step 2: Filter by tags
- If the order has `required_tags`, the courier must have **all** of those tags
- E.g. order requires `["fragile_ok", "bike"]` → courier must have both

### Step 3: VIP priority
- For VIP orders (`is_vip: true`), the algorithm first tries to find a courier with the `vip` tag
- If no VIP courier is available, a regular courier is used

### Step 4: Phased search
1. **Phase 1 (750 km)**: Looks for couriers within 750 km of the pickup point
2. **Phase 2 (1500 km)**: If none found within 750 km, expands to 1500 km

### Step 5: Select nearest
- From all candidates in range, selects the **nearest** one
- Distance is calculated using the Haversine formula (GPS)

## On success
1. Order moves to `ASSIGNED` status
2. Courier moves to `busy` status
3. A record is created in the dispatch log

## On failure
1. Order moves to `SEARCHING` status
2. Returns `success: false` with a reason
3. You can retry later or use manual dispatch

## Example responses

### Success
```json
{
    "success": true,
    "message": "Courier Jan Novák assigned (distance: 1.2 km)",
    "order_id": 42,
    "courier_id": 5
}
```

### Failure - no courier in range
```json
{
    "success": false,
    "message": "No available courier found within 1500km radius",
    "order_id": 42,
    "courier_id": null
}
```

### Failure - missing tags
```json
{
    "success": false,
    "message": "No courier with required tags: fragile_ok",
    "order_id": 42,
    "courier_id": null
}
```

## Errors
- **Order not found** - `success: false`, message contains "not found"
- **Order already assigned** - `success: false`, message contains "cannot be dispatched"
    """,
    responses={
        200: {
            "description": "Dispatch operation result",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful dispatch",
                            "value": {
                                "success": True,
                                "message": "Courier Jan Novák assigned (distance: 1.2 km)",
                                "order_id": 42,
                                "courier_id": 5
                            }
                        },
                        "no_courier": {
                            "summary": "No courier in range",
                            "value": {
                                "success": False,
                                "message": "No available courier found within 5km radius",
                                "order_id": 42,
                                "courier_id": None
                            }
                        },
                        "wrong_state": {
                            "summary": "Order in invalid status",
                            "value": {
                                "success": False,
                                "message": "Order 42 cannot be dispatched (status: DELIVERED)",
                                "order_id": 42,
                                "courier_id": None
                            }
                        }
                    }
                }
            }
        }
    }
)
def dispatch_order_auto(
    order_id: int = Path(..., ge=1, description="Order ID to dispatch"),
    db: Session = Depends(get_db)
):
    """Automatically assigns the nearest suitable courier."""
    success, message, courier_id = auto_dispatch_order(db, order_id)
    return DispatchResult(
        success=success,
        message=message,
        order_id=order_id,
        courier_id=courier_id
    )


@router.post(
    "/manual",
    response_model=DispatchResult,
    summary="Manually assign a courier to an order",
    description="""
Manually assigns a specific courier to an order.

## When to use
- Customer requested a specific courier
- Auto dispatch failed and the operator is selecting manually
- Special situation requiring a human decision
- Courier is outside the standard range but can handle the order

## Prerequisites
- Order must be in `CREATED` or `SEARCHING` status
- Courier must be in `available` status
- Courier must have all required tags for the order

## What is validated
1. Order exists and is in a dispatchable status
2. Courier exists and is available
3. Courier has all required tags

## On success
1. Order moves to `ASSIGNED` status
2. Courier moves to `busy` status
3. A record is created in the dispatch log with action `manual_assigned`

## Example request
```json
{
    "order_id": 42,
    "courier_id": 5
}
```

## Errors
- **Courier not available** - `success: false`
- **Courier missing required tags** - `success: false`
- **Order in invalid status** - `success: false`
    """,
    responses={
        200: {
            "description": "Manual dispatch result",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Successful assignment",
                            "value": {
                                "success": True,
                                "message": "Courier successfully assigned to order",
                                "order_id": 42,
                                "courier_id": 5
                            }
                        },
                        "courier_busy": {
                            "summary": "Courier not available",
                            "value": {
                                "success": False,
                                "message": "Courier 5 is not available (status: busy)",
                                "order_id": 42,
                                "courier_id": None
                            }
                        },
                        "missing_tags": {
                            "summary": "Courier missing required tags",
                            "value": {
                                "success": False,
                                "message": "Courier 5 missing required tags: fragile_ok",
                                "order_id": 42,
                                "courier_id": None
                            }
                        }
                    }
                }
            }
        }
    }
)
def dispatch_order_manual(
    assign: DispatchAssign,
    db: Session = Depends(get_db)
):
    """Manually assigns a specific courier to an order."""
    success, message = manual_dispatch_order(db, assign.order_id, assign.courier_id)
    return DispatchResult(
        success=success,
        message=message,
        order_id=assign.order_id,
        courier_id=assign.courier_id if success else None
    )


@router.get(
    "/available-couriers/{order_id}",
    summary="Get suitable couriers for an order",
    description="""
Returns a list of all couriers who can take the given order.

## What is checked
- Courier is in `available` status
- Courier has a valid GPS location
- Courier has all `required_tags` from the order
- Courier is within the specified radius of the pickup point

## Use cases
- Manual dispatch UI - operator sees candidates
- Displaying couriers on a map
- Decision support before manual assignment

## Parameters
- `order_id` - Order ID
- `radius_km` - Maximum distance in km (default 10)

## Returned data
For each courier:
- Basic info (ID, name, phone)
- Distance from the pickup point
- Whether the courier is VIP
- List of tags

## Ordering
Couriers are sorted by distance (nearest first).
For VIP orders, VIP couriers appear at the top.

## Example response
```json
{
    "order_id": 42,
    "radius_km": 10.0,
    "count": 2,
    "couriers": [
        {
            "courier_id": 5,
            "name": "Jan Novák",
            "phone": "+420777123456",
            "distance_km": 1.2,
            "is_vip_courier": true,
            "tags": ["bike", "vip"]
        },
        {
            "courier_id": 8,
            "name": "Petr Svoboda",
            "phone": "+420666789012",
            "distance_km": 2.5,
            "is_vip_courier": false,
            "tags": ["bike"]
        }
    ]
}
```
    """,
    responses={
        200: {
            "description": "List of available couriers",
            "content": {
                "application/json": {
                    "examples": {
                        "found": {
                            "summary": "Couriers found",
                            "value": {
                                "order_id": 42,
                                "radius_km": 10.0,
                                "count": 2,
                                "couriers": [
                                    {
                                        "courier_id": 5,
                                        "name": "Jan Novák",
                                        "phone": "+420777123456",
                                        "distance_km": 1.2,
                                        "is_vip_courier": True,
                                        "tags": ["bike", "vip"]
                                    }
                                ]
                            }
                        },
                        "empty": {
                            "summary": "No courier found",
                            "value": {
                                "order_id": 42,
                                "radius_km": 10.0,
                                "couriers": [],
                                "message": "No available couriers found"
                            }
                        }
                    }
                }
            }
        }
    }
)
def get_couriers_for_order(
    order_id: int = Path(..., ge=1, description="Order ID"),
    radius_km: float = Query(
        default=10.0,
        ge=0.1,
        le=100.0,
        description="Maximum distance from the pickup point in km"
    ),
    db: Session = Depends(get_db)
):
    """Returns a list of couriers suitable for the given order."""
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


@router.get(
    "/logs/order/{order_id}",
    response_model=List[DispatchLogResponse],
    summary="Get dispatch history for an order",
    description="""
Returns the complete courier assignment history for a given order.

## Use cases
- Audit and debugging
- Displaying history in order detail
- Analysing dispatch problems

## Record types (action)

| Action | Description |
|--------|-------------|
| `auto_assigned` | Courier assigned by the automatic algorithm |
| `manual_assigned` | Courier assigned manually by an operator |
| `auto_failed` | Automatic dispatch failed |
| `rejected` | Courier rejected the order |

## Ordering
Records are sorted from newest to oldest.

## Example response
```json
[
    {
        "id": 456,
        "order_id": 42,
        "courier_id": 5,
        "action": "auto_assigned",
        "created_at": "2024-01-15T12:05:00"
    },
    {
        "id": 455,
        "order_id": 42,
        "courier_id": 3,
        "action": "auto_failed",
        "created_at": "2024-01-15T12:04:30"
    }
]
```
    """,
    responses={
        200: {
            "description": "Dispatch history for the order"
        }
    }
)
def get_dispatch_logs_for_order(
    order_id: int = Path(..., ge=1, description="Order ID"),
    db: Session = Depends(get_db)
):
    """Returns dispatch history for an order."""
    return dispatch_log_crud.get_dispatch_logs_for_order(db, order_id)


@router.get(
    "/logs/courier/{courier_id}",
    response_model=List[DispatchLogResponse],
    summary="Get dispatch history for a courier",
    description="""
Returns the complete order assignment history for a given courier.

## Use cases
- Courier performance analysis
- Overview of completed orders
- Debugging issues with a specific courier

## Record information
- Which orders the courier received
- Whether they were assigned automatically or manually
- Timestamps

## Ordering
Records are sorted from newest to oldest.

## Example response
```json
[
    {
        "id": 456,
        "order_id": 42,
        "courier_id": 5,
        "action": "auto_assigned",
        "created_at": "2024-01-15T12:05:00"
    },
    {
        "id": 400,
        "order_id": 38,
        "courier_id": 5,
        "action": "manual_assigned",
        "created_at": "2024-01-15T10:30:00"
    }
]
```
    """,
    responses={
        200: {
            "description": "Dispatch history for the courier"
        }
    }
)
def get_dispatch_logs_for_courier(
    courier_id: int = Path(..., ge=1, description="Courier ID"),
    db: Session = Depends(get_db)
):
    """Returns dispatch history for a courier."""
    return dispatch_log_crud.get_dispatch_logs_for_courier(db, courier_id)
