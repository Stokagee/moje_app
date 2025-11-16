import requests
import json
from typing import Dict, List, Optional

class APIClient:
    """Base API client for testing FastAPI endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """GET request"""
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """POST request"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        return self.session.post(url, json=data, headers=headers)

    def delete(self, endpoint: str) -> requests.Response:
        """DELETE request"""
        url = f"{self.base_url}{endpoint}"
        return self.session.delete(url)

    def close(self):
        """Close the session"""
        self.session.close()