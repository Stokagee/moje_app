"""Pydantic schémata pro objednávky.

Tento modul definuje datové struktury pro práci s objednávkami v API.
Objednávka představuje požadavek na doručení od místa vyzvednutí k zákazníkovi.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus


class OrderBase(BaseModel):
    """Základní atributy objednávky společné pro vytváření i odpovědi."""

    customer_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Jméno zákazníka, který objednávku přijímá",
        json_schema_extra={"example": "Marie Svobodová"}
    )
    customer_phone: str = Field(
        ...,
        min_length=9,
        max_length=20,
        description="Telefonní číslo zákazníka pro kontakt při doručení",
        json_schema_extra={"example": "+420606123456"}
    )
    pickup_address: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Adresa místa vyzvednutí (restaurace, obchod)",
        json_schema_extra={"example": "Národní 25, Praha 1"}
    )
    pickup_lat: float = Field(
        ...,
        ge=-90,
        le=90,
        description="GPS šířka místa vyzvednutí",
        json_schema_extra={"example": 50.0815}
    )
    pickup_lng: float = Field(
        ...,
        ge=-180,
        le=180,
        description="GPS délka místa vyzvednutí",
        json_schema_extra={"example": 14.4195}
    )
    delivery_address: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Adresa doručení k zákazníkovi",
        json_schema_extra={"example": "Vinohradská 50, Praha 2"}
    )
    delivery_lat: float = Field(
        ...,
        ge=-90,
        le=90,
        description="GPS šířka místa doručení",
        json_schema_extra={"example": 50.0755}
    )
    delivery_lng: float = Field(
        ...,
        ge=-180,
        le=180,
        description="GPS délka místa doručení",
        json_schema_extra={"example": 14.4378}
    )
    is_vip: bool = Field(
        default=False,
        description="""VIP příznak objednávky.

        VIP objednávky mají prioritu při přiřazování kurýra:
        - Preferují se kurýři s tagem `vip`
        - Pokud žádný VIP kurýr není k dispozici, přiřadí se běžný kurýr
        """,
        json_schema_extra={"example": False}
    )
    required_tags: List[str] = Field(
        default=[],
        description="""Seznam tagů, které musí mít kurýr pro tuto objednávku.

        Běžné tagy:
        - `fragile_ok` - objednávka obsahuje křehké zboží
        - `fast` - expresní doručení
        - `bike` / `car` - specifický typ dopravy

        Kurýr MUSÍ mít VŠECHNY požadované tagy, aby mohl objednávku převzít.
        """,
        json_schema_extra={"example": ["fragile_ok"]}
    )


class OrderCreate(OrderBase):
    """Schéma pro vytvoření nové objednávky.

    Po vytvoření je objednávka ve stavu `CREATED`.
    Pro přiřazení kurýra použijte endpoint `/dispatch/auto/{order_id}`.

    ## Životní cyklus objednávky

    1. **CREATED** - Objednávka vytvořena, čeká na dispatch
    2. **SEARCHING** - Hledá se vhodný kurýr
    3. **ASSIGNED** - Kurýr přiřazen, míří k vyzvednutí
    4. **PICKED** - Kurýr vyzvednul objednávku
    5. **DELIVERED** - Doručeno zákazníkovi
    6. **CANCELLED** - Objednávka zrušena (může nastat kdykoli před DELIVERED)

    ## Příklad vytvoření

    ```json
    {
        "customer_name": "Marie Svobodová",
        "customer_phone": "+420606123456",
        "pickup_address": "Národní 25, Praha 1",
        "pickup_lat": 50.0815,
        "pickup_lng": 14.4195,
        "delivery_address": "Vinohradská 50, Praha 2",
        "delivery_lat": 50.0755,
        "delivery_lng": 14.4378,
        "is_vip": false,
        "required_tags": []
    }
    ```
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_name": "Marie Svobodová",
                "customer_phone": "+420606123456",
                "pickup_address": "Národní 25, Praha 1",
                "pickup_lat": 50.0815,
                "pickup_lng": 14.4195,
                "delivery_address": "Vinohradská 50, Praha 2",
                "delivery_lat": 50.0755,
                "delivery_lng": 14.4378,
                "is_vip": False,
                "required_tags": []
            }
        }
    )


class OrderStatusUpdate(BaseModel):
    """Schéma pro manuální změnu stavu objednávky.

    ## Možné stavy

    | Stav | Popis | Následující stav |
    |------|-------|------------------|
    | `CREATED` | Nově vytvořená | SEARCHING |
    | `SEARCHING` | Hledá se kurýr | ASSIGNED |
    | `ASSIGNED` | Kurýr přiřazen | PICKED |
    | `PICKED` | Vyzvednuto | DELIVERED |
    | `DELIVERED` | Doručeno | - (konec) |
    | `CANCELLED` | Zrušeno | - (konec) |

    ## Upozornění

    Pro běžné operace používejte specifické endpointy:
    - `/orders/{id}/pickup` - pro označení vyzvednutí
    - `/orders/{id}/deliver` - pro označení doručení
    - `/orders/{id}/cancel` - pro zrušení

    Tento endpoint je určen pro administrativní účely.
    """

    status: OrderStatus = Field(
        ...,
        description="Nový stav objednávky",
        json_schema_extra={"example": "ASSIGNED"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ASSIGNED"
            }
        }
    )


class OrderResponse(OrderBase):
    """Kompletní odpověď s daty objednávky.

    Vrací se při GET operacích a po vytvoření/aktualizaci objednávky.

    ## Příklad odpovědi

    ```json
    {
        "id": 42,
        "customer_name": "Marie Svobodová",
        "customer_phone": "+420606123456",
        "pickup_address": "Národní 25, Praha 1",
        "pickup_lat": 50.0815,
        "pickup_lng": 14.4195,
        "delivery_address": "Vinohradská 50, Praha 2",
        "delivery_lat": 50.0755,
        "delivery_lng": 14.4378,
        "is_vip": false,
        "required_tags": [],
        "status": "ASSIGNED",
        "courier_id": 5,
        "created_at": "2024-01-15T12:00:00",
        "updated_at": "2024-01-15T12:05:00"
    }
    ```
    """

    id: int = Field(
        ...,
        description="Unikátní identifikátor objednávky",
        json_schema_extra={"example": 42}
    )
    status: OrderStatus = Field(
        ...,
        description="Aktuální stav objednávky",
        json_schema_extra={"example": "ASSIGNED"}
    )
    courier_id: Optional[int] = Field(
        default=None,
        description="ID přiřazeného kurýra (null pokud ještě není přiřazen)",
        json_schema_extra={"example": 5}
    )
    created_at: datetime = Field(
        ...,
        description="Datum a čas vytvoření objednávky",
        json_schema_extra={"example": "2024-01-15T12:00:00"}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Datum a čas poslední změny stavu",
        json_schema_extra={"example": "2024-01-15T12:05:00"}
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 42,
                "customer_name": "Marie Svobodová",
                "customer_phone": "+420606123456",
                "pickup_address": "Národní 25, Praha 1",
                "pickup_lat": 50.0815,
                "pickup_lng": 14.4195,
                "delivery_address": "Vinohradská 50, Praha 2",
                "delivery_lat": 50.0755,
                "delivery_lng": 14.4378,
                "is_vip": False,
                "required_tags": [],
                "status": "ASSIGNED",
                "courier_id": 5,
                "created_at": "2024-01-15T12:00:00",
                "updated_at": "2024-01-15T12:05:00"
            }
        }
    )


class OrderWithCourier(OrderResponse):
    """Rozšířená odpověď s detaily přiřazeného kurýra.

    Vrací se při GET jednotlivé objednávky (`/orders/{id}`).
    Obsahuje navíc jméno a telefon kurýra pro snadnější zobrazení v UI.

    ## Příklad odpovědi

    ```json
    {
        "id": 42,
        "customer_name": "Marie Svobodová",
        "customer_phone": "+420606123456",
        "pickup_address": "Národní 25, Praha 1",
        "pickup_lat": 50.0815,
        "pickup_lng": 14.4195,
        "delivery_address": "Vinohradská 50, Praha 2",
        "delivery_lat": 50.0755,
        "delivery_lng": 14.4378,
        "is_vip": false,
        "required_tags": [],
        "status": "ASSIGNED",
        "courier_id": 5,
        "courier_name": "Jan Novák",
        "courier_phone": "+420777123456",
        "created_at": "2024-01-15T12:00:00",
        "updated_at": "2024-01-15T12:05:00"
    }
    ```
    """

    courier_name: Optional[str] = Field(
        default=None,
        description="Jméno přiřazeného kurýra (null pokud není přiřazen)",
        json_schema_extra={"example": "Jan Novák"}
    )
    courier_phone: Optional[str] = Field(
        default=None,
        description="Telefon přiřazeného kurýra (null pokud není přiřazen)",
        json_schema_extra={"example": "+420777123456"}
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 42,
                "customer_name": "Marie Svobodová",
                "customer_phone": "+420606123456",
                "pickup_address": "Národní 25, Praha 1",
                "pickup_lat": 50.0815,
                "pickup_lng": 14.4195,
                "delivery_address": "Vinohradská 50, Praha 2",
                "delivery_lat": 50.0755,
                "delivery_lng": 14.4378,
                "is_vip": False,
                "required_tags": [],
                "status": "ASSIGNED",
                "courier_id": 5,
                "courier_name": "Jan Novák",
                "courier_phone": "+420777123456",
                "created_at": "2024-01-15T12:00:00",
                "updated_at": "2024-01-15T12:05:00"
            }
        }
    )
