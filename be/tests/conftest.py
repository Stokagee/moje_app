"""Pytest fixtures pro Food Delivery API testy."""
import os
import sys
import pytest
from uuid import uuid4

# Přidej tests/ do path pro správné importy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pageobjects.api_client import APIClient
from pageobjects.courier_api import CourierAPI
from pageobjects.order_api import OrderAPI
from pageobjects.dispatch_api import DispatchAPI


# Base URL z ENV nebo default
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="function")
def api_client():
    """HTTP client pro API."""
    client = APIClient(API_BASE_URL)
    yield client
    client.close()


@pytest.fixture
def courier_api(api_client):
    """Courier API Page Object."""
    return CourierAPI(api_client)


@pytest.fixture
def order_api(api_client):
    """Order API Page Object."""
    return OrderAPI(api_client)


@pytest.fixture
def dispatch_api(api_client):
    """Dispatch API Page Object."""
    return DispatchAPI(api_client)


@pytest.fixture
def unique_email():
    """Generuje unikátní email pro každý test."""
    return f"courier_{uuid4().hex[:8]}@test.cz"


@pytest.fixture
def unique_tag():
    """Generuje unikátní tag pro izolaci testů."""
    return f"test_{uuid4().hex[:8]}"


@pytest.fixture
def sample_courier(unique_email):
    """Vzorový kurýr."""
    return {
        "name": "Jan Novák",
        "phone": "+420123456789",
        "email": unique_email,
        "tags": ["bike", "fast"]
    }


@pytest.fixture
def sample_courier_vip(unique_email):
    """Vzorový VIP kurýr."""
    return {
        "name": "Petr VIP",
        "phone": "+420111222333",
        "email": f"vip_{unique_email}",
        "tags": ["car", "vip", "fast"]
    }


@pytest.fixture
def sample_order():
    """Vzorová objednávka."""
    return {
        "customer_name": "Petr Svoboda",
        "customer_phone": "+420987654321",
        "pickup_address": "Národní 10, Praha",
        "pickup_lat": 50.0815,
        "pickup_lng": 14.4195,
        "delivery_address": "Václavské náměstí 1, Praha",
        "delivery_lat": 50.0819,
        "delivery_lng": 14.4271,
        "is_vip": False,
        "required_tags": []
    }


@pytest.fixture
def sample_order_vip():
    """Vzorová VIP objednávka."""
    return {
        "customer_name": "VIP Zákazník",
        "customer_phone": "+420555666777",
        "pickup_address": "Pařížská 1, Praha",
        "pickup_lat": 50.0900,
        "pickup_lng": 14.4180,
        "delivery_address": "Staroměstské náměstí 1, Praha",
        "delivery_lat": 50.0870,
        "delivery_lng": 14.4210,
        "is_vip": True,
        "required_tags": []
    }


@pytest.fixture
def sample_order_with_tags():
    """Objednávka s požadovanými tagy."""
    return {
        "customer_name": "Fragile Zákazník",
        "customer_phone": "+420888999000",
        "pickup_address": "Na Příkopě 1, Praha",
        "pickup_lat": 50.0840,
        "pickup_lng": 14.4280,
        "delivery_address": "Můstek 1, Praha",
        "delivery_lat": 50.0830,
        "delivery_lng": 14.4260,
        "is_vip": False,
        "required_tags": ["fragile_ok"]
    }


# GPS lokace pro testování vzdáleností
PRAGUE_CENTER = (50.0815, 14.4195)  # Národní třída
PRAGUE_1KM = (50.0905, 14.4195)     # ~1km na sever
PRAGUE_2KM = (50.0995, 14.4195)     # ~2km na sever
PRAGUE_3KM = (50.1085, 14.4195)     # ~3km na sever
PRAGUE_5KM = (50.1265, 14.4195)     # ~5km na sever
PRAGUE_10KM = (50.1715, 14.4195)    # ~10km na sever


@pytest.fixture
def cleanup_couriers(courier_api):
    """Fixture pro automatický cleanup kurýrů po testu."""
    created_ids = []
    yield created_ids
    for cid in created_ids:
        try:
            courier_api.delete_courier_safe(cid)
        except Exception:
            pass


@pytest.fixture
def cleanup_orders(order_api):
    """Fixture pro automatický cleanup objednávek po testu."""
    created_ids = []
    yield created_ids
    for oid in created_ids:
        try:
            order_api.delete_order_safe(oid)
        except Exception:
            pass


@pytest.fixture
def created_courier(courier_api, sample_courier, cleanup_couriers):
    """Vytvoří kurýra a automaticky ho smaže po testu."""
    courier = courier_api.create_courier(sample_courier)
    cleanup_couriers.append(courier["id"])
    return courier


@pytest.fixture
def created_order(order_api, sample_order, cleanup_orders):
    """Vytvoří objednávku a automaticky ji smaže po testu."""
    order = order_api.create_order(sample_order)
    cleanup_orders.append(order["id"])
    return order


@pytest.fixture
def available_courier_near(courier_api, unique_email, cleanup_couriers):
    """Vytvoří available kurýra blízko centra Prahy (~1km)."""
    courier = courier_api.create_courier({
        "name": "Blízký Kurýr",
        "phone": "+420111111111",
        "email": f"near_{unique_email}",
        "tags": ["bike"]
    })
    cleanup_couriers.append(courier["id"])
    courier_api.set_available_with_location(courier["id"], *PRAGUE_1KM)
    return courier_api.get_courier(courier["id"])


@pytest.fixture
def available_courier_far(courier_api, unique_email, cleanup_couriers):
    """Vytvoří available kurýra daleko od centra (~5km)."""
    courier = courier_api.create_courier({
        "name": "Vzdálený Kurýr",
        "phone": "+420222222222",
        "email": f"far_{unique_email}",
        "tags": ["car"]
    })
    cleanup_couriers.append(courier["id"])
    courier_api.set_available_with_location(courier["id"], *PRAGUE_5KM)
    return courier_api.get_courier(courier["id"])
