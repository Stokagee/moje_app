"""Kompletní E2E workflow testy."""
import pytest
from conftest import PRAGUE_1KM, PRAGUE_CENTER


class TestFullWorkflow:
    """Testy pro kompletní E2E scénáře."""

    def test_complete_delivery_workflow(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test kompletního doručovacího workflow."""
        # 1. Vytvoření kurýra s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Workflow Kurýr",
            "phone": "+420111111111",
            "email": unique_email,
            "tags": ["bike", unique_tag]
        })
        cleanup_couriers.append(courier["id"])

        # 2. Kurýr jde online
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # 3. Vytvoření objednávky s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Workflow Test",
            "customer_phone": "+420987654321",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.427,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])
        assert order["status"] == "CREATED"

        # 4. Auto dispatch
        result = dispatch_api.auto_dispatch(order["id"])
        assert result["success"] is True

        # 5. Ověření ASSIGNED
        order = order_api.get_order(order["id"])
        assert order["status"] == "ASSIGNED"
        assert order["courier_id"] == courier["id"]

        # 6. Kurýr je busy
        courier = courier_api.get_courier(courier["id"])
        assert courier["status"] == "busy"

        # 7. Pickup
        order = order_api.pickup_order(order["id"])
        assert order["status"] == "PICKED"

        # 8. Deliver
        order = order_api.deliver_order(order["id"])
        assert order["status"] == "DELIVERED"

        # 9. Kurýr je zpět available
        courier = courier_api.get_courier(courier["id"])
        assert courier["status"] == "available"

    def test_workflow_with_retry_dispatch(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test workflow s opakovaným dispatchem."""
        # Objednávka s unikátním tagem - zatím žádný kurýr s tímto tagem
        order = order_api.create_order({
            "customer_name": "Retry Test",
            "customer_phone": "+420987654321",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.427,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        # První dispatch - žádný kurýr s tímto tagem
        result1 = dispatch_api.auto_dispatch(order["id"])
        assert result1["success"] is False

        # Objednávka v SEARCHING
        order = order_api.get_order(order["id"])
        assert order["status"] == "SEARCHING"

        # Kurýr přichází s požadovaným tagem
        courier = courier_api.create_courier({
            "name": "Late Kurýr",
            "phone": "+420222222222",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Retry dispatch
        result2 = dispatch_api.auto_dispatch(order["id"])
        assert result2["success"] is True

    def test_workflow_order_cancellation(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test workflow se zrušením objednávky."""
        # Kurýr s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Cancel Kurýr",
            "phone": "+420333333333",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Cancel Test",
            "customer_phone": "+420987654321",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.427,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        # Dispatch
        dispatch_api.auto_dispatch(order["id"])

        # Kurýr je busy
        assert courier_api.get_courier(courier["id"])["status"] == "busy"

        # Zákazník ruší objednávku
        order = order_api.cancel_order(order["id"])
        assert order["status"] == "CANCELLED"

        # Kurýr je zpět available
        assert courier_api.get_courier(courier["id"])["status"] == "available"

    def test_workflow_multiple_orders_one_courier(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že jeden kurýr nemůže mít více objednávek současně."""
        # Kurýr s unikátním tagem
        courier = courier_api.create_courier({
            "name": "Busy Kurýr",
            "phone": "+420444444444",
            "email": unique_email,
            "tags": [unique_tag]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # První objednávka s unique_tag
        order1 = order_api.create_order({
            "customer_name": "Multi Order 1",
            "customer_phone": "+420987654321",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.427,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order1["id"])
        result1 = dispatch_api.auto_dispatch(order1["id"])
        assert result1["success"] is True

        # Druhá objednávka se stejným tagem - kurýr je busy
        order2 = order_api.create_order({
            "customer_name": "Multi Order 2",
            "customer_phone": "+420987654322",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 3",
            "delivery_lat": 50.083,
            "delivery_lng": 14.428,
            "is_vip": False,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order2["id"])
        result2 = dispatch_api.auto_dispatch(order2["id"])
        assert result2["success"] is False

    def test_workflow_courier_completes_returns_available(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order, cleanup_couriers, cleanup_orders
    ):
        """Test že kurýr po dokončení může vzít další objednávku."""
        courier = courier_api.create_courier({
            "name": "Repeat Kurýr",
            "phone": "+420555555555",
            "email": unique_email,
            "tags": []
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # První objednávka - kompletní workflow
        order1 = order_api.create_order(sample_order)
        cleanup_orders.append(order1["id"])
        dispatch_api.auto_dispatch(order1["id"])
        order_api.pickup_order(order1["id"])
        order_api.deliver_order(order1["id"])

        # Kurýr je available
        assert courier_api.get_courier(courier["id"])["status"] == "available"

        # Druhá objednávka - měla by projít
        order2 = order_api.create_order(sample_order)
        cleanup_orders.append(order2["id"])
        result = dispatch_api.auto_dispatch(order2["id"])
        assert result["success"] is True

    def test_workflow_vip_order_priority(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order_vip, cleanup_couriers, cleanup_orders
    ):
        """Test VIP order workflow."""
        # VIP kurýr
        vip_courier = courier_api.create_courier({
            "name": "VIP Kurýr",
            "phone": "+420666666666",
            "email": unique_email,
            "tags": ["car", "vip"]
        })
        cleanup_couriers.append(vip_courier["id"])
        courier_api.set_available_with_location(vip_courier["id"], *PRAGUE_1KM)

        # VIP objednávka
        order = order_api.create_order(sample_order_vip)
        cleanup_orders.append(order["id"])
        assert order["is_vip"] is True

        # Dispatch
        result = dispatch_api.auto_dispatch(order["id"])
        assert result["success"] is True
        assert result["courier_id"] == vip_courier["id"]

        # Kompletní workflow
        order_api.pickup_order(order["id"])
        order = order_api.deliver_order(order["id"])
        assert order["status"] == "DELIVERED"

    def test_workflow_fragile_order(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order_with_tags, cleanup_couriers, cleanup_orders
    ):
        """Test workflow s fragile objednávkou."""
        # Kurýr s fragile_ok tagem
        courier = courier_api.create_courier({
            "name": "Fragile Kurýr",
            "phone": "+420777777777",
            "email": unique_email,
            "tags": ["bike", "fragile_ok"]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Fragile objednávka
        order = order_api.create_order(sample_order_with_tags)
        cleanup_orders.append(order["id"])
        assert "fragile_ok" in order["required_tags"]

        # Dispatch
        result = dispatch_api.auto_dispatch(order["id"])
        assert result["success"] is True

    def test_workflow_express_delivery(
        self, courier_api, order_api, dispatch_api,
        unique_email, cleanup_couriers, cleanup_orders
    ):
        """Test express doručení s fast tagem."""
        # Fast kurýr
        courier = courier_api.create_courier({
            "name": "Express Kurýr",
            "phone": "+420888888888",
            "email": unique_email,
            "tags": ["bike", "fast"]
        })
        cleanup_couriers.append(courier["id"])
        courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)

        # Express objednávka
        order = order_api.create_order({
            "customer_name": "Express Zákazník",
            "customer_phone": "+420999999999",
            "pickup_address": "Test",
            "pickup_lat": 50.0815,
            "pickup_lng": 14.4195,
            "delivery_address": "Test 2",
            "delivery_lat": 50.082,
            "delivery_lng": 14.420,
            "is_vip": False,
            "required_tags": ["fast"]
        })
        cleanup_orders.append(order["id"])

        # Dispatch
        result = dispatch_api.auto_dispatch(order["id"])
        assert result["success"] is True

        # Kompletní workflow
        order_api.pickup_order(order["id"])
        order = order_api.deliver_order(order["id"])
        assert order["status"] == "DELIVERED"
