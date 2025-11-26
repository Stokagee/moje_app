"""Testy pro tag matching logiku."""
import pytest
from conftest import PRAGUE_1KM


class TestTagMatching:
    """Testy pro tag matching při dispatchnutí."""

    def test_required_tag_single_match(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test shody jednoho požadovaného tagu."""
        # Kurýr s požadovaným tagem
        courier = courier_api.create_courier({
            "name": "Fragile OK",
            "phone": "+420111111111",
            "email": unique_email,
            "tags": ["bike", "fragile_ok"]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Objednávka s required_tags
        order = order_api.create_order({
            "customer_name": "Fragile Zákazník",
            "customer_phone": "+420999999999",
            "pickup_address": "Test",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": ["fragile_ok"]
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        assert result["courier_id"] == courier["id"]

    def test_required_tags_multiple_match(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test shody více požadovaných tagů."""
        courier = courier_api.create_courier({
            "name": "Multi Tag",
            "phone": "+420222222222",
            "email": unique_email,
            "tags": ["car", "vip", "fragile_ok", "fast"]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        order = order_api.create_order({
            "customer_name": "Multi Tag Zákazník",
            "customer_phone": "+420888888888",
            "pickup_address": "Test",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": ["fragile_ok", "fast"]
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True

    def test_required_tag_no_match(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test když kurýr nemá požadovaný tag."""
        # Kurýr BEZ požadovaného tagu
        courier = courier_api.create_courier({
            "name": "No Fragile",
            "phone": "+420333333333",
            "email": unique_email,
            "tags": ["bike", "fast"]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Objednávka vyžadující fragile_ok
        order = order_api.create_order({
            "customer_name": "Need Fragile",
            "customer_phone": "+420777777777",
            "pickup_address": "Test",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": ["fragile_ok"]
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        # Mělo by selhat - žádný kurýr s fragile_ok
        assert result["success"] is False

    def test_required_tags_partial_match(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test částečné shody tagů (má jen některé)."""
        courier = courier_api.create_courier({
            "name": "Partial",
            "phone": "+420444444444",
            "email": unique_email,
            "tags": ["fragile_ok"]  # Chybí "fast"
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        order = order_api.create_order({
            "customer_name": "Need Both",
            "customer_phone": "+420666666666",
            "pickup_address": "Test",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": ["fragile_ok", "fast"]  # Vyžaduje oba
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        # Mělo by selhat - kurýr nemá všechny požadované tagy
        assert result["success"] is False

    def test_no_required_tags(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test objednávky bez požadovaných tagů."""
        # Kurýr s jakýmikoli tagy
        courier = courier_api.create_courier({
            "name": "Any",
            "phone": "+420555555555",
            "email": unique_email,
            "tags": ["bike"]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # sample_order má prázdné required_tags
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True

    def test_courier_extra_tags_ok(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test že kurýr s více tagy než požadováno je OK."""
        # Kurýr s mnoha tagy
        courier = courier_api.create_courier({
            "name": "Super Courier",
            "phone": "+420666666666",
            "email": unique_email,
            "tags": ["bike", "car", "vip", "fragile_ok", "fast"]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Objednávka vyžadující jen jeden tag
        order = order_api.create_order({
            "customer_name": "Simple Need",
            "customer_phone": "+420555555555",
            "pickup_address": "Test",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": ["bike"]
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
