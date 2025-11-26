"""Testy pro VIP prioritu."""
import pytest
from conftest import PRAGUE_1KM, PRAGUE_2KM, PRAGUE_CENTER


class TestVIPPriority:
    """Testy pro VIP prioritu dispatchnutí."""

    def test_vip_order_prefers_vip_courier(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order_vip, cleanup_couriers, cleanup_orders
    ):
        """Test že VIP objednávka preferuje VIP kurýra."""
        # Non-VIP kurýr - bližší
        non_vip = courier_api.create_courier({
            "name": "Non VIP Blízký",
            "phone": "+420111111111",
            "email": f"nonvip_{unique_email}",
            "tags": ["bike"]
        })
        cleanup_couriers.append(non_vip["id"])
        courier_api.set_available_with_location(non_vip["id"], *PRAGUE_1KM)

        # VIP kurýr - vzdálenější
        vip = courier_api.create_courier({
            "name": "VIP Vzdálený",
            "phone": "+420222222222",
            "email": f"vip_{unique_email}",
            "tags": ["car", "vip"]
        })
        cleanup_couriers.append(vip["id"])
        courier_api.set_available_with_location(vip["id"], *PRAGUE_2KM)

        # VIP objednávka
        order = order_api.create_order(sample_order_vip)
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        assert result["courier_id"] == vip["id"]

    def test_vip_order_falls_back_to_non_vip(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že VIP objednávka použije non-VIP kurýra když není VIP."""
        # Pouze non-VIP kurýr s unikátním tagem
        non_vip = courier_api.create_courier({
            "name": "Non VIP",
            "phone": "+420333333333",
            "email": unique_email,
            "tags": ["bike", unique_tag]
        })
        cleanup_couriers.append(non_vip["id"])
        courier_api.set_available_with_location(non_vip["id"], *PRAGUE_1KM)

        # VIP objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "VIP Fallback",
            "customer_phone": "+420555666777",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.087,
            "delivery_lng": 14.421,
            "is_vip": True,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        assert result["courier_id"] == non_vip["id"]

    def test_non_vip_order_ignores_vip_priority(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test že non-VIP objednávka ignoruje VIP prioritu."""
        # VIP kurýr - vzdálenější s unique_tag
        vip = courier_api.create_courier({
            "name": "VIP",
            "phone": "+420444444444",
            "email": f"vip_{unique_email}",
            "tags": ["car", "vip", unique_tag]
        })
        cleanup_couriers.append(vip["id"])
        courier_api.set_available_with_location(vip["id"], *PRAGUE_2KM)

        # Non-VIP kurýr - bližší s unique_tag
        non_vip = courier_api.create_courier({
            "name": "Non VIP",
            "phone": "+420555555555",
            "email": f"nonvip_{unique_email}",
            "tags": ["bike", unique_tag]
        })
        cleanup_couriers.append(non_vip["id"])
        courier_api.set_available_with_location(non_vip["id"], *PRAGUE_1KM)

        # Non-VIP objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Non VIP Test",
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

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        # Měl by být vybrán bližší kurýr (non-VIP)
        assert result["courier_id"] == non_vip["id"]

    def test_vip_courier_closer_wins(
        self, courier_api, order_api, dispatch_api,
        unique_email, sample_order_vip, cleanup_couriers, cleanup_orders
    ):
        """Test že bližší VIP kurýr vyhrává nad vzdálenějším VIP."""
        # Vzdálenější VIP kurýr
        vip_far = courier_api.create_courier({
            "name": "VIP Vzdálený",
            "phone": "+420666666666",
            "email": f"vipfar_{unique_email}",
            "tags": ["vip"]
        })
        cleanup_couriers.append(vip_far["id"])
        courier_api.set_available_with_location(vip_far["id"], *PRAGUE_2KM)

        # Bližší VIP kurýr
        vip_near = courier_api.create_courier({
            "name": "VIP Blízký",
            "phone": "+420777777777",
            "email": f"vipnear_{unique_email}",
            "tags": ["vip"]
        })
        cleanup_couriers.append(vip_near["id"])
        courier_api.set_available_with_location(vip_near["id"], *PRAGUE_1KM)

        # VIP objednávka
        order = order_api.create_order(sample_order_vip)
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        assert result["courier_id"] == vip_near["id"]

    def test_vip_with_distance_sorting(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test VIP priority s řazením podle vzdálenosti."""
        # 3 VIP kurýři v různých vzdálenostech s unikátním tagem
        distances = [
            (PRAGUE_2KM, "vip2km"),
            (PRAGUE_1KM, "vip1km"),
            ((50.085, 14.420), "vip05km"),  # ~0.5km
        ]

        created = []
        for loc, suffix in distances:
            c = courier_api.create_courier({
                "name": f"VIP {suffix}",
                "phone": f"+420{len(created)}11111111",
                "email": f"{suffix}_{unique_email}",
                "tags": ["vip", unique_tag]
            })
            cleanup_couriers.append(c["id"])
            courier_api.set_available_with_location(c["id"], *loc)
            created.append(c)

        # VIP objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "VIP Sorting Test",
            "customer_phone": "+420555666777",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.087,
            "delivery_lng": 14.421,
            "is_vip": True,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        # Nejbližší VIP (0.5km) by měl být vybrán
        assert result["courier_id"] == created[2]["id"]

    def test_multiple_vip_couriers(
        self, courier_api, order_api, dispatch_api,
        unique_email, unique_tag, cleanup_couriers, cleanup_orders
    ):
        """Test s více VIP kurýry - nejbližší je vybrán."""
        couriers = []
        for i in range(3):
            c = courier_api.create_courier({
                "name": f"VIP {i}",
                "phone": f"+420{i}88888888",
                "email": f"multi{i}_{unique_email}",
                "tags": ["vip", unique_tag]
            })
            cleanup_couriers.append(c["id"])
            # Různé vzdálenosti
            lat = 50.0815 + (i * 0.005)  # Každý ~0.5km dál
            courier_api.set_available_with_location(c["id"], lat, 14.4195)
            couriers.append(c)

        # VIP objednávka s unique_tag pro izolaci
        order = order_api.create_order({
            "customer_name": "Multi VIP Test",
            "customer_phone": "+420555666777",
            "pickup_address": "Národní",
            "pickup_lat": PRAGUE_CENTER[0],
            "pickup_lng": PRAGUE_CENTER[1],
            "delivery_address": "Test 2",
            "delivery_lat": 50.087,
            "delivery_lng": 14.421,
            "is_vip": True,
            "required_tags": [unique_tag]
        })
        cleanup_orders.append(order["id"])

        result = dispatch_api.auto_dispatch(order["id"])

        assert result["success"] is True
        # První (nejbližší) by měl být vybrán
        assert result["courier_id"] == couriers[0]["id"]
