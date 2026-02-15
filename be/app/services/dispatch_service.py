"""Dispatch service for automatic courier assignment."""
import math
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.courier import Courier, CourierStatus
from app.models.order import Order, OrderStatus
from app.crud import courier as courier_crud
from app.crud import order as order_crud
from app.crud import dispatch_log as dispatch_log_crud


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth (in km).
    Uses the Haversine formula.
    """
    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def courier_has_required_tags(courier: Courier, required_tags: List[str]) -> bool:
    """Check if courier has all required tags for the order."""
    if not required_tags:
        return True

    courier_tags = courier.tags or []
    return all(tag in courier_tags for tag in required_tags)


def find_couriers_in_radius(
    db: Session,
    pickup_lat: float,
    pickup_lng: float,
    radius_km: float,
    required_tags: List[str],
    prefer_vip: bool = False
) -> List[Tuple[Courier, float]]:
    """
    Find available couriers within a given radius from pickup location.
    Returns list of (courier, distance) tuples sorted by distance.

    If prefer_vip is True, VIP couriers are prioritized.
    """
    available_couriers = courier_crud.get_available_couriers(db)

    matching_couriers = []
    for courier in available_couriers:
        # Skip couriers without GPS location
        if courier.lat is None or courier.lng is None:
            continue

        # Check if courier has required tags
        if not courier_has_required_tags(courier, required_tags):
            continue

        # Calculate distance
        distance = haversine_distance(
            courier.lat, courier.lng,
            pickup_lat, pickup_lng
        )

        # Check if within radius
        if distance <= radius_km:
            matching_couriers.append((courier, distance))

    # Sort by distance (closest first)
    matching_couriers.sort(key=lambda x: x[1])

    # If VIP preference, move VIP couriers to front while maintaining distance order
    if prefer_vip:
        vip_couriers = [(c, d) for c, d in matching_couriers if 'vip' in (c.tags or [])]
        non_vip_couriers = [(c, d) for c, d in matching_couriers if 'vip' not in (c.tags or [])]
        matching_couriers = vip_couriers + non_vip_couriers

    return matching_couriers


def auto_dispatch_order(db: Session, order_id: int) -> Tuple[bool, str, Optional[int]]:
    """
    Automatically dispatch an order to the best available courier.

    Algorithm:
    1. Check order exists and is in valid status
    2. Phase 1: Search within 750km radius
    3. Phase 2: If no match, expand to 1500km radius
    4. VIP orders prioritize VIP couriers
    5. Assign closest matching courier

    Returns:
        Tuple of (success, message, courier_id)
    """
    order = order_crud.get_order(db, order_id)
    if not order:
        return False, "Order not found", None

    if order.status not in [OrderStatus.CREATED, OrderStatus.SEARCHING]:
        return False, f"Order cannot be dispatched (status: {order.status})", None

    required_tags = order.required_tags or []
    prefer_vip = order.is_vip

    # Phase 1: Search within 750km
    couriers_750km = find_couriers_in_radius(
        db,
        order.pickup_lat,
        order.pickup_lng,
        radius_km=750.0,
        required_tags=required_tags,
        prefer_vip=prefer_vip
    )

    if couriers_750km:
        best_courier, distance = couriers_750km[0]
        return _assign_courier_to_order(db, order, best_courier, distance, "auto_assigned_750km")

    # Phase 2: Expand to 1500km
    couriers_1500km = find_couriers_in_radius(
        db,
        order.pickup_lat,
        order.pickup_lng,
        radius_km=1500.0,
        required_tags=required_tags,
        prefer_vip=prefer_vip
    )

    if couriers_1500km:
        best_courier, distance = couriers_1500km[0]
        return _assign_courier_to_order(db, order, best_courier, distance, "auto_assigned_1500km")

    # No courier found - set order to SEARCHING status
    order_crud.set_order_searching(db, order_id)
    return False, "No available courier found within 1500km radius", None


def _assign_courier_to_order(
    db: Session,
    order: Order,
    courier: Courier,
    distance: float,
    action: str
) -> Tuple[bool, str, int]:
    """Helper to assign a courier to an order and log the action."""
    # Update order
    order_crud.assign_courier_to_order(db, order.id, courier.id)

    # Update courier status to busy
    from app.schemas.courier import CourierStatusUpdate
    courier_crud.update_courier_status(
        db,
        courier.id,
        CourierStatusUpdate(status=CourierStatus.busy)
    )

    # Log the dispatch
    dispatch_log_crud.create_dispatch_log(
        db,
        order_id=order.id,
        courier_id=courier.id,
        action=action
    )

    return True, f"Courier {courier.name} assigned (distance: {distance:.2f}km)", courier.id


def manual_dispatch_order(
    db: Session,
    order_id: int,
    courier_id: int
) -> Tuple[bool, str]:
    """
    Manually assign a specific courier to an order.

    Returns:
        Tuple of (success, message)
    """
    order = order_crud.get_order(db, order_id)
    if not order:
        return False, "Order not found"

    if order.status not in [OrderStatus.CREATED, OrderStatus.SEARCHING]:
        return False, f"Order cannot be dispatched (status: {order.status})"

    courier = courier_crud.get_courier(db, courier_id)
    if not courier:
        return False, "Courier not found"

    if courier.status != CourierStatus.available:
        return False, f"Courier is not available (status: {courier.status})"

    # Check tags if order has requirements
    if order.required_tags and not courier_has_required_tags(courier, order.required_tags):
        return False, "Courier does not have required tags"

    # Update order
    order_crud.assign_courier_to_order(db, order.id, courier.id)

    # Update courier status
    from app.schemas.courier import CourierStatusUpdate
    courier_crud.update_courier_status(
        db,
        courier.id,
        CourierStatusUpdate(status=CourierStatus.busy)
    )

    # Log the dispatch
    dispatch_log_crud.create_dispatch_log(
        db,
        order_id=order.id,
        courier_id=courier.id,
        action="manual_assigned"
    )

    return True, f"Courier {courier.name} manually assigned to order {order.id}"


def get_available_couriers_for_order(
    db: Session,
    order_id: int,
    radius_km: float = 10.0
) -> List[dict]:
    """
    Get list of available couriers suitable for an order.
    Used for manual dispatch selection.

    Returns list of courier info with distance.
    """
    order = order_crud.get_order(db, order_id)
    if not order:
        return []

    required_tags = order.required_tags or []

    couriers = find_couriers_in_radius(
        db,
        order.pickup_lat,
        order.pickup_lng,
        radius_km=radius_km,
        required_tags=required_tags,
        prefer_vip=order.is_vip
    )

    return [
        {
            "courier_id": courier.id,
            "name": courier.name,
            "phone": courier.phone,
            "distance_km": round(distance, 2),
            "tags": courier.tags or [],
            "is_vip": 'vip' in (courier.tags or [])
        }
        for courier, distance in couriers
    ]
