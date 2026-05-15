"""API endpoints for courier management.

This module provides CRUD operations and courier status management.
A courier is a person who delivers orders to customers.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
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


@router.post(
    "/",
    response_model=CourierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new courier",
    description="""
Creates a new courier in the system.

## What happens
1. Verifies the e-mail is not already in the system
2. Creates a new courier record
3. Courier starts in `offline` status with no GPS location

## Next steps after creation
- Set GPS location: `PATCH /couriers/{id}/location`
- Activate the courier: `PATCH /couriers/{id}/status` with value `available`

## Errors
- **400 Bad Request** - E-mail already exists in the system
- **422 Unprocessable Entity** - Invalid data format (missing required fields, bad e-mail)
    """,
    responses={
        201: {
            "description": "Courier created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Jan Novák",
                        "phone": "+420777123456",
                        "email": "jan.novak@example.cz",
                        "tags": ["bike", "vip"],
                        "lat": None,
                        "lng": None,
                        "status": "offline",
                        "created_at": "2024-01-15T10:30:00",
                        "updated_at": None
                    }
                }
            }
        },
        400: {
            "description": "E-mail already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier with this email already exists"}
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
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def create_courier(courier: CourierCreate, db: Session = Depends(get_db)):
    """Creates a new courier in the system."""
    existing = courier_crud.get_courier_by_email(db, courier.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Courier with this email already exists"
        )
    return courier_crud.create_courier(db, courier)


@router.get(
    "/",
    response_model=List[CourierResponse],
    summary="Get list of all couriers",
    description="""
Returns a paginated list of all couriers in the system.

## Parameters
- `skip` - Number of records to skip (for pagination)
- `limit` - Maximum number of records to return (max 1000)

## Pagination example
- First page (10 records): `?skip=0&limit=10`
- Second page: `?skip=10&limit=10`
- Third page: `?skip=20&limit=10`

## Ordering
Couriers are sorted by creation date (newest first).
    """,
    responses={
        200: {
            "description": "List of couriers",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Jan Novák",
                            "phone": "+420777123456",
                            "email": "jan.novak@example.cz",
                            "tags": ["bike", "vip"],
                            "lat": 50.0755,
                            "lng": 14.4378,
                            "status": "available",
                            "created_at": "2024-01-15T10:30:00",
                            "updated_at": "2024-01-15T14:45:00"
                        }
                    ]
                }
            }
        }
    }
)
def get_couriers(
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip (pagination offset)"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db)
):
    """Returns a paginated list of all couriers."""
    return courier_crud.get_couriers(db, skip=skip, limit=limit)


@router.get(
    "/available",
    response_model=List[CourierResponse],
    summary="Get list of available couriers",
    description="""
Returns a list of all couriers who are currently **available** to accept an order.

## Criteria for an "available" courier
- Status: `available`
- Has a GPS location set (lat and lng are not null)

## Use cases
- Operator sees who can be assigned to an order
- Dashboard showing active couriers
- Fleet tracking mobile application
    """,
    responses={
        200: {
            "description": "List of available couriers",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Jan Novák",
                            "phone": "+420777123456",
                            "email": "jan.novak@example.cz",
                            "tags": ["bike", "vip"],
                            "lat": 50.0755,
                            "lng": 14.4378,
                            "status": "available",
                            "created_at": "2024-01-15T10:30:00",
                            "updated_at": "2024-01-15T14:45:00"
                        }
                    ]
                }
            }
        }
    }
)
def get_available_couriers(db: Session = Depends(get_db)):
    """Returns a list of all available couriers."""
    return courier_crud.get_available_couriers(db)


@router.get(
    "/{courier_id}",
    response_model=CourierResponse,
    summary="Get courier detail",
    description="""
Returns complete information about one courier by their ID.

## Returned information
- Basic data (name, phone, e-mail)
- Current GPS location
- Current status (offline/available/busy)
- List of tags/specializations
- Timestamps (created, updated)

## Errors
- **404 Not Found** - Courier with the given ID does not exist
    """,
    responses={
        200: {
            "description": "Courier detail"
        },
        404: {
            "description": "Courier not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def get_courier(
    courier_id: int = Path(
        ...,
        ge=1,
        description="Unique courier identifier"
    ),
    db: Session = Depends(get_db)
):
    """Returns courier detail by ID."""
    courier = courier_crud.get_courier(db, courier_id)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return courier


@router.put(
    "/{courier_id}",
    response_model=CourierResponse,
    summary="Update courier data",
    description="""
Updates basic courier data (name, phone, tags).

## What can be changed
- `name` - Courier name
- `phone` - Phone number
- `tags` - List of tags (replaces the existing list)

## What CANNOT be changed
- `email` - E-mail is a unique identifier and cannot be changed

## Note
To change location use `PATCH /couriers/{id}/location`.
To change status use `PATCH /couriers/{id}/status`.

## Errors
- **404 Not Found** - Courier does not exist
    """,
    responses={
        200: {
            "description": "Courier updated successfully"
        },
        404: {
            "description": "Courier not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def update_courier(
    courier_id: int = Path(..., ge=1, description="Courier ID"),
    courier: CourierUpdate = ...,
    db: Session = Depends(get_db)
):
    """Updates basic courier data."""
    updated = courier_crud.update_courier(db, courier_id, courier)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.patch(
    "/{courier_id}/location",
    response_model=CourierResponse,
    summary="Update courier GPS location",
    description="""
Updates the courier's current GPS location.

## When to call
- Regularly from the courier's mobile app (e.g. every 30 seconds)
- After moving more than X metres

## Important
- The courier must have a valid GPS location to be assigned to an order
- Distance is calculated from the order's pickup point

## Coordinate format
- Latitude: -90 to 90 (Prague is approx. 50.08)
- Longitude: -180 to 180 (Prague is approx. 14.42)

## Errors
- **404 Not Found** - Courier does not exist
- **422 Unprocessable Entity** - Invalid coordinates
    """,
    responses={
        200: {
            "description": "Location updated"
        },
        404: {
            "description": "Courier not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def update_courier_location(
    courier_id: int = Path(..., ge=1, description="Courier ID"),
    location: CourierLocationUpdate = ...,
    db: Session = Depends(get_db)
):
    """Updates the courier's GPS location."""
    updated = courier_crud.update_courier_location(db, courier_id, location)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.patch(
    "/{courier_id}/status",
    response_model=CourierResponse,
    summary="Change courier status",
    description="""
Changes the courier's operational status.

## Possible statuses

| Status | Description | Can accept orders |
|--------|-------------|-------------------|
| `offline` | Courier is not working | No |
| `available` | Courier is free | Yes |
| `busy` | Courier is delivering | No |

## Typical transitions
- **Start of shift**: `offline` → `available`
- **End of shift**: `available` → `offline`
- **Order assignment**: `available` → `busy` (automatic)
- **Delivery completed**: `busy` → `available` (automatic)

## Note
- `busy` status is usually set automatically during dispatch
- Status changes to `available` automatically after delivery is completed

## Errors
- **404 Not Found** - Courier does not exist
    """,
    responses={
        200: {
            "description": "Status updated"
        },
        404: {
            "description": "Courier not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def update_courier_status(
    courier_id: int = Path(..., ge=1, description="Courier ID"),
    status_update: CourierStatusUpdate = ...,
    db: Session = Depends(get_db)
):
    """Changes the courier's operational status."""
    updated = courier_crud.update_courier_status(db, courier_id, status_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.delete(
    "/{courier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a courier",
    description="""
Permanently deletes a courier from the system.

## Warning
- This action is **irreversible**!
- The courier should not have active orders (`busy` status)
- Order history will be preserved

## Recommendation
Instead of deleting, consider setting the status to `offline` to deactivate.

## Errors
- **404 Not Found** - Courier does not exist
    """,
    responses={
        204: {
            "description": "Courier deleted"
        },
        404: {
            "description": "Courier not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def delete_courier(
    courier_id: int = Path(..., ge=1, description="Courier ID"),
    db: Session = Depends(get_db)
):
    """Deletes a courier from the system."""
    deleted = courier_crud.delete_courier(db, courier_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return None
