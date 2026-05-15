"""Pydantic schemas for orders.

This module defines data structures for working with orders in the API.
An order represents a delivery request from a pickup location to a customer.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus


class OrderBase(BaseModel):
    """Base order attributes shared by create and response schemas."""

    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the customer receiving the order",
        json_schema_extra={"example": "Marie Svobodová"}
    )
    customer_phone: str = Field(
        ...,
        min_length=9,
        max_length=20,
        description="Customer phone number for contact during delivery",
        json_schema_extra={"example": "+420606123456"}
    )
    pickup_address: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Pickup address (restaurant, shop)",
        json_schema_extra={"example": "Národní 25, Praha 1"}
    )
    pickup_lat: float = Field(
        ...,
        ge=-90,
        le=90,
        description="GPS latitude of the pickup point",
        json_schema_extra={"example": 50.0815}
    )
    pickup_lng: float = Field(
        ...,
        ge=-180,
        le=180,
        description="GPS longitude of the pickup point",
        json_schema_extra={"example": 14.4195}
    )
    delivery_address: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Delivery address to the customer",
        json_schema_extra={"example": "Vinohradská 50, Praha 2"}
    )
    delivery_lat: float = Field(
        ...,
        ge=-90,
        le=90,
        description="GPS latitude of the delivery point",
        json_schema_extra={"example": 50.0755}
    )
    delivery_lng: float = Field(
        ...,
        ge=-180,
        le=180,
        description="GPS longitude of the delivery point",
        json_schema_extra={"example": 14.4378}
    )
    is_vip: bool = Field(
        default=False,
        description="""VIP flag for the order.

        VIP orders have priority during courier assignment:
        - Couriers with the `vip` tag are preferred
        - If no VIP courier is available, a regular courier is assigned
        """,
        json_schema_extra={"example": False}
    )
    required_tags: List[str] = Field(
        default=[],
        description="""List of tags the courier must have for this order.

        Common tags:
        - `fragile_ok` - order contains fragile items
        - `fast` - express delivery
        - `bike` / `car` - specific transport type

        The courier MUST have ALL required tags to be able to take the order.
        """,
        json_schema_extra={"example": ["fragile_ok"]}
    )


class OrderCreate(OrderBase):
    """Schema for creating a new order.

    After creation the order is in `CREATED` status.
    To assign a courier use the `/dispatch/auto/{order_id}` endpoint.

    ## Order lifecycle

    1. **CREATED** - Order created, waiting for dispatch
    2. **SEARCHING** - Looking for a suitable courier
    3. **ASSIGNED** - Courier assigned, heading to pickup
    4. **PICKED** - Courier picked up the order
    5. **DELIVERED** - Delivered to the customer
    6. **CANCELLED** - Order cancelled (can happen any time before DELIVERED)

    ## Creation example

    ```json
    {
        "customer_name": "Marie Svobodová",
        "customer_phone": "+420606123456",
        "pickup_address": "Národní 25, Praha 1",
        "pickup_lat": 50.0815,
        "pickup_lng": 14.4195,
        "delivery_address": "Vinohradská 50, Praha 2",
        "delivery_lat": 50.0755,
        "delivery_lng": 14.4378,
        "is_vip": false,
        "required_tags": []
    }
    ```
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_name": "Marie Svobodová",
                "customer_phone": "+420606123456",
                "pickup_address": "Národní 25, Praha 1",
                "pickup_lat": 50.0815,
                "pickup_lng": 14.4195,
                "delivery_address": "Vinohradská 50, Praha 2",
                "delivery_lat": 50.0755,
                "delivery_lng": 14.4378,
                "is_vip": False,
                "required_tags": []
            }
        }
    )


class OrderStatusUpdate(BaseModel):
    """Schema for manually changing an order's status.

    ## Possible statuses

    | Status | Description | Next status |
    |--------|-------------|-------------|
    | `CREATED` | Newly created | SEARCHING |
    | `SEARCHING` | Looking for courier | ASSIGNED |
    | `ASSIGNED` | Courier assigned | PICKED |
    | `PICKED` | Picked up | DELIVERED |
    | `DELIVERED` | Delivered | - (final) |
    | `CANCELLED` | Cancelled | - (final) |

    ## Note

    For normal operations use the dedicated endpoints:
    - `/orders/{id}/pickup` - to mark pickup
    - `/orders/{id}/deliver` - to mark delivery
    - `/orders/{id}/cancel` - to cancel

    This endpoint is intended for administrative purposes.
    """

    status: OrderStatus = Field(
        ...,
        description="New order status",
        json_schema_extra={"example": "ASSIGNED"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ASSIGNED"
            }
        }
    )


class OrderResponse(OrderBase):
    """Complete response with order data.

    Returned on GET operations and after creating/updating an order.

    ## Example response

    ```json
    {
        "id": 42,
        "customer_name": "Marie Svobodová",
        "customer_phone": "+420606123456",
        "pickup_address": "Národní 25, Praha 1",
        "pickup_lat": 50.0815,
        "pickup_lng": 14.4195,
        "delivery_address": "Vinohradská 50, Praha 2",
        "delivery_lat": 50.0755,
        "delivery_lng": 14.4378,
        "is_vip": false,
        "required_tags": [],
        "status": "ASSIGNED",
        "courier_id": 5,
        "created_at": "2024-01-15T12:00:00",
        "updated_at": "2024-01-15T12:05:00"
    }
    ```
    """

    id: int = Field(
        ...,
        description="Unique order identifier",
        json_schema_extra={"example": 42}
    )
    status: OrderStatus = Field(
        ...,
        description="Current order status",
        json_schema_extra={"example": "ASSIGNED"}
    )
    courier_id: Optional[int] = Field(
        default=None,
        description="ID of the assigned courier (null if not yet assigned)",
        json_schema_extra={"example": 5}
    )
    created_at: datetime = Field(
        ...,
        description="Date and time the order was created",
        json_schema_extra={"example": "2024-01-15T12:00:00"}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Date and time of the last status change",
        json_schema_extra={"example": "2024-01-15T12:05:00"}
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
                "status": "ASSIGNED",
                "courier_id": 5,
                "created_at": "2024-01-15T12:00:00",
                "updated_at": "2024-01-15T12:05:00"
            }
        }
    )


class OrderWithCourier(OrderResponse):
    """Extended response with assigned courier details.

    Returned on GET for a single order (`/orders/{id}`).
    Includes the courier's name and phone for easier display in the UI.

    ## Example response

    ```json
    {
        "id": 42,
        "customer_name": "Marie Svobodová",
        "customer_phone": "+420606123456",
        "pickup_address": "Národní 25, Praha 1",
        "pickup_lat": 50.0815,
        "pickup_lng": 14.4195,
        "delivery_address": "Vinohradská 50, Praha 2",
        "delivery_lat": 50.0755,
        "delivery_lng": 14.4378,
        "is_vip": false,
        "required_tags": [],
        "status": "ASSIGNED",
        "courier_id": 5,
        "courier_name": "Jan Novák",
        "courier_phone": "+420777123456",
        "created_at": "2024-01-15T12:00:00",
        "updated_at": "2024-01-15T12:05:00"
    }
    ```
    """

    courier_name: Optional[str] = Field(
        default=None,
        description="Name of the assigned courier (null if not assigned)",
        json_schema_extra={"example": "Jan Novák"}
    )
    courier_phone: Optional[str] = Field(
        default=None,
        description="Phone of the assigned courier (null if not assigned)",
        json_schema_extra={"example": "+420777123456"}
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
                "status": "ASSIGNED",
                "courier_id": 5,
                "courier_name": "Jan Novák",
                "courier_phone": "+420777123456",
                "created_at": "2024-01-15T12:00:00",
                "updated_at": "2024-01-15T12:05:00"
            }
        }
    )
