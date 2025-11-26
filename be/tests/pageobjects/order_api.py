"""Page Object pro Order API."""
from typing import Dict, List, Optional
from .api_client import APIClient


class OrderAPI:
    """Order API wrapper."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.base_endpoint = "/api/v1/orders"

    def create_order(self, data: Dict) -> Dict:
        """Vytvořit novou objednávku."""
        response = self.api_client.post(f"{self.base_endpoint}/", data)
        response.raise_for_status()
        return response.json()

    def get_order(self, order_id: int) -> Dict:
        """Získat objednávku podle ID."""
        response = self.api_client.get(f"{self.base_endpoint}/{order_id}")
        response.raise_for_status()
        return response.json()

    def get_order_safe(self, order_id: int) -> Optional[Dict]:
        """Získat objednávku, vrátí None pokud neexistuje."""
        response = self.api_client.get(f"{self.base_endpoint}/{order_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def get_all_orders(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Získat všechny objednávky."""
        response = self.api_client.get(
            f"{self.base_endpoint}/",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def get_pending_orders(self) -> List[Dict]:
        """Získat čekající objednávky (SEARCHING)."""
        response = self.api_client.get(f"{self.base_endpoint}/pending")
        response.raise_for_status()
        return response.json()

    def get_orders_by_status(self, status: str) -> List[Dict]:
        """Získat objednávky podle statusu."""
        response = self.api_client.get(f"{self.base_endpoint}/by-status/{status}")
        response.raise_for_status()
        return response.json()

    def update_status(self, order_id: int, status: str) -> Dict:
        """Aktualizovat status objednávky."""
        response = self.api_client.patch(
            f"{self.base_endpoint}/{order_id}/status",
            {"status": status}
        )
        response.raise_for_status()
        return response.json()

    def pickup_order(self, order_id: int) -> Dict:
        """Označit objednávku jako vyzvednutou."""
        response = self.api_client.post(f"{self.base_endpoint}/{order_id}/pickup")
        response.raise_for_status()
        return response.json()

    def deliver_order(self, order_id: int) -> Dict:
        """Označit objednávku jako doručenou."""
        response = self.api_client.post(f"{self.base_endpoint}/{order_id}/deliver")
        response.raise_for_status()
        return response.json()

    def cancel_order(self, order_id: int) -> Dict:
        """Zrušit objednávku."""
        response = self.api_client.post(f"{self.base_endpoint}/{order_id}/cancel")
        response.raise_for_status()
        return response.json()

    def delete_order(self, order_id: int) -> None:
        """Smazat objednávku."""
        response = self.api_client.delete(f"{self.base_endpoint}/{order_id}")
        response.raise_for_status()

    def delete_order_safe(self, order_id: int) -> bool:
        """Smazat objednávku, vrátí False pokud neexistuje."""
        response = self.api_client.delete(f"{self.base_endpoint}/{order_id}")
        return response.status_code == 204

    # Raw methods pro testování chybových stavů
    def create_order_raw(self, data: Dict):
        """Vytvořit objednávku - vrátí response objekt."""
        return self.api_client.post(f"{self.base_endpoint}/", data)

    def get_order_raw(self, order_id: int):
        """Získat objednávku - vrátí response objekt."""
        return self.api_client.get(f"{self.base_endpoint}/{order_id}")

    def delete_order_raw(self, order_id: int):
        """Smazat objednávku - vrátí response objekt."""
        return self.api_client.delete(f"{self.base_endpoint}/{order_id}")

    def pickup_order_raw(self, order_id: int):
        """Pickup - vrátí response objekt."""
        return self.api_client.post(f"{self.base_endpoint}/{order_id}/pickup")

    def deliver_order_raw(self, order_id: int):
        """Deliver - vrátí response objekt."""
        return self.api_client.post(f"{self.base_endpoint}/{order_id}/deliver")

    def cancel_order_raw(self, order_id: int):
        """Cancel - vrátí response objekt."""
        return self.api_client.post(f"{self.base_endpoint}/{order_id}/cancel")
