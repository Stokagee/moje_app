#!/usr/bin/env python3
"""
Rychlý test DELETE endpointu
Spusťte: python quick_test.py
"""

import requests
import json

def test_delete():
    base_url = "http://localhost:8000"
    print("🧪 Rychlý test DELETE endpointu...")

    # 1. Vytvoření testovacích dat
    print("\n1. Vytváření testovacích dat...")
    test_data = {
        "first_name": "Test",
        "last_name": "Delete",
        "phone": "123456789",
        "gender": "male",
        "email": "test.delete@example.com"
    }

    try:
        response = requests.post(f"{base_url}/api/v1/form/", json=test_data)
        if response.status_code == 200:
            data = response.json()
            form_id = data["id"]
            print(f"✅ Vytvořeno s ID: {form_id}")
        else:
            print(f"❌ Chyba při vytváření: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Chyba: {e}")
        return

    # 2. Smazání dat
    print("\n2. Mazání dat...")
    try:
        response = requests.delete(f"{base_url}/api/v1/form/{form_id}")
        if response.status_code == 200:
            print("✅ Úspěšně smazáno!")
            print(f"Odpověď: {response.json()}")
        else:
            print(f"❌ Chyba při mazání: {response.status_code}")
            print(f"Odpověď: {response.text}")
    except Exception as e:
        print(f"❌ Chyba: {e}")

    # 3. Ověření smazání
    print("\n3. Ověření smazání...")
    try:
        response = requests.get(f"{base_url}/api/v1/form/{form_id}")
        if response.status_code == 404:
            print("✅ Ověřeno - data smazána!")
        else:
            print(f"❌ Data stále existují: {response.status_code}")
    except Exception as e:
        print(f"❌ Chyba: {e}")

if __name__ == "__main__":
    print("🚀 Spouštění rychlého testu DELETE endpointu")
    print("Ujistěte se, že backend server běží na http://localhost:8000")

    test_delete()
    print("\n🎉 Test dokončen!")