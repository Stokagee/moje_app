"""Dispatch Pydantic schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DispatchAssign(BaseModel):
    """Schema for manual dispatch assignment."""
    order_id: int
    courier_id: int


class DispatchLogResponse(BaseModel):
    """Schema for dispatch log response."""
    id: int
    order_id: int
    courier_id: int
    action: str
    created_at: datetime

    class Config:
        from_attributes = True


class DispatchResult(BaseModel):
    """Schema for dispatch operation result."""
    success: bool
    message: str
    order_id: int
    courier_id: Optional[int] = None
