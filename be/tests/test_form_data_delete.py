import pytest
from tests.pageobjects.api_client import APIClient
from tests.pageobjects.form_data_api import FormDataAPI

class TestFormDataDelete:
    """Test cases for Form Data DELETE endpoint."""

    @pytest.fixture
    def api_client(self):
        """Fixture for API client."""
        client = APIClient("http://localhost:8000")
        yield client
        client.close()

    @pytest.fixture
    def form_data_api(self, api_client):
        """Fixture for FormData API page object."""
        return FormDataAPI(api_client)

    @pytest.fixture
    def sample_form_data(self):
        """Sample form data for testing."""
        return {
            "first_name": "Jan",
            "last_name": "Novák",
            "phone": "123456789",
            "gender": "male",
            "email": "jan.novak@example.com"
        }

    def test_delete_existing_form_data(self, form_data_api, sample_form_data):
        """Test successful deletion of existing form data."""
        # Create test data
        created_data = form_data_api.create_form_data(sample_form_data)
        form_data_id = created_data["id"]

        # Verify data exists
        assert form_data_api.is_form_data_exists(form_data_id)

        # Delete the data
        delete_response = form_data_api.delete_form_data(form_data_id)

        # Verify deletion response
        assert "message" in delete_response
        assert "úspěšně smazán" in delete_response["message"]

        # Verify data no longer exists
        assert not form_data_api.is_form_data_exists(form_data_id)

    def test_delete_nonexistent_form_data(self, form_data_api):
        """Test deletion of non-existent form data returns 404."""
        # Try to delete non-existent record
        response = form_data_api.api_client.delete(f"{form_data_api.base_endpoint}/99999")

        # Should return 404
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "nenalezen" in error_data["detail"]

    def test_delete_and_verify_count_decreases(self, form_data_api, sample_form_data):
        """Test that count decreases after deletion."""
        # Get initial count
        initial_count = form_data_api.get_form_data_count()

        # Create test data
        created_data = form_data_api.create_form_data(sample_form_data)
        form_data_id = created_data["id"]

        # Verify count increased
        assert form_data_api.get_form_data_count() == initial_count + 1

        # Delete the data
        form_data_api.delete_form_data(form_data_id)

        # Verify count decreased back
        assert form_data_api.get_form_data_count() == initial_count

    def test_delete_form_data_by_email_workflow(self, form_data_api, sample_form_data):
        """Test complete workflow: create, find by email, delete."""
        # Create test data
        created_data = form_data_api.create_form_data(sample_form_data)

        # Find by email
        found_data = form_data_api.find_form_data_by_email(sample_form_data["email"])
        assert found_data is not None
        assert found_data["id"] == created_data["id"]

        # Delete by ID
        form_data_api.delete_form_data(found_data["id"])

        # Verify no longer found by email
        not_found_data = form_data_api.find_form_data_by_email(sample_form_data["email"])
        assert not_found_data is None