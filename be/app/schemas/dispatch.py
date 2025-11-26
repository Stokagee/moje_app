"""Pydantic schémata pro dispečink.

Tento modul definuje datové struktury pro přiřazování kurýrů k objednávkám.
Dispečink je klíčová část systému, která spojuje dostupné kurýry s novými objednávkami.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class DispatchAssign(BaseModel):
    """Schéma pro manuální přiřazení kurýra k objednávce.

    Používá se, když operátor chce přepsat automatický dispatch
    a přiřadit konkrétního kurýra k objednávce.

    ## Kdy použít manuální dispatch

    - Zákazník si vyžádal konkrétního kurýra
    - Automatický dispatch selhal a operátor vybírá ručně
    - Speciální situace vyžadující lidské rozhodnutí

    ## Předpoklady

    - Objednávka musí být ve stavu `CREATED` nebo `SEARCHING`
    - Kurýr musí být ve stavu `available`
    - Kurýr musí mít všechny požadované tagy objednávky

    ## Příklad

    ```json
    {
        "order_id": 42,
        "courier_id": 5
    }
    ```
    """

    order_id: int = Field(
        ...,
        description="ID objednávky k přiřazení",
        json_schema_extra={"example": 42}
    )
    courier_id: int = Field(
        ...,
        description="ID kurýra, který má objednávku převzít",
        json_schema_extra={"example": 5}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": 42,
                "courier_id": 5
            }
        }
    )


class DispatchLogResponse(BaseModel):
    """Záznam v logu dispečinku.

    Každé přiřazení (úspěšné i neúspěšné) vytváří záznam v logu.
    Slouží pro audit, analýzu a řešení sporů.

    ## Typy akcí (action)

    | Akce | Popis |
    |------|-------|
    | `auto_assigned` | Kurýr přiřazen automatickým algoritmem |
    | `manual_assigned` | Kurýr přiřazen operátorem ručně |
    | `auto_failed` | Automatický dispatch selhal (žádný kurýr) |
    | `rejected` | Kurýr odmítl objednávku |

    ## Příklad odpovědi

    ```json
    {
        "id": 123,
        "order_id": 42,
        "courier_id": 5,
        "action": "auto_assigned",
        "created_at": "2024-01-15T12:05:00"
    }
    ```
    """

    id: int = Field(
        ...,
        description="Unikátní ID záznamu v logu",
        json_schema_extra={"example": 123}
    )
    order_id: int = Field(
        ...,
        description="ID objednávky, které se záznam týká",
        json_schema_extra={"example": 42}
    )
    courier_id: int = Field(
        ...,
        description="ID kurýra, který byl přiřazen/odmítnut",
        json_schema_extra={"example": 5}
    )
    action: str = Field(
        ...,
        description="Typ akce: auto_assigned, manual_assigned, auto_failed, rejected",
        json_schema_extra={"example": "auto_assigned"}
    )
    created_at: datetime = Field(
        ...,
        description="Datum a čas vytvoření záznamu",
        json_schema_extra={"example": "2024-01-15T12:05:00"}
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 123,
                "order_id": 42,
                "courier_id": 5,
                "action": "auto_assigned",
                "created_at": "2024-01-15T12:05:00"
            }
        }
    )


class DispatchResult(BaseModel):
    """Výsledek operace dispečinku.

    Vrací se po každém pokusu o přiřazení kurýra (automatickém i manuálním).

    ## Úspěšný dispatch

    ```json
    {
        "success": true,
        "message": "Kurýr Jan Novák přiřazen (vzdálenost: 1.2 km)",
        "order_id": 42,
        "courier_id": 5
    }
    ```

    ## Neúspěšný dispatch

    ```json
    {
        "success": false,
        "message": "No available courier found within 5km radius",
        "order_id": 42,
        "courier_id": null
    }
    ```

    ## Možné důvody neúspěchu

    - Žádný kurýr v dosahu (2km, pak 5km)
    - Žádný kurýr s požadovanými tagy
    - Všichni kurýři jsou busy nebo offline
    - Objednávka je v neplatném stavu
    - Objednávka nebo kurýr neexistuje
    """

    success: bool = Field(
        ...,
        description="True pokud byl kurýr úspěšně přiřazen, False jinak",
        json_schema_extra={"example": True}
    )
    message: str = Field(
        ...,
        description="Textový popis výsledku operace",
        json_schema_extra={"example": "Kurýr Jan Novák přiřazen (vzdálenost: 1.2 km)"}
    )
    order_id: int = Field(
        ...,
        description="ID objednávky, které se operace týká",
        json_schema_extra={"example": 42}
    )
    courier_id: Optional[int] = Field(
        default=None,
        description="ID přiřazeného kurýra (null pokud dispatch selhal)",
        json_schema_extra={"example": 5}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "summary": "Úspěšný dispatch",
                    "value": {
                        "success": True,
                        "message": "Kurýr Jan Novák přiřazen (vzdálenost: 1.2 km)",
                        "order_id": 42,
                        "courier_id": 5
                    }
                },
                {
                    "summary": "Neúspěšný dispatch - žádný kurýr",
                    "value": {
                        "success": False,
                        "message": "No available courier found within 5km radius",
                        "order_id": 42,
                        "courier_id": None
                    }
                }
            ]
        }
    )


class AvailableCourierInfo(BaseModel):
    """Informace o dostupném kurýrovi pro danou objednávku.

    Vrací se v seznamu při dotazu na dostupné kurýry pro objednávku.
    Obsahuje vypočítanou vzdálenost a informaci o VIP statusu.

    ## Příklad

    ```json
    {
        "courier_id": 5,
        "name": "Jan Novák",
        "phone": "+420777123456",
        "distance_km": 1.2,
        "is_vip_courier": true,
        "tags": ["bike", "vip"]
    }
    ```
    """

    courier_id: int = Field(
        ...,
        description="ID kurýra",
        json_schema_extra={"example": 5}
    )
    name: str = Field(
        ...,
        description="Jméno kurýra",
        json_schema_extra={"example": "Jan Novák"}
    )
    phone: str = Field(
        ...,
        description="Telefonní číslo kurýra",
        json_schema_extra={"example": "+420777123456"}
    )
    distance_km: float = Field(
        ...,
        description="Vzdálenost od místa vyzvednutí v kilometrech",
        json_schema_extra={"example": 1.2}
    )
    is_vip_courier: bool = Field(
        ...,
        description="True pokud kurýr má tag 'vip'",
        json_schema_extra={"example": True}
    )
    tags: list[str] = Field(
        ...,
        description="Seznam tagů kurýra",
        json_schema_extra={"example": ["bike", "vip"]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "courier_id": 5,
                "name": "Jan Novák",
                "phone": "+420777123456",
                "distance_km": 1.2,
                "is_vip_courier": True,
                "tags": ["bike", "vip"]
            }
        }
    )
