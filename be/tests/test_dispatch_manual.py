"""Testy pro manuální dispatch."""
import pytest
from conftest import PRAGUE_1KM


class TestDispatchManual:
    """Testy pro manuální dispatch."""

    def test_manual_dispatch_success(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test úspěšného manuálního dispatchnutí."""
        courier = courier_api.create_courier({
            "name": "Manual",
            "phone": "+420111111111",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        result = dispatch_api.manual_dispatch(order["id"], courier["id"])

        assert result["success"] is True
        assert result["courier_id"] == courier["id"]

        # Ověříme stav objednávky
        updated_order = order_api.get_order(order["id"])
        assert updated_order["status"] == "ASSIGNED"
        assert updated_order["courier_id"] == courier["id"]

    def test_manual_dispatch_courier_not_available(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test manuálního dispatchnutí na nedostupného kurýra."""
        # Busy kurýr
        courier = courier_api.create_courier({
            "name": "Busy Manual",
            "phone": "+420222222222",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.update_status(courier["id"], "busy")

        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        result = dispatch_api.manual_dispatch(order["id"], courier["id"])

        assert result["success"] is False
        assert "not available" in result["message"]

    def test_manual_dispatch_order_already_assigned(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test manuálního dispatchnutí již přiřazené objednávky."""
        # První kurýr
        c1 = courier_api.create_courier({
            "name": "First",
            "phone": "+420333333333",
            "email": f"first_{unique_email}",
            "tags": []
        })
        cleanup_couriers.append(c1["id"])
        courier_api.set_available_with_location(c1["id"], *PRAGUE_1KM)

        # Druhý kurýr
        c2 = courier_api.create_courier({
            "name": "Second",
            "phone": "+420444444444",
            "email": f"second_{unique_email}",
            "tags": []
        })
        cleanup_couriers.append(c2["id"])
        courier_api.set_available_with_location(c2["id"], *PRAGUE_1KM)

        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        # První dispatch
        dispatch_api.manual_dispatch(order["id"], c1["id"])

        # Druhý pokus - měl by selhat
        result = dispatch_api.manual_dispatch(order["id"], c2["id"])

        assert result["success"] is False

    def test_manual_dispatch_order_not_found(self, dispatch_api, courier_api, unique_email, cleanup_couriers):
        """Test manuálního dispatchnutí neexistující objednávky."""
        courier = courier_api.create_courier({
            "name": "No Order",
            "phone": "+420555555555",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        result = dispatch_api.manual_dispatch(999999, courier["id"])

        assert result["success"] is False
        assert "not found" in result["message"]

    def test_manual_dispatch_courier_not_found(
        self, order_api, dispatch_api, sample_order, cleanup_orders
    ):
        """Test manuálního dispatchnutí na neexistujícího kurýra."""
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        result = dispatch_api.manual_dispatch(order["id"], 999999)

        assert result["success"] is False
        assert "not found" in result["message"]

    def test_manual_dispatch_creates_log(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test že manuální dispatch vytvoří log."""
        courier = courier_api.create_courier({
            "name": "Manual Log",
            "phone": "+420666666666",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        dispatch_api.manual_dispatch(order["id"], courier["id"])

        logs = dispatch_api.get_logs_for_order(order["id"])

        assert len(logs) > 0
        assert logs[0]["action"] == "manual_assigned"
