"""Page Object pro Courier API."""
from typing import Dict, List, Optional
from .api_client import APIClient


class CourierAPI:
    """Courier API wrapper."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.base_endpoint = "/api/v1/couriers"

    def create_courier(self, data: Dict) -> Dict:
        """Vytvořit nového kurýra."""
        response = self.api_client.post(f"{self.base_endpoint}/", data)
        response.raise_for_status()
        return response.json()

    def get_courier(self, courier_id: int) -> Dict:
        """Získat kurýra podle ID."""
        response = self.api_client.get(f"{self.base_endpoint}/{courier_id}")
        response.raise_for_status()
        return response.json()

    def get_courier_safe(self, courier_id: int) -> Optional[Dict]:
        """Získat kurýra, vrátí None pokud neexistuje."""
        response = self.api_client.get(f"{self.base_endpoint}/{courier_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    def get_all_couriers(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Získat všechny kurýry."""
        response = self.api_client.get(
            f"{self.base_endpoint}/",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def get_available_couriers(self) -> List[Dict]:
        """Získat dostupné kurýry."""
        response = self.api_client.get(f"{self.base_endpoint}/available")
        response.raise_for_status()
        return response.json()

    def update_courier(self, courier_id: int, data: Dict) -> Dict:
        """Aktualizovat kurýra."""
        response = self.api_client.put(f"{self.base_endpoint}/{courier_id}", data)
        response.raise_for_status()
        return response.json()

    def update_location(self, courier_id: int, lat: float, lng: float) -> Dict:
        """Aktualizovat GPS pozici."""
        response = self.api_client.patch(
            f"{self.base_endpoint}/{courier_id}/location",
            {"lat": lat, "lng": lng}
        )
        response.raise_for_status()
        return response.json()

    def update_status(self, courier_id: int, status: str) -> Dict:
        """Aktualizovat status kurýra."""
        response = self.api_client.patch(
            f"{self.base_endpoint}/{courier_id}/status",
            {"status": status}
        )
        response.raise_for_status()
        return response.json()

    def delete_courier(self, courier_id: int) -> None:
        """Smazat kurýra."""
        response = self.api_client.delete(f"{self.base_endpoint}/{courier_id}")
        response.raise_for_status()

    def delete_courier_safe(self, courier_id: int) -> bool:
        """Smazat kurýra, vrátí False pokud neexistuje."""
        response = self.api_client.delete(f"{self.base_endpoint}/{courier_id}")
        return response.status_code == 204

    def set_available_with_location(self, courier_id: int, lat: float, lng: float) -> Dict:
        """Nastavit kurýra jako available s lokací."""
        self.update_status(courier_id, "available")
        return self.update_location(courier_id, lat, lng)

    def create_courier_raw(self, data: Dict):
        """Vytvořit kurýra - vrátí response objekt."""
        return self.api_client.post(f"{self.base_endpoint}/", data)

    def get_courier_raw(self, courier_id: int):
        """Získat kurýra - vrátí response objekt."""
        return self.api_client.get(f"{self.base_endpoint}/{courier_id}")

    def delete_courier_raw(self, courier_id: int):
        """Smazat kurýra - vrátí response objekt."""
        return self.api_client.delete(f"{self.base_endpoint}/{courier_id}")

    def update_status_raw(self, courier_id: int, status: str):
        """Aktualizovat status - vrátí response objekt."""
        return self.api_client.patch(
            f"{self.base_endpoint}/{courier_id}/status",
            {"status": status}
        )

    def update_location_raw(self, courier_id: int, lat: float, lng: float):
        """Aktualizovat lokaci - vrátí response objekt."""
        return self.api_client.patch(
            f"{self.base_endpoint}/{courier_id}/location",
            {"lat": lat, "lng": lng}
        )
