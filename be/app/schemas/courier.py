"""Courier Pydantic schemas."""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.courier import CourierStatus


class CourierBase(BaseModel):
    """Base courier schema."""
    name: str
    phone: str
    email: EmailStr
    tags: List[str] = []


class CourierCreate(CourierBase):
    """Schema for creating a courier."""
    pass


class CourierUpdate(BaseModel):
    """Schema for updating a courier."""
    name: Optional[str] = None
    phone: Optional[str] = None
    tags: Optional[List[str]] = None


class CourierLocationUpdate(BaseModel):
    """Schema for updating courier GPS location."""
    lat: float
    lng: float


class CourierStatusUpdate(BaseModel):
    """Schema for updating courier status."""
    status: CourierStatus


class CourierResponse(CourierBase):
    """Schema for courier response."""
    id: int
    lat: Optional[float] = None
    lng: Optional[float] = None
    status: CourierStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourierOfferResponse(BaseModel):
    """Schema for courier responding to offer."""
    accept: bool
