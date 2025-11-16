from typing import Dict, List, Optional
from .api_client import APIClient

class FormDataAPI:
    """Page Object for Form Data API endpoints."""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.base_endpoint = "/api/v1/form"

    def create_form_data(self, form_data: Dict) -> Dict:
        """Create new form data record."""
        response = self.api_client.post(f"{self.base_endpoint}/", form_data)
        response.raise_for_status()
        return response.json()

    def get_all_form_data(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Get all form data records."""
        params = {"skip": skip, "limit": limit}
        response = self.api_client.get(f"{self.base_endpoint}/", params)
        response.raise_for_status()
        return response.json()

    def get_form_data_by_id(self, form_data_id: int) -> Dict:
        """Get single form data record by ID."""
        response = self.api_client.get(f"{self.base_endpoint}/{form_data_id}")
        response.raise_for_status()
        return response.json()

    def delete_form_data(self, form_data_id: int) -> Dict:
        """Delete form data record by ID."""
        response = self.api_client.delete(f"{self.base_endpoint}/{form_data_id}")
        response.raise_for_status()
        return response.json()

    def is_form_data_exists(self, form_data_id: int) -> bool:
        """Check if form data record exists."""
        response = self.api_client.get(f"{self.base_endpoint}/{form_data_id}")
        return response.status_code == 200

    def get_form_data_count(self) -> int:
        """Get total count of form data records."""
        all_data = self.get_all_form_data()
        return len(all_data)

    def find_form_data_by_email(self, email: str) -> Optional[Dict]:
        """Find form data record by email."""
        all_data = self.get_all_form_data()
        for item in all_data:
            if item.get("email") == email:
                return item
        return None