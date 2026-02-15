"""Dispatch log model for Food Delivery system."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DispatchLog(Base):
    """Dispatch log - tracks courier assignment history."""
    __tablename__ = "dispatch_logs"

    id = Column(Integer, primary_key=True, index=True)

    # References
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), nullable=False)

    # Action: offered, accepted, rejected, auto_assigned
    action = Column(String, nullable=False)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="dispatch_logs")
    courier = relationship("Courier", back_populates="dispatch_logs")
