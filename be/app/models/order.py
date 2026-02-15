"""Order model for Food Delivery system."""
from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class OrderStatus(str, enum.Enum):
    """Order lifecycle status."""
    CREATED = "CREATED"
    SEARCHING = "SEARCHING"
    ASSIGNED = "ASSIGNED"
    PICKED = "PICKED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(Base):
    """Order model - delivery order."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # Customer info
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)

    # Pickup location
    pickup_address = Column(String, nullable=False)
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)

    # Delivery location
    delivery_address = Column(String, nullable=False)
    delivery_lat = Column(Float, nullable=False)
    delivery_lng = Column(Float, nullable=False)

    # Order details
    status = Column(Enum(OrderStatus), default=OrderStatus.CREATED, nullable=False)
    is_vip = Column(Boolean, default=False)
    required_tags = Column(JSON, default=list)  # ["fragile_ok", "car"]

    # Assigned courier
    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    courier = relationship("Courier", back_populates="orders")
    dispatch_logs = relationship("DispatchLog", back_populates="order", cascade="all, delete-orphan")
