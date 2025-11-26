"""Testy pro edge cases a chybové stavy."""
import pytest
from conftest import PRAGUE_CENTER, PRAGUE_2KM, PRAGUE_5KM


class TestEdgeCases:
    """Testy pro edge cases."""

    def test_dispatch_with_zero_distance(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test dispatchnutí kurýra na stejném místě jako pickup."""
        # Kurýr přesně na místě vyzvednutí
        courier = courier_api.create_courier({
            "name": "Exact Location",
            "phone": "+420111111111",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_CENTER)

        # Objednávka na stejném místě
        order = order_api.create_order({
            "customer_name": "Same Location",
            "customer_phone": "+420999999999",
            "pickup_address": "Test",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.09,
            "delivery_lng": 14.43,
            "is_vip": False,
            "required_tags": []
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])
        assert result["success"] is True
        # Vzdálenost by měla být ~0km
        assert "0.00km" in result["message"] or "0.01km" in result["message"]

    def test_dispatch_exactly_2km_boundary(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test dispatchnutí přesně na hranici 2km."""
        courier = courier_api.create_courier({
            "name": "2km Boundary",
            "phone": "+420222222222",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_2KM)

        order = order_api.create_order({
            "customer_name": "2km Test",
            "customer_phone": "+420888888888",
            "pickup_address": "Test",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.09,
            "delivery_lng": 14.43,
            "is_vip": False,
            "required_tags": []
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])
        # Mělo by projít (2km je hranice pro fázi 1)
        assert result["success"] is True

    def test_dispatch_exactly_5km_boundary(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test dispatchnutí přesně na hranici 5km."""
        courier = courier_api.create_courier({
            "name": "5km Boundary",
            "phone": "+420333333333",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_5KM)

        order = order_api.create_order({
            "customer_name": "5km Test",
            "customer_phone": "+420777777777",
            "pickup_address": "Test",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.09,
            "delivery_lng": 14.43,
            "is_vip": False,
            "required_tags": []
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])
        # Mělo by projít (5km je hranice pro fázi 2)
        assert result["success"] is True

    def test_concurrent_dispatch_same_courier(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test souběžného dispatchnutí na stejného kurýra."""
        # Kurýr s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Concurrent",
            "phone": "+420444444444",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Dvě objednávky s unique_tag pro izolaci
        order1 = order_api.create_order({
            "customer_name": "Concurrent 1",
            "customer_phone": "+420987654321",
            "pickup_address": "Národní",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.427,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order1["id"])

        order2 = order_api.create_order({
            "customer_name": "Concurrent 2",
            "customer_phone": "+420987654322",
            "pickup_address": "Národní",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 3",
            "delivery_lat": 50.083,
            "delivery_lng": 14.428,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order2["id"])

        # První dispatch
        result1 = dispatch_api.auto_dispatch(order1["id"])
        assert result1["success"] is True

        # Druhý dispatch - kurýr už je busy
        result2 = dispatch_api.auto_dispatch(order2["id"])
        assert result2["success"] is False

    def test_update_location_during_busy(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test aktualizace lokace busy kurýra."""
        courier = courier_api.create_courier({
            "name": "Moving",
            "phone": "+420555555555",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])
        dispatch_api.auto_dispatch(order["id"])

        # Kurýr je busy
        assert courier_api.get_courier(courier["id"])["status"] == "busy"

        # Update lokace by měl fungovat i během busy
        updated = courier_api.update_location(courier["id"], 50.09, 14.43)
        assert updated["lat"] == 50.09
        assert updated["lng"] == 14.43

    def test_empty_database_queries(self, courier_api, order_api, dispatch_api):
        """Test dotazů na prázdnou databázi."""
        # Tyto dotazy by neměly selhat ani s prázdnou DB
        couriers = courier_api.get_all_couriers()
        assert isinstance(couriers, list)

        available = courier_api.get_available_couriers()
        assert isinstance(available, list)

        orders = order_api.get_all_orders()
        assert isinstance(orders, list)

        pending = order_api.get_pending_orders()
        assert isinstance(pending, list)

    def test_special_characters_in_names(
        self, courier_api, order_api, unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test českých znaků v jménech."""
        courier = courier_api.create_courier({
            "name": "Jiří Řehoř Čech",
            "phone": "+420666666666",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])

        # Ověříme že se jméno uložilo správně
        loaded = courier_api.get_courier(courier["id"])
        assert loaded["name"] == "Jiří Řehoř Čech"

        # Objednávka s českými znaky
        order = order_api.create_order({
            "customer_name": "Žluťoučký Kůň",
            "customer_phone": "+420777777777",
            "pickup_address": "Příčná 123, Praha",
            "pickup_lat": 50.08,
            "pickup_lng": 14.42,
            "delivery_address": "Řeznická 456, Praha",
            "delivery_lat": 50.09,
            "delivery_lng": 14.43,
            "is_vip": False,
            "required_tags": []
        })
        cleanup_orders.append(order["id"])

        loaded_order = order_api.get_order(order["id"])
        assert loaded_order["customer_name"] == "Žluťoučký Kůň"
        assert loaded_order["pickup_address"] == "Příčná 123, Praha"

    def test_very_long_address(
        self, order_api, cleanup_orders
    ):
        """Test velmi dlouhé adresy."""
        long_address = "A" * 500  # 500 znaků

        order = order_api.create_order({
            "customer_name": "Long Address",
            "customer_phone": "+420888888888",
            "pickup_address": long_address,
            "pickup_lat": 50.08,
            "pickup_lng": 14.42,
            "delivery_address": long_address,
            "delivery_lat": 50.09,
            "delivery_lng": 14.43,
            "is_vip": False,
            "required_tags": []
        })
        cleanup_orders.append(order["id"])

        # Mělo by projít
        assert order["id"] is not None
