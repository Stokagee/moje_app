"""API endpointy pro dispečink.

Tento modul zajišťuje přiřazování kurýrů k objednávkám.
Podporuje automatický dispatch (algoritmus) i manuální (operátor).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.dispatch import DispatchAssign, DispatchResult, DispatchLogResponse
from app.services.dispatch_service import (
    auto_dispatch_order,
    manual_dispatch_order,
    get_available_couriers_for_order
)
from app.crud import dispatch_log as dispatch_log_crud

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


@router.post(
    "/auto/{order_id}",
    response_model=DispatchResult,
    summary="Automaticky přiřadit kurýra k objednávce",
    description="""
Automaticky najde a přiřadí nejbližšího vhodného kurýra k objednávce.

## Jak algoritmus funguje

### Krok 1: Najdi kandidáty
- Vybere všechny kurýry ve stavu `available`
- Musí mít platnou GPS polohu

### Krok 2: Filtruj podle tagů
- Pokud objednávka má `required_tags`, kurýr musí mít **všechny** tyto tagy
- Např. objednávka vyžaduje `["fragile_ok", "bike"]` → kurýr musí mít oba

### Krok 3: VIP priorita
- Pro VIP objednávky (`is_vip: true`) se nejdřív zkusí najít kurýr s tagem `vip`
- Pokud žádný VIP kurýr není dostupný, použije se běžný kurýr

### Krok 4: Fázové hledání
1. **Fáze 1 (750 km)**: Hledá kurýry do 750 km od místa vyzvednutí
2. **Fáze 2 (1500 km)**: Pokud nikdo není v 750 km, rozšíří na 1500 km

### Krok 5: Výběr nejbližšího
- Ze všech kandidátů v dosahu vybere **nejbližšího**
- Vzdálenost se počítá pomocí Haversine vzorce (GPS)

## Co se stane po úspěchu
1. Objednávka přejde do stavu `ASSIGNED`
2. Kurýr přejde do stavu `busy`
3. Vytvoří se záznam v dispatch logu

## Co se stane po neúspěchu
1. Objednávka přejde do stavu `SEARCHING`
2. Vrátí se `success: false` s důvodem
3. Můžete zkusit znovu později nebo použít manuální dispatch

## Příklady odpovědí

### Úspěch
```json
{
    "success": true,
    "message": "Kurýr Jan Novák přiřazen (vzdálenost: 1.2 km)",
    "order_id": 42,
    "courier_id": 5
}
```

### Neúspěch - žádný kurýr v dosahu
```json
{
    "success": false,
    "message": "No available courier found within 1500km radius",
    "order_id": 42,
    "courier_id": null
}
```

### Neúspěch - chybí tagy
```json
{
    "success": false,
    "message": "No courier with required tags: fragile_ok",
    "order_id": 42,
    "courier_id": null
}
```

## Chyby
- **Objednávka neexistuje** - `success: false`, message obsahuje "not found"
- **Objednávka již přiřazena** - `success: false`, message obsahuje "cannot be dispatched"
    """,
    responses={
        200: {
            "description": "Výsledek dispatch operace",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Úspěšný dispatch",
                            "value": {
                                "success": True,
                                "message": "Kurýr Jan Novák přiřazen (vzdálenost: 1.2 km)",
                                "order_id": 42,
                                "courier_id": 5
                            }
                        },
                        "no_courier": {
                            "summary": "Žádný kurýr v dosahu",
                            "value": {
                                "success": False,
                                "message": "No available courier found within 5km radius",
                                "order_id": 42,
                                "courier_id": None
                            }
                        },
                        "wrong_state": {
                            "summary": "Objednávka v neplatném stavu",
                            "value": {
                                "success": False,
                                "message": "Order 42 cannot be dispatched (status: DELIVERED)",
                                "order_id": 42,
                                "courier_id": None
                            }
                        }
                    }
                }
            }
        }
    }
)
def dispatch_order_auto(
    order_id: int = Path(..., ge=1, description="ID objednávky k dispatchnutí"),
    db: Session = Depends(get_db)
):
    """Automaticky přiřadí nejbližšího vhodného kurýra."""
    success, message, courier_id = auto_dispatch_order(db, order_id)
    return DispatchResult(
        success=success,
        message=message,
        order_id=order_id,
        courier_id=courier_id
    )


@router.post(
    "/manual",
    response_model=DispatchResult,
    summary="Manuálně přiřadit kurýra k objednávce",
    description="""
Manuálně přiřadí konkrétního kurýra k objednávce.

## Kdy použít
- Zákazník si vyžádal konkrétního kurýra
- Automatický dispatch selhal a operátor vybírá ručně
- Speciální situace vyžadující lidské rozhodnutí
- Kurýr je mimo standardní dosah ale může objednávku obsloužit

## Předpoklady
- Objednávka musí být ve stavu `CREATED` nebo `SEARCHING`
- Kurýr musí být ve stavu `available`
- Kurýr musí mít všechny požadované tagy objednávky

## Co se ověřuje
1. Objednávka existuje a je v dispatchovatelném stavu
2. Kurýr existuje a je dostupný
3. Kurýr má všechny požadované tagy

## Co se stane po úspěchu
1. Objednávka přejde do stavu `ASSIGNED`
2. Kurýr přejde do stavu `busy`
3. Vytvoří se záznam v dispatch logu s akcí `manual_assigned`

## Příklad požadavku
```json
{
    "order_id": 42,
    "courier_id": 5
}
```

## Chyby
- **Kurýr není dostupný** - `success: false`
- **Kurýr nemá požadované tagy** - `success: false`
- **Objednávka v neplatném stavu** - `success: false`
    """,
    responses={
        200: {
            "description": "Výsledek manuálního dispatch",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Úspěšné přiřazení",
                            "value": {
                                "success": True,
                                "message": "Courier successfully assigned to order",
                                "order_id": 42,
                                "courier_id": 5
                            }
                        },
                        "courier_busy": {
                            "summary": "Kurýr není dostupný",
                            "value": {
                                "success": False,
                                "message": "Courier 5 is not available (status: busy)",
                                "order_id": 42,
                                "courier_id": None
                            }
                        },
                        "missing_tags": {
                            "summary": "Kurýr nemá požadované tagy",
                            "value": {
                                "success": False,
                                "message": "Courier 5 missing required tags: fragile_ok",
                                "order_id": 42,
                                "courier_id": None
                            }
                        }
                    }
                }
            }
        }
    }
)
def dispatch_order_manual(
    assign: DispatchAssign,
    db: Session = Depends(get_db)
):
    """Manuálně přiřadí konkrétního kurýra k objednávce."""
    success, message = manual_dispatch_order(db, assign.order_id, assign.courier_id)
    return DispatchResult(
        success=success,
        message=message,
        order_id=assign.order_id,
        courier_id=assign.courier_id if success else None
    )


@router.get(
    "/available-couriers/{order_id}",
    summary="Získat seznam vhodných kurýrů pro objednávku",
    description="""
Vrátí seznam všech kurýrů, kteří mohou převzít danou objednávku.

## Co se kontroluje
- Kurýr je ve stavu `available`
- Kurýr má platnou GPS polohu
- Kurýr má všechny `required_tags` objednávky
- Kurýr je v zadaném radiusu od místa vyzvednutí

## Využití
- UI pro manuální dispatch - operátor vidí kandidáty
- Zobrazení kurýrů na mapě
- Rozhodování před manuálním přiřazením

## Parametry
- `order_id` - ID objednávky
- `radius_km` - Maximální vzdálenost v km (default 10)

## Vrácená data
Pro každého kurýra:
- Základní info (ID, jméno, telefon)
- Vzdálenost od místa vyzvednutí
- Je-li VIP kurýr
- Seznam tagů

## Řazení
Kurýři jsou seřazeni podle vzdálenosti (nejbližší první).
Pro VIP objednávky jsou VIP kurýři na začátku.

## Příklad odpovědi
```json
{
    "order_id": 42,
    "radius_km": 10.0,
    "count": 2,
    "couriers": [
        {
            "courier_id": 5,
            "name": "Jan Novák",
            "phone": "+420777123456",
            "distance_km": 1.2,
            "is_vip_courier": true,
            "tags": ["bike", "vip"]
        },
        {
            "courier_id": 8,
            "name": "Petr Svoboda",
            "phone": "+420666789012",
            "distance_km": 2.5,
            "is_vip_courier": false,
            "tags": ["bike"]
        }
    ]
}
```
    """,
    responses={
        200: {
            "description": "Seznam dostupných kurýrů",
            "content": {
                "application/json": {
                    "examples": {
                        "found": {
                            "summary": "Nalezeni kurýři",
                            "value": {
                                "order_id": 42,
                                "radius_km": 10.0,
                                "count": 2,
                                "couriers": [
                                    {
                                        "courier_id": 5,
                                        "name": "Jan Novák",
                                        "phone": "+420777123456",
                                        "distance_km": 1.2,
                                        "is_vip_courier": True,
                                        "tags": ["bike", "vip"]
                                    }
                                ]
                            }
                        },
                        "empty": {
                            "summary": "Žádný kurýr nenalezen",
                            "value": {
                                "order_id": 42,
                                "radius_km": 10.0,
                                "couriers": [],
                                "message": "No available couriers found"
                            }
                        }
                    }
                }
            }
        }
    }
)
def get_couriers_for_order(
    order_id: int = Path(..., ge=1, description="ID objednávky"),
    radius_km: float = Query(
        default=10.0,
        ge=0.1,
        le=100.0,
        description="Maximální vzdálenost od místa vyzvednutí v km"
    ),
    db: Session = Depends(get_db)
):
    """Vrátí seznam kurýrů vhodných pro danou objednávku."""
    couriers = get_available_couriers_for_order(db, order_id, radius_km)
    if not couriers:
        return {
            "order_id": order_id,
            "radius_km": radius_km,
            "couriers": [],
            "message": "No available couriers found"
        }
    return {
        "order_id": order_id,
        "radius_km": radius_km,
        "couriers": couriers,
        "count": len(couriers)
    }


@router.get(
    "/logs/order/{order_id}",
    response_model=List[DispatchLogResponse],
    summary="Získat historii dispatchů pro objednávku",
    description="""
Vrátí kompletní historii přiřazení kurýrů k dané objednávce.

## Využití
- Audit a debugging
- Zobrazení historie v detailu objednávky
- Analýza problémů s dispatchem

## Typy záznamů (action)

| Akce | Popis |
|------|-------|
| `auto_assigned` | Kurýr přiřazen automatickým algoritmem |
| `manual_assigned` | Kurýr přiřazen operátorem ručně |
| `auto_failed` | Automatický dispatch selhal |
| `rejected` | Kurýr odmítl objednávku |

## Řazení
Záznamy jsou seřazeny od nejnovějšího.

## Příklad odpovědi
```json
[
    {
        "id": 456,
        "order_id": 42,
        "courier_id": 5,
        "action": "auto_assigned",
        "created_at": "2024-01-15T12:05:00"
    },
    {
        "id": 455,
        "order_id": 42,
        "courier_id": 3,
        "action": "auto_failed",
        "created_at": "2024-01-15T12:04:30"
    }
]
```
    """,
    responses={
        200: {
            "description": "Historie dispatchů pro objednávku"
        }
    }
)
def get_dispatch_logs_for_order(
    order_id: int = Path(..., ge=1, description="ID objednávky"),
    db: Session = Depends(get_db)
):
    """Vrátí historii dispatchů pro objednávku."""
    return dispatch_log_crud.get_dispatch_logs_for_order(db, order_id)


@router.get(
    "/logs/courier/{courier_id}",
    response_model=List[DispatchLogResponse],
    summary="Získat historii dispatchů pro kurýra",
    description="""
Vrátí kompletní historii přiřazení objednávek danému kurýrovi.

## Využití
- Analýza výkonu kurýra
- Přehled dokončených objednávek
- Debugging problémů s konkrétním kurýrem

## Informace v záznamu
- Které objednávky kurýr dostal
- Zda byly automaticky nebo manuálně přiřazeny
- Časové údaje

## Řazení
Záznamy jsou seřazeny od nejnovějšího.

## Příklad odpovědi
```json
[
    {
        "id": 456,
        "order_id": 42,
        "courier_id": 5,
        "action": "auto_assigned",
        "created_at": "2024-01-15T12:05:00"
    },
    {
        "id": 400,
        "order_id": 38,
        "courier_id": 5,
        "action": "manual_assigned",
        "created_at": "2024-01-15T10:30:00"
    }
]
```
    """,
    responses={
        200: {
            "description": "Historie dispatchů pro kurýra"
        }
    }
)
def get_dispatch_logs_for_courier(
    courier_id: int = Path(..., ge=1, description="ID kurýra"),
    db: Session = Depends(get_db)
):
    """Vrátí historii dispatchů pro kurýra."""
    return dispatch_log_crud.get_dispatch_logs_for_courier(db, courier_id)
