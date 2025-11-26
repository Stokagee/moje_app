"""Testy pro lifecycle objednávek."""
import pytest


class TestOrderStatus:
    """Testy pro status management objednávek."""

    def test_pickup_order_from_assigned(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test ASSIGNED → PICKED."""
        # Vytvoříme kurýra a nastavíme jako available
        courier = courier_api.create_courier({
            "name": "Pickup Kurýr",
            "phone": "+420111111111",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Vytvoříme a dispatchneme objednávku
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Pickup
        picked = order_api.pickup_order(order["id"])

        assert picked["status"] == "PICKED"

    def test_pickup_order_invalid_status(self, order_api, created_order):
        """Test CREATED → PICKED (mělo by selhat)."""
        # Objednávka je v CREATED stavu
        response = order_api.pickup_order_raw(created_order["id"])

        assert response.status_code == 400

    def test_deliver_order_from_picked(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test PICKED → DELIVERED."""
        # Vytvoříme kurýra
        courier = courier_api.create_courier({
            "name": "Deliver Kurýr",
            "phone": "+420222222222",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Vytvoříme objednávku a dispatchneme
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Pickup
        order_api.pickup_order(order["id"])

        # Deliver
        delivered = order_api.deliver_order(order["id"])

        assert delivered["status"] == "DELIVERED"

    def test_deliver_order_invalid_status(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test ASSIGNED → DELIVERED (mělo by selhat)."""
        # Vytvoříme kurýra
        courier = courier_api.create_courier({
            "name": "Invalid Deliver",
            "phone": "+420333333333",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Vytvoříme a dispatchneme (ASSIGNED)
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Pokus o deliver bez pickup
        response = order_api.deliver_order_raw(order["id"])

        assert response.status_code == 400

    def test_deliver_frees_courier(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test že doručení uvolní kurýra."""
        # Vytvoříme kurýra
        courier = courier_api.create_courier({
            "name": "Free Kurýr",
            "phone": "+420444444444",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Vytvoříme objednávku a dispatchneme
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Ověříme že kurýr je busy
        courier_after_dispatch = courier_api.get_courier(courier["id"])
        assert courier_after_dispatch["status"] == "busy"

        # Pickup a deliver
        order_api.pickup_order(order["id"])
        order_api.deliver_order(order["id"])

        # Ověříme že kurýr je zpět available
        courier_after_deliver = courier_api.get_courier(courier["id"])
        assert courier_after_deliver["status"] == "available"

    def test_cancel_order_from_created(self, order_api, created_order):
        """Test CREATED → CANCELLED."""
        cancelled = order_api.cancel_order(created_order["id"])

        assert cancelled["status"] == "CANCELLED"

    def test_cancel_order_from_assigned(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test ASSIGNED → CANCELLED."""
        # Vytvoříme kurýra
        courier = courier_api.create_courier({
            "name": "Cancel Kurýr",
            "phone": "+420555555555",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Vytvoříme a dispatchneme
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Cancel
        cancelled = order_api.cancel_order(order["id"])

        assert cancelled["status"] == "CANCELLED"

    def test_cancel_frees_courier(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že zrušení uvolní kurýra."""
        # Vytvoříme kurýra s unikátním tagem pro izolaci
        courier = courier_api.create_courier({
            "name": "Cancel Free",
            "phone": "+420666666666",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Vytvoříme objednávku s required_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Cancel Test",
            "customer_phone": "+420999999999",
            "pickup_address": "Test",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Ověříme že kurýr je busy
        assert courier_api.get_courier(courier["id"])["status"] == "busy"

        # Cancel
        order_api.cancel_order(order["id"])

        # Ověříme že kurýr je zpět available
        assert courier_api.get_courier(courier["id"])["status"] == "available"

    def test_cancel_delivered_order_fails(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test DELIVERED → CANCELLED (mělo by selhat)."""
        # Vytvoříme kurýra
        courier = courier_api.create_courier({
            "name": "Delivered Cancel",
            "phone": "+420777777777",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Kompletní workflow
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])
        order_api.pickup_order(order["id"])
        order_api.deliver_order(order["id"])

        # Pokus o cancel doručené objednávky
        response = order_api.cancel_order_raw(order["id"])

        assert response.status_code == 400

    def test_get_pending_orders(
        self, courier_api, order_api, dispatch_api,
        sample_order, cleanup_orders
    ):
        """Test získání objednávek ve stavu SEARCHING."""
        # Vytvoříme objednávku bez kurýra v dosahu
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        # Auto dispatch bez kurýra → SEARCHING
        result = dispatch_api.auto_dispatch(order["id"])

        if not result["success"]:
            # Objednávka by měla být v SEARCHING
            pending = order_api.get_pending_orders()
            pending_ids = [o["id"] for o in pending]
            assert order["id"] in pending_ids
