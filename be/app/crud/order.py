"""Order CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate, OrderStatusUpdate


def create_order(db: Session, order: OrderCreate) -> Order:
    """Create a new order."""
    db_order = Order(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        pickup_address=order.pickup_address,
        pickup_lat=order.pickup_lat,
        pickup_lng=order.pickup_lng,
        delivery_address=order.delivery_address,
        delivery_lat=order.delivery_lat,
        delivery_lng=order.delivery_lng,
        is_vip=order.is_vip,
        required_tags=order.required_tags,
        status=OrderStatus.CREATED
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID."""
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders."""
    return db.query(Order).offset(skip).limit(limit).all()


def get_orders_by_status(db: Session, status: OrderStatus) -> List[Order]:
    """Get orders by status."""
    return db.query(Order).filter(Order.status == status).all()


def get_pending_orders(db: Session) -> List[Order]:
    """Get orders waiting for courier (SEARCHING status)."""
    return db.query(Order).filter(Order.status == OrderStatus.SEARCHING).all()


def update_order_status(db: Session, order_id: int, status_update: OrderStatusUpdate) -> Optional[Order]:
    """Update order status."""
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    db_order.status = status_update.status
    db.commit()
    db.refresh(db_order)
    return db_order


def assign_courier_to_order(db: Session, order_id: int, courier_id: int) -> Optional[Order]:
    """Assign a courier to an order."""
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    db_order.courier_id = courier_id
    db_order.status = OrderStatus.ASSIGNED
    db.commit()
    db.refresh(db_order)
    return db_order


def set_order_searching(db: Session, order_id: int) -> Optional[Order]:
    """Set order to SEARCHING status (no courier found)."""
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    db_order.status = OrderStatus.SEARCHING
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    """Delete order."""
    db_order = get_order(db, order_id)
    if not db_order:
        return False

    db.delete(db_order)
    db.commit()
    return True
