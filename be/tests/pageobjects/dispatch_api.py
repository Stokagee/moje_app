"""Page Object pro Dispatch API."""
from typing import Dict, List
from .api_client import APIClient


class DispatchAPI:
    """Dispatch API wrapper."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.base_endpoint = "/api/v1/dispatch"

    def auto_dispatch(self, order_id: int) -> Dict:
        """Automatický dispatch objednávky."""
        response = self.api_client.post(f"{self.base_endpoint}/auto/{order_id}")
        response.raise_for_status()
        return response.json()

    def auto_dispatch_raw(self, order_id: int):
        """Automatický dispatch - vrátí response objekt."""
        return self.api_client.post(f"{self.base_endpoint}/auto/{order_id}")

    def manual_dispatch(self, order_id: int, courier_id: int) -> Dict:
        """Manuální dispatch objednávky."""
        response = self.api_client.post(
            f"{self.base_endpoint}/manual",
            {"order_id": order_id, "courier_id": courier_id}
        )
        response.raise_for_status()
        return response.json()

    def manual_dispatch_raw(self, order_id: int, courier_id: int):
        """Manuální dispatch - vrátí response objekt."""
        return self.api_client.post(
            f"{self.base_endpoint}/manual",
            {"order_id": order_id, "courier_id": courier_id}
        )

    def get_available_couriers_for_order(
        self, order_id: int, radius_km: float = 10.0
    ) -> Dict:
        """Získat dostupné kurýry pro objednávku."""
        response = self.api_client.get(
            f"{self.base_endpoint}/available-couriers/{order_id}",
            params={"radius_km": radius_km}
        )
        response.raise_for_status()
        return response.json()

    def get_logs_for_order(self, order_id: int) -> List[Dict]:
        """Získat dispatch logy pro objednávku."""
        response = self.api_client.get(f"{self.base_endpoint}/logs/order/{order_id}")
        response.raise_for_status()
        return response.json()

    def get_logs_for_courier(self, courier_id: int) -> List[Dict]:
        """Získat dispatch logy pro kurýra."""
        response = self.api_client.get(f"{self.base_endpoint}/logs/courier/{courier_id}")
        response.raise_for_status()
        return response.json()
