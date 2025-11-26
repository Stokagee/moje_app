"""Testy pro automatický dispatch."""
import pytest
from conftest import PRAGUE_CENTER, PRAGUE_1KM, PRAGUE_2KM, PRAGUE_3KM, PRAGUE_5KM, PRAGUE_10KM


class TestDispatchAuto:
    """Testy pro automatický dispatch."""

    def test_auto_dispatch_success_2km(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test úspěšného dispatchnutí kurýra do 2km."""
        # Kurýr 1km od místa vyzvednutí s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Blízký",
            "phone": "+420111111111",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Objednávka v centru s required_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "2km Test",
            "customer_phone": "+420999999999",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        # Auto dispatch
        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        assert result["courier_id"] == courier["id"]
        # Kurýr je 1km daleko, message obsahuje distance
        assert "km" in result["message"]

    def test_auto_dispatch_success_5km(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test dispatchnutí kurýra mezi 2-5km."""
        # Kurýr 3km od místa vyzvednutí s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Střední",
            "phone": "+420222222222",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_3KM)

        # Objednávka s required_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "5km Test",
            "customer_phone": "+420888888888",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        # Auto dispatch
        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        assert result["courier_id"] == courier["id"]
        # Kurýr je 3km daleko - fáze 2 (5km range)
        assert "3." in result["message"] or "km" in result["message"]

    def test_auto_dispatch_no_courier_in_range(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test když není žádný kurýr v dosahu."""
        # Kurýr 10km od místa vyzvednutí s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Vzdálený",
            "phone": "+420333333333",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_10KM)

        # Objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "No Range Test",
            "customer_phone": "+420777777777",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        # Auto dispatch
        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is False
        assert "No available courier" in result["message"]

        # Objednávka by měla být v SEARCHING
        updated_order = order_api.get_order(order["id"])
        assert updated_order["status"] == "SEARCHING"

    def test_auto_dispatch_courier_busy(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že busy kurýr je ignorován."""
        # Busy kurýr blízko s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Busy",
            "phone": "+420444444444",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.update_location(courier["id"], *PRAGUE_1KM)
        courier_api.update_status(courier["id"], "busy")

        # Objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Busy Test",
            "customer_phone": "+420666666666",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        # Auto dispatch - měl by selhat (kurýr je busy)
        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is False

    def test_auto_dispatch_courier_offline(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že offline kurýr je ignorován."""
        # Offline kurýr blízko s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Offline",
            "phone": "+420555555555",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.update_location(courier["id"], *PRAGUE_1KM)
        # Default status je offline

        # Objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Offline Test",
            "customer_phone": "+420555555555",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        # Auto dispatch - měl by selhat (kurýr je offline)
        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is False

    def test_auto_dispatch_courier_no_location(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že kurýr bez GPS lokace je ignorován."""
        # Kurýr bez lokace s unikátním tagem
        courier = courier_api.create_courier({
            "name": "No GPS",
            "phone": "+420666666666",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.update_status(courier["id"], "available")
        # Bez update_location

        # Objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "No GPS Test",
            "customer_phone": "+420444444444",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        # Auto dispatch - měl by selhat (kurýr nemá lokaci)
        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is False

    def test_auto_dispatch_sets_courier_busy(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že dispatch nastaví kurýra na busy."""
        # Kurýr s unikátním tagem
        courier = courier_api.create_courier({
            "name": "To Busy",
            "phone": "+420777777777",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Ověříme že je available
        assert courier_api.get_courier(courier["id"])["status"] == "available"

        # Objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Busy Test",
            "customer_phone": "+420333333333",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Ověříme že je busy
        assert courier_api.get_courier(courier["id"])["status"] == "busy"

    def test_auto_dispatch_creates_log(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že dispatch vytvoří log záznam."""
        # Kurýr s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Logged",
            "phone": "+420888888888",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Log Test",
            "customer_phone": "+420222222222",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Zkontrolujeme logy
        logs = dispatch_api.get_logs_for_order(order["id"])

        assert len(logs) > 0
        assert logs[0]["order_id"] == order["id"]
        assert logs[0]["courier_id"] == courier["id"]
        assert "auto_assigned" in logs[0]["action"]

    def test_auto_dispatch_closest_first(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že nejbližší kurýr je vybrán první."""
        # Vzdálenější kurýr s unikátním tagem
        far = courier_api.create_courier({
            "name": "Vzdálený",
            "phone": "+420111111111",
            "email": f"far_{unique_email}",
            "tags": [unique_tag]
        })
        cleanup_couriers.append(far["id"])
        courier_api.set_available_with_location(far["id"], *PRAGUE_2KM)

        # Bližší kurýr s unikátním tagem
        near = courier_api.create_courier({
            "name": "Blízký",
            "phone": "+420222222222",
            "email": f"near_{unique_email}",
            "tags": [unique_tag]
        })
        cleanup_couriers.append(near["id"])
        courier_api.set_available_with_location(near["id"], *PRAGUE_1KM)

        # Objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Closest Test",
            "customer_phone": "+420111111111",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        assert result["courier_id"] == near["id"]

    def test_auto_dispatch_already_assigned(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test dispatch již přiřazené objednávky."""
        courier = courier_api.create_courier({
            "name": "Double",
            "phone": "+420333333333",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        # První dispatch
        dispatch_api.auto_dispatch(order["id"])

        # Druhý dispatch - měl by selhat
        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is False
        assert "cannot be dispatched" in result["message"]

    def test_auto_dispatch_order_not_found(self, dispatch_api):
        """Test dispatch neexistující objednávky."""
        result = dispatch_api.auto_dispatch(999999)

        assert result["success"] is False
        assert "not found" in result["message"]

    def test_auto_dispatch_cancelled_order(
        self, order_api, dispatch_api, sample_order, cleanup_orders
    ):
        """Test dispatch zrušené objednávky."""
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])
        order_api.cancel_order(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is False
