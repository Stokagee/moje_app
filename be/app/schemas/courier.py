"""Pydantic schemas for couriers.

This module defines data structures for working with couriers in the API.
A courier is a person who delivers orders to customers.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.courier import CourierStatus


class CourierBase(BaseModel):
    """Base courier attributes shared by create and response schemas."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the courier",
        json_schema_extra={"example": "Jan Novák"}
    )
    phone: str = Field(
        ...,
        min_length=9,
        max_length=20,
        description="Courier phone number in international format",
        json_schema_extra={"example": "+420777123456"}
    )
    email: EmailStr = Field(
        ...,
        description="Courier e-mail address (must be unique in the system)",
        json_schema_extra={"example": "jan.novak@example.cz"}
    )
    tags: List[str] = Field(
        default=[],
        description="""List of courier tags/specializations. Common tags:
        - `bike` - rides a bicycle
        - `car` - has a car
        - `vip` - preferred for VIP orders
        - `fragile_ok` - can transport fragile items
        - `fast` - express delivery
        """,
        json_schema_extra={"example": ["bike", "vip"]}
    )


class CourierCreate(CourierBase):
    """Schema for creating a new courier.

    After creation the courier is in `offline` status with no GPS location.
    To activate, set the location and change status to `available`.

    ## Usage example

    ```json
    {
        "name": "Jan Novák",
        "phone": "+420777123456",
        "email": "jan.novak@example.cz",
        "tags": ["bike", "vip"]
    }
    ```
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jan Novák",
                "phone": "+420777123456",
                "email": "jan.novak@example.cz",
                "tags": ["bike", "vip"]
            }
        }
    )


class CourierUpdate(BaseModel):
    """Schema for updating courier data.

    All fields are optional — send only the ones you want to change.
    E-mail cannot be changed (it is the unique identifier).

    ## Example - change name and tags

    ```json
    {
        "name": "Jan Novák Jr.",
        "tags": ["car", "vip", "fragile_ok"]
    }
    ```
    """

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="New courier name",
        json_schema_extra={"example": "Jan Novák Jr."}
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=9,
        max_length=20,
        description="New phone number",
        json_schema_extra={"example": "+420777999888"}
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="New list of tags (replaces the existing list)",
        json_schema_extra={"example": ["car", "vip"]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jan Novák Jr.",
                "tags": ["car", "vip"]
            }
        }
    )


class CourierLocationUpdate(BaseModel):
    """Schema for updating the courier's GPS location.

    This should be called regularly from the courier's mobile app
    to track their position in real time.

    ## Coordinates

    - `lat` (latitude) - geographic latitude (-90 to 90)
    - `lng` (longitude) - geographic longitude (-180 to 180)

    ## Example - Prague city centre

    ```json
    {
        "lat": 50.0755,
        "lng": 14.4378
    }
    ```
    """

    lat: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Geographic latitude - WGS84",
        json_schema_extra={"example": 50.0755}
    )
    lng: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Geographic longitude - WGS84",
        json_schema_extra={"example": 14.4378}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lat": 50.0755,
                "lng": 14.4378
            }
        }
    )


class CourierStatusUpdate(BaseModel):
    """Schema for changing the courier's status.

    ## Possible statuses

    | Status | Description | Can accept orders |
    |--------|-------------|-------------------|
    | `offline` | Courier is not available | No |
    | `available` | Courier is free and waiting for an order | Yes |
    | `busy` | Courier is currently delivering | No |

    ## Status transitions

    - `offline` → `available`: Courier logged into their shift
    - `available` → `busy`: Courier accepted an order (automatic during dispatch)
    - `busy` → `available`: Courier completed delivery (automatic)
    - `available` → `offline`: Courier ended their shift
    - `busy` → `offline`: Not allowed! Must complete the order first

    ## Example

    ```json
    {
        "status": "available"
    }
    ```
    """

    status: CourierStatus = Field(
        ...,
        description="New courier status: offline, available, or busy",
        json_schema_extra={"example": "available"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "available"
            }
        }
    )


class CourierResponse(CourierBase):
    """Complete response with courier data.

    Returned on GET operations and after creating/updating a courier.
    Includes all attributes including ID, status, and GPS location.

    ## Example response

    ```json
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
    ```
    """

    id: int = Field(
        ...,
        description="Unique courier identifier in the database",
        json_schema_extra={"example": 1}
    )
    lat: Optional[float] = Field(
        default=None,
        description="Current latitude (null if GPS is not set)",
        json_schema_extra={"example": 50.0755}
    )
    lng: Optional[float] = Field(
        default=None,
        description="Current longitude (null if GPS is not set)",
        json_schema_extra={"example": 14.4378}
    )
    status: CourierStatus = Field(
        ...,
        description="Current courier status",
        json_schema_extra={"example": "available"}
    )
    created_at: datetime = Field(
        ...,
        description="Date and time the record was created",
        json_schema_extra={"example": "2024-01-15T10:30:00"}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Date and time of the last update",
        json_schema_extra={"example": "2024-01-15T14:45:00"}
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
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
        }
    )


class CourierOfferResponse(BaseModel):
    """Schema for the courier's response to an order offer.

    Used when the courier manually confirms acceptance of an order.

    ## Example - accepting an order

    ```json
    {
        "accept": true
    }
    ```
    """

    accept: bool = Field(
        ...,
        description="True if the courier accepts the order, False if they decline",
        json_schema_extra={"example": True}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "accept": True
            }
        }
    )
