"""Dispatch log CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.dispatch_log import DispatchLog


def create_dispatch_log(db: Session, order_id: int, courier_id: int, action: str) -> DispatchLog:
    """Create a dispatch log entry."""
    db_log = DispatchLog(
        order_id=order_id,
        courier_id=courier_id,
        action=action
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_dispatch_logs_for_order(db: Session, order_id: int) -> List[DispatchLog]:
    """Get all dispatch logs for an order."""
    return db.query(DispatchLog).filter(DispatchLog.order_id == order_id).all()


def get_dispatch_logs_for_courier(db: Session, courier_id: int) -> List[DispatchLog]:
    """Get all dispatch logs for a courier."""
    return db.query(DispatchLog).filter(DispatchLog.courier_id == courier_id).all()


def get_dispatch_log(db: Session, log_id: int) -> Optional[DispatchLog]:
    """Get dispatch log by ID."""
    return db.query(DispatchLog).filter(DispatchLog.id == log_id).first()
