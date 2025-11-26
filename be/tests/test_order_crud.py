"""Testy pro CRUD operace objednávek."""
import pytest


class TestOrderCRUD:
    """Testy pro Order CRUD operace."""

    def test_create_order_success(self, order_api, sample_order, cleanup_orders):
        """Test vytvoření objednávky."""
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        assert order["id"] is not None
        assert order["customer_name"] == sample_order["customer_name"]
        assert order["pickup_address"] == sample_order["pickup_address"]
        assert order["delivery_address"] == sample_order["delivery_address"]

    def test_create_order_vip(self, order_api, sample_order_vip, cleanup_orders):
        """Test vytvoření VIP objednávky."""
        order = order_api.create_order(sample_order_vip)
        cleanup_orders.append(order["id"])

        assert order["is_vip"] is True

    def test_create_order_with_tags(self, order_api, sample_order_with_tags, cleanup_orders):
        """Test vytvoření objednávky s required_tags."""
        order = order_api.create_order(sample_order_with_tags)
        cleanup_orders.append(order["id"])

        assert order["required_tags"] == ["fragile_ok"]

    def test_create_order_default_status(self, order_api, sample_order, cleanup_orders):
        """Test že nová objednávka má status CREATED."""
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        assert order["status"] == "CREATED"

    def test_get_order_by_id(self, order_api, created_order):
        """Test získání objednávky podle ID."""
        order = order_api.get_order(created_order["id"])

        assert order["id"] == created_order["id"]
        assert order["customer_name"] == created_order["customer_name"]

    def test_get_order_with_courier(
        self, courier_api, order_api, dispatch_api,
        sample_courier, sample_order, unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test získání objednávky s detaily kurýra."""
        # Vytvoříme kurýra
        courier_data = sample_courier.copy()
        courier_data["email"] = unique_email
        courier = courier_api.create_courier(courier_data)
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], 50.0815, 14.4195)

        # Vytvoříme objednávku
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        # Dispatch
        dispatch_api.auto_dispatch(order["id"])

        # Získáme objednávku s detaily kurýra
        order_with_courier = order_api.get_order(order["id"])

        assert order_with_courier["courier_id"] == courier["id"]
        assert order_with_courier["courier_name"] == courier["name"]
        assert order_with_courier["courier_phone"] == courier["phone"]

    def test_get_order_not_found(self, order_api):
        """Test získání neexistující objednávky."""
        response = order_api.get_order_raw(999999)
        assert response.status_code == 404

    def test_get_all_orders(self, order_api, sample_order, cleanup_orders):
        """Test získání seznamu objednávek."""
        # Vytvoříme dvě objednávky
        o1 = order_api.create_order(sample_order)
        cleanup_orders.append(o1["id"])

        o2 = order_api.create_order(sample_order)
        cleanup_orders.append(o2["id"])

        # Použijeme vyšší limit pro získání všech objednávek
        orders = order_api.get_all_orders(limit=1000)
        order_ids = [o["id"] for o in orders]

        assert o1["id"] in order_ids
        assert o2["id"] in order_ids

    def test_get_all_orders_pagination(self, order_api, sample_order, cleanup_orders):
        """Test stránkování objednávek."""
        # Vytvoříme 5 objednávek
        for _ in range(5):
            o = order_api.create_order(sample_order)
            cleanup_orders.append(o["id"])

        # Test limit
        limited = order_api.get_all_orders(skip=0, limit=2)
        assert len(limited) <= 2

    def test_get_orders_by_status(self, order_api, sample_order, cleanup_orders):
        """Test filtrace objednávek podle statusu."""
        # Vytvoříme objednávku
        order = order_api.create_order(sample_order)
        cleanup_orders.append(order["id"])

        # Získáme objednávky se statusem CREATED
        created_orders = order_api.get_orders_by_status("CREATED")
        order_ids = [o["id"] for o in created_orders]

        assert order["id"] in order_ids

    def test_delete_order(self, order_api, sample_order):
        """Test smazání objednávky."""
        order = order_api.create_order(sample_order)
        order_id = order["id"]

        # Ověříme že existuje
        assert order_api.get_order_safe(order_id) is not None

        # Smažeme
        order_api.delete_order(order_id)

        # Ověříme že neexistuje
        assert order_api.get_order_safe(order_id) is None

    def test_delete_order_not_found(self, order_api):
        """Test smazání neexistující objednávky."""
        response = order_api.delete_order_raw(999999)
        assert response.status_code == 404
