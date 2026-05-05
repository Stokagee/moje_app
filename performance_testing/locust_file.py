from locust import HttpUser, task, between
from faker import Faker
import uuid
import my_jtl_listnener 


fake = Faker("cs_CZ")

class FormUser(HttpUser):
    """Jednoduchý Locust test pro POST api/v1/form/ endpoint."""
    
    host = "http://localhost:20300"
    
    wait_time = between(1, 3)
    @task
    def create_form(self):
        """Odesílá POST požadavek s náhodnými daty."""
        data = {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "phone": fake.phone_number(),
                "gender": "male",
                "email": f"{fake.user_name()}_{uuid.uuid4().hex[:6]}@seznam.cz"
        }
        self.client.post("/api/v1/form/", json=data, name="Testuju první část API")