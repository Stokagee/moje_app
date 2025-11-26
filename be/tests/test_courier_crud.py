"""Testy pro CRUD operace kurýrů."""
import pytest


class TestCourierCRUD:
    """Testy pro Courier CRUD operace."""

    def test_create_courier_success(self, courier_api, sample_courier, cleanup_couriers):
        """Test vytvoření kurýra."""
        courier = courier_api.create_courier(sample_courier)
        cleanup_couriers.append(courier["id"])

        assert courier["id"] is not None
        assert courier["name"] == sample_courier["name"]
        assert courier["email"] == sample_courier["email"]
        assert courier["phone"] == sample_courier["phone"]
        assert courier["tags"] == sample_courier["tags"]

    def test_create_courier_duplicate_email(self, courier_api, sample_courier, cleanup_couriers):
        """Test vytvoření kurýra s duplicitním emailem."""
        courier = courier_api.create_courier(sample_courier)
        cleanup_couriers.append(courier["id"])

        # Druhý pokus se stejným emailem
        response = courier_api.create_courier_raw(sample_courier)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_courier_with_tags(self, courier_api, unique_email, cleanup_couriers):
        """Test vytvoření kurýra s různými tagy."""
        data = {
            "name": "Tagovaný Kurýr",
            "phone": "+420999888777",
            "email": unique_email,
            "tags": ["bike", "vip", "fragile_ok", "fast"]
        }
        courier = courier_api.create_courier(data)
        cleanup_couriers.append(courier["id"])

        assert courier["tags"] == ["bike", "vip", "fragile_ok", "fast"]

    def test_create_courier_empty_tags(self, courier_api, unique_email, cleanup_couriers):
        """Test vytvoření kurýra bez tagů."""
        data = {
            "name": "Bez Tagů",
            "phone": "+420111222333",
            "email": unique_email,
            "tags": []
        }
        courier = courier_api.create_courier(data)
        cleanup_couriers.append(courier["id"])

        assert courier["tags"] == []

    def test_get_courier_by_id(self, courier_api, created_courier):
        """Test získání kurýra podle ID."""
        courier = courier_api.get_courier(created_courier["id"])

        assert courier["id"] == created_courier["id"]
        assert courier["name"] == created_courier["name"]
        assert courier["email"] == created_courier["email"]

    def test_get_courier_not_found(self, courier_api):
        """Test získání neexistujícího kurýra."""
        response = courier_api.get_courier_raw(999999)
        assert response.status_code == 404

    def test_get_all_couriers(self, courier_api, sample_courier, unique_email, cleanup_couriers):
        """Test získání seznamu kurýrů."""
        # Zapamatujeme si kolik kurýrů je před testem
        before_count = len(courier_api.get_all_couriers(limit=1000))

        # Vytvoříme dva kurýry
        c1 = courier_api.create_courier(sample_courier)
        cleanup_couriers.append(c1["id"])

        c2_data = sample_courier.copy()
        c2_data["email"] = f"second_{unique_email}"
        c2 = courier_api.create_courier(c2_data)
        cleanup_couriers.append(c2["id"])

        # Získáme seznam s dostatečným limitem
        couriers = courier_api.get_all_couriers(limit=1000)
        courier_ids = [c["id"] for c in couriers]

        # Ověříme že nově vytvoření kurýři jsou v seznamu
        assert c1["id"] in courier_ids
        assert c2["id"] in courier_ids
        assert len(couriers) >= before_count + 2

    def test_get_all_couriers_pagination(self, courier_api, unique_email, cleanup_couriers):
        """Test stránkování seznamu kurýrů."""
        # Vytvoříme 5 kurýrů
        created_ids = []
        for i in range(5):
            c = courier_api.create_courier({
                "name": f"Kurýr {i}",
                "phone": f"+42000000000{i}",
                "email": f"page_{i}_{unique_email}",
                "tags": []
            })
            cleanup_couriers.append(c["id"])
            created_ids.append(c["id"])

        # Test limit - měli bychom dostat max 2 záznamy
        limited = courier_api.get_all_couriers(skip=0, limit=2)
        assert len(limited) == 2

        # Test skip - měli bychom přeskočit první 2 záznamy
        first_two = courier_api.get_all_couriers(skip=0, limit=2)
        skipped = courier_api.get_all_couriers(skip=2, limit=2)
        # Přeskočená data by měla být jiná než první
        first_ids = {c["id"] for c in first_two}
        skipped_ids = {c["id"] for c in skipped}
        assert first_ids.isdisjoint(skipped_ids)

    def test_update_courier_name(self, courier_api, created_courier):
        """Test změny jména kurýra."""
        updated = courier_api.update_courier(
            created_courier["id"],
            {"name": "Nové Jméno"}
        )

        assert updated["name"] == "Nové Jméno"
        assert updated["email"] == created_courier["email"]

    def test_update_courier_tags(self, courier_api, created_courier):
        """Test změny tagů kurýra."""
        updated = courier_api.update_courier(
            created_courier["id"],
            {"tags": ["car", "vip"]}
        )

        assert updated["tags"] == ["car", "vip"]

    def test_delete_courier(self, courier_api, sample_courier):
        """Test smazání kurýra."""
        courier = courier_api.create_courier(sample_courier)
        courier_id = courier["id"]

        # Ověříme že existuje
        assert courier_api.get_courier_safe(courier_id) is not None

        # Smažeme
        courier_api.delete_courier(courier_id)

        # Ověříme že neexistuje
        assert courier_api.get_courier_safe(courier_id) is None

    def test_delete_courier_not_found(self, courier_api):
        """Test smazání neexistujícího kurýra."""
        response = courier_api.delete_courier_raw(999999)
        assert response.status_code == 404
