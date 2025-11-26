"""Courier model for Food Delivery system."""
from sqlalchemy import Column, Integer, String, Float, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class CourierStatus(str, enum.Enum):
    """Courier availability status."""
    available = "available"
    busy = "busy"
    offline = "offline"


class Courier(Base):
    """Courier model - delivery person."""
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # GPS location
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    # Status and capabilities
    status = Column(Enum(CourierStatus), default=CourierStatus.offline, nullable=False)
    tags = Column(JSON, default=list)  # ["bike", "car", "vip", "fragile_ok", "fast"]

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="courier")
    dispatch_logs = relationship("DispatchLog", back_populates="courier")
