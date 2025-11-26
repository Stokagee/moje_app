"""Testy pro správu statusu kurýrů."""
import pytest


class TestCourierStatus:
    """Testy pro status management kurýrů."""

    def test_courier_default_status_offline(self, courier_api, sample_courier, cleanup_couriers):
        """Test že nový kurýr má default status offline."""
        courier = courier_api.create_courier(sample_courier)
        cleanup_couriers.append(courier["id"])

        assert courier["status"] == "offline"

    def test_update_status_to_available(self, courier_api, created_courier):
        """Test změny statusu na available."""
        updated = courier_api.update_status(created_courier["id"], "available")

        assert updated["status"] == "available"

    def test_update_status_to_busy(self, courier_api, created_courier):
        """Test změny statusu na busy."""
        updated = courier_api.update_status(created_courier["id"], "busy")

        assert updated["status"] == "busy"

    def test_update_status_to_offline(self, courier_api, created_courier):
        """Test změny statusu na offline."""
        # Nejdřív nastavíme available
        courier_api.update_status(created_courier["id"], "available")

        # Pak zpět na offline
        updated = courier_api.update_status(created_courier["id"], "offline")

        assert updated["status"] == "offline"

    def test_update_location(self, courier_api, created_courier):
        """Test aktualizace GPS lokace."""
        lat, lng = 50.0815, 14.4195

        updated = courier_api.update_location(created_courier["id"], lat, lng)

        assert updated["lat"] == lat
        assert updated["lng"] == lng

    def test_update_location_not_found(self, courier_api):
        """Test aktualizace lokace neexistujícího kurýra."""
        response = courier_api.update_location_raw(999999, 50.0, 14.0)
        assert response.status_code == 404

    def test_get_available_couriers(self, courier_api, unique_email, cleanup_couriers):
        """Test získání pouze available kurýrů."""
        # Vytvoříme 3 kurýry s různými statusy
        c1 = courier_api.create_courier({
            "name": "Available",
            "phone": "+420111111111",
            "email": f"av_{unique_email}",
            "tags": []
        })
        cleanup_couriers.append(c1["id"])
        courier_api.update_status(c1["id"], "available")

        c2 = courier_api.create_courier({
            "name": "Busy",
            "phone": "+420222222222",
            "email": f"busy_{unique_email}",
            "tags": []
        })
        cleanup_couriers.append(c2["id"])
        courier_api.update_status(c2["id"], "busy")

        c3 = courier_api.create_courier({
            "name": "Offline",
            "phone": "+420333333333",
            "email": f"off_{unique_email}",
            "tags": []
        })
        cleanup_couriers.append(c3["id"])
        # c3 zůstane offline (default)

        available = courier_api.get_available_couriers()
        available_ids = [c["id"] for c in available]

        assert c1["id"] in available_ids
        assert c2["id"] not in available_ids
        assert c3["id"] not in available_ids

    def test_get_available_couriers_empty(self, courier_api, created_courier):
        """Test když není žádný available kurýr."""
        # created_courier je offline (default)
        available = courier_api.get_available_couriers()

        # Může být prázdný nebo neobsahuje našeho kurýra
        available_ids = [c["id"] for c in available]
        assert created_courier["id"] not in available_ids
