"""Pydantic schémata pro kurýry.

Tento modul definuje datové struktury pro práci s kurýry v API.
Kurýr je osoba, která doručuje objednávky zákazníkům.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.courier import CourierStatus


class CourierBase(BaseModel):
    """Základní atributy kurýra společné pro vytváření i odpovědi."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Celé jméno kurýra",
        json_schema_extra={"example": "Jan Novák"}
    )
    phone: str = Field(
        ...,
        min_length=9,
        max_length=20,
        description="Telefonní číslo kurýra v mezinárodním formátu",
        json_schema_extra={"example": "+420777123456"}
    )
    email: EmailStr = Field(
        ...,
        description="E-mailová adresa kurýra (musí být unikátní v systému)",
        json_schema_extra={"example": "jan.novak@example.cz"}
    )
    tags: List[str] = Field(
        default=[],
        description="""Seznam tagů/specializací kurýra. Běžné tagy:
        - `bike` - jezdí na kole
        - `car` - má auto
        - `vip` - preferovaný pro VIP objednávky
        - `fragile_ok` - může vozit křehké zboží
        - `fast` - expresní doručení
        """,
        json_schema_extra={"example": ["bike", "vip"]}
    )


class CourierCreate(CourierBase):
    """Schéma pro vytvoření nového kurýra.

    Po vytvoření je kurýr ve stavu `offline` bez GPS polohy.
    Pro aktivaci je potřeba nastavit lokaci a změnit stav na `available`.

    ## Příklad použití

    ```json
    {
        "name": "Jan Novák",
        "phone": "+420777123456",
        "email": "jan.novak@example.cz",
        "tags": ["bike", "vip"]
    }
    ```
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jan Novák",
                "phone": "+420777123456",
                "email": "jan.novak@example.cz",
                "tags": ["bike", "vip"]
            }
        }
    )


class CourierUpdate(BaseModel):
    """Schéma pro aktualizaci údajů kurýra.

    Všechna pole jsou volitelná - odešlete pouze ta, která chcete změnit.
    E-mail nelze změnit (je unikátní identifikátor).

    ## Příklad - změna jména a tagů

    ```json
    {
        "name": "Jan Novák ml.",
        "tags": ["car", "vip", "fragile_ok"]
    }
    ```
    """

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Nové jméno kurýra",
        json_schema_extra={"example": "Jan Novák ml."}
    )
    phone: Optional[str] = Field(
        default=None,
        min_length=9,
        max_length=20,
        description="Nové telefonní číslo",
        json_schema_extra={"example": "+420777999888"}
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Nový seznam tagů (nahradí stávající)",
        json_schema_extra={"example": ["car", "vip"]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jan Novák ml.",
                "tags": ["car", "vip"]
            }
        }
    )


class CourierLocationUpdate(BaseModel):
    """Schéma pro aktualizaci GPS polohy kurýra.

    Tato akce by měla být volána pravidelně z mobilní aplikace kurýra
    pro sledování jeho pozice v reálném čase.

    ## Souřadnice

    - `lat` (latitude) - zeměpisná šířka (-90 až 90)
    - `lng` (longitude) - zeměpisná délka (-180 až 180)

    ## Příklad - centrum Prahy

    ```json
    {
        "lat": 50.0755,
        "lng": 14.4378
    }
    ```
    """

    lat: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Zeměpisná šířka (latitude) - WGS84",
        json_schema_extra={"example": 50.0755}
    )
    lng: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Zeměpisná délka (longitude) - WGS84",
        json_schema_extra={"example": 14.4378}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lat": 50.0755,
                "lng": 14.4378
            }
        }
    )


class CourierStatusUpdate(BaseModel):
    """Schéma pro změnu stavu kurýra.

    ## Možné stavy

    | Stav | Popis | Může přijmout objednávku |
    |------|-------|--------------------------|
    | `offline` | Kurýr není k dispozici | Ne |
    | `available` | Kurýr je volný a čeká na objednávku | Ano |
    | `busy` | Kurýr právě doručuje | Ne |

    ## Stavové přechody

    - `offline` → `available`: Kurýr se přihlásil do směny
    - `available` → `busy`: Kurýr přijal objednávku (automaticky při dispatch)
    - `busy` → `available`: Kurýr dokončil doručení (automaticky)
    - `available` → `offline`: Kurýr ukončil směnu
    - `busy` → `offline`: Nelze! Musí nejdřív dokončit objednávku

    ## Příklad

    ```json
    {
        "status": "available"
    }
    ```
    """

    status: CourierStatus = Field(
        ...,
        description="Nový stav kurýra: offline, available, nebo busy",
        json_schema_extra={"example": "available"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "available"
            }
        }
    )


class CourierResponse(CourierBase):
    """Kompletní odpověď s daty kurýra.

    Vrací se při GET operacích a po vytvoření/aktualizaci kurýra.
    Obsahuje všechny atributy včetně ID, stavu a GPS polohy.

    ## Příklad odpovědi

    ```json
    {
        "id": 1,
        "name": "Jan Novák",
        "phone": "+420777123456",
        "email": "jan.novak@example.cz",
        "tags": ["bike", "vip"],
        "lat": 50.0755,
        "lng": 14.4378,
        "status": "available",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T14:45:00"
    }
    ```
    """

    id: int = Field(
        ...,
        description="Unikátní identifikátor kurýra v databázi",
        json_schema_extra={"example": 1}
    )
    lat: Optional[float] = Field(
        default=None,
        description="Aktuální zeměpisná šířka (null pokud GPS není nastavena)",
        json_schema_extra={"example": 50.0755}
    )
    lng: Optional[float] = Field(
        default=None,
        description="Aktuální zeměpisná délka (null pokud GPS není nastavena)",
        json_schema_extra={"example": 14.4378}
    )
    status: CourierStatus = Field(
        ...,
        description="Aktuální stav kurýra",
        json_schema_extra={"example": "available"}
    )
    created_at: datetime = Field(
        ...,
        description="Datum a čas vytvoření záznamu",
        json_schema_extra={"example": "2024-01-15T10:30:00"}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Datum a čas poslední aktualizace",
        json_schema_extra={"example": "2024-01-15T14:45:00"}
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Jan Novák",
                "phone": "+420777123456",
                "email": "jan.novak@example.cz",
                "tags": ["bike", "vip"],
                "lat": 50.0755,
                "lng": 14.4378,
                "status": "available",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T14:45:00"
            }
        }
    )


class CourierOfferResponse(BaseModel):
    """Schéma pro odpověď kurýra na nabídku objednávky.

    Používá se v případě, že kurýr manuálně potvrzuje přijetí objednávky.

    ## Příklad - přijetí objednávky

    ```json
    {
        "accept": true
    }
    ```
    """

    accept: bool = Field(
        ...,
        description="True pokud kurýr přijímá objednávku, False pokud odmítá",
        json_schema_extra={"example": True}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "accept": True
            }
        }
    )
