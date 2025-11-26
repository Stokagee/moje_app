"""Order Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus


class OrderBase(BaseModel):
    """Base order schema."""
    customer_name: str
    customer_phone: str
    pickup_address: str
    pickup_lat: float
    pickup_lng: float
    delivery_address: str
    delivery_lat: float
    delivery_lng: float
    is_vip: bool = False
    required_tags: List[str] = []


class OrderCreate(OrderBase):
    """Schema for creating an order."""
    pass


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus


class OrderResponse(OrderBase):
    """Schema for order response."""
    id: int
    status: OrderStatus
    courier_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderWithCourier(OrderResponse):
    """Schema for order with courier details."""
    courier_name: Optional[str] = None
    courier_phone: Optional[str] = None
