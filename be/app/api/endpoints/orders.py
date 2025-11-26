"""API endpointy pro správu objednávek.

Tento modul poskytuje kompletní životní cyklus objednávky:
vytvoření, dispatch, pickup, deliver, cancel.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    OrderWithCourier
)
from app.models.order import OrderStatus
from app.crud import order as order_crud
from app.crud import courier as courier_crud

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Vytvořit novou objednávku",
    description="""
Vytvoří novou objednávku v systému.

## Co se stane
1. Vytvoří se nový záznam objednávky
2. Objednávka je ve stavu `CREATED`
3. Čeká na přiřazení kurýra (dispatch)

## Další kroky
Pro přiřazení kurýra zavolejte `POST /dispatch/auto/{order_id}`.

## GPS souřadnice
- **pickup_lat/pickup_lng** - Místo vyzvednutí (restaurace)
- **delivery_lat/delivery_lng** - Místo doručení (zákazník)

## VIP objednávky
Nastavte `is_vip: true` pro prioritní zpracování.
VIP objednávky preferují kurýry s tagem `vip`.

## Požadavky na kurýra (tagy)
Pole `required_tags` určuje, jaké specializace musí mít kurýr.
Např. `["fragile_ok"]` znamená, že kurýr musí mít tag `fragile_ok`.

## Příklad
```json
{
    "customer_name": "Marie Svobodová",
    "customer_phone": "+420606123456",
    "pickup_address": "Restaurace U Malířů, Národní 25",
    "pickup_lat": 50.0815,
    "pickup_lng": 14.4195,
    "delivery_address": "Vinohradská 50, Praha 2",
    "delivery_lat": 50.0755,
    "delivery_lng": 14.4378,
    "is_vip": false,
    "required_tags": []
}
```
    """,
    responses={
        201: {
            "description": "Objednávka vytvořena",
            "content": {
                "application/json": {
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
                        "status": "CREATED",
                        "courier_id": None,
                        "created_at": "2024-01-15T12:00:00",
                        "updated_at": None
                    }
                }
            }
        },
        422: {
            "description": "Neplatný formát dat",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "customer_phone"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Vytvoří novou objednávku."""
    return order_crud.create_order(db, order)


@router.get(
    "/",
    response_model=List[OrderResponse],
    summary="Získat seznam všech objednávek",
    description="""
Vrátí stránkovaný seznam všech objednávek v systému.

## Parametry
- `skip` - Počet záznamů k přeskočení
- `limit` - Maximální počet vrácených záznamů

## Řazení
Objednávky jsou řazeny podle data vytvoření (nejnovější první).

## Tip
Pro filtrování podle stavu použijte `/orders/by-status/{status}`.
    """,
    responses={
        200: {
            "description": "Seznam objednávek"
        }
    }
)
def get_orders(
    skip: int = Query(default=0, ge=0, description="Offset pro stránkování"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max počet záznamů"),
    db: Session = Depends(get_db)
):
    """Vrátí seznam všech objednávek."""
    return order_crud.get_orders(db, skip=skip, limit=limit)


@router.get(
    "/pending",
    response_model=List[OrderResponse],
    summary="Získat objednávky čekající na kurýra",
    description="""
Vrátí seznam objednávek ve stavu `SEARCHING` - čekají na přiřazení kurýra.

## Kdy je objednávka ve stavu SEARCHING?
- Po neúspěšném automatickém dispatch (žádný kurýr v dosahu)
- Objednávka čeká na opakovaný pokus o dispatch

## Využití
- Dashboard dispečera pro manuální přiřazení
- Monitoring nepřiřazených objednávek
- Alert systém pro dlouho čekající objednávky
    """,
    responses={
        200: {
            "description": "Seznam čekajících objednávek"
        }
    }
)
def get_pending_orders(db: Session = Depends(get_db)):
    """Vrátí objednávky čekající na přiřazení kurýra."""
    return order_crud.get_pending_orders(db)


@router.get(
    "/by-status/{status}",
    response_model=List[OrderResponse],
    summary="Získat objednávky podle stavu",
    description="""
Vrátí seznam všech objednávek v daném stavu.

## Možné stavy

| Stav | Popis |
|------|-------|
| `CREATED` | Nově vytvořená, čeká na dispatch |
| `SEARCHING` | Hledá se kurýr |
| `ASSIGNED` | Kurýr přiřazen, míří k vyzvednutí |
| `PICKED` | Kurýr vyzvednul zásilku |
| `DELIVERED` | Doručeno zákazníkovi |
| `CANCELLED` | Zrušeno |

## Příklady
- `/orders/by-status/ASSIGNED` - Aktivní objednávky s kurýrem
- `/orders/by-status/DELIVERED` - Dokončené objednávky
- `/orders/by-status/CANCELLED` - Zrušené objednávky
    """,
    responses={
        200: {
            "description": "Seznam objednávek v daném stavu"
        }
    }
)
def get_orders_by_status(
    status: OrderStatus = Path(..., description="Stav objednávky pro filtrování"),
    db: Session = Depends(get_db)
):
    """Vrátí objednávky filtrované podle stavu."""
    return order_crud.get_orders_by_status(db, status)


@router.get(
    "/{order_id}",
    response_model=OrderWithCourier,
    summary="Získat detail objednávky",
    description="""
Vrátí kompletní informace o objednávce včetně detailů přiřazeného kurýra.

## Vrácené informace
- Všechny údaje objednávky (zákazník, adresy, GPS)
- Aktuální stav
- ID kurýra + jeho jméno a telefon (pokud je přiřazen)
- Časové údaje

## Využití
- Sledování stavu objednávky
- Zobrazení kontaktu na kurýra
- Detail pro zákazníka

## Chyby
- **404 Not Found** - Objednávka neexistuje
    """,
    responses={
        200: {
            "description": "Detail objednávky s kurýrem"
        },
        404: {
            "description": "Objednávka nenalezena",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
def get_order(
    order_id: int = Path(..., ge=1, description="ID objednávky"),
    db: Session = Depends(get_db)
):
    """Vrátí detail objednávky včetně kurýra."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    response = OrderWithCourier.model_validate(order)
    if order.courier_id:
        courier = courier_crud.get_courier(db, order.courier_id)
        if courier:
            response.courier_name = courier.name
            response.courier_phone = courier.phone

    return response


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Změnit stav objednávky (admin)",
    description="""
Administrativní endpoint pro přímou změnu stavu objednávky.

## Upozornění
Pro běžné operace používejte specifické endpointy:
- `/orders/{id}/pickup` - Kurýr vyzvednul
- `/orders/{id}/deliver` - Kurýr doručil
- `/orders/{id}/cancel` - Zrušení

Tento endpoint je určen pro **výjimečné situace** a opravy.

## Chyby
- **404 Not Found** - Objednávka neexistuje
    """,
    responses={
        200: {
            "description": "Stav změněn"
        },
        404: {
            "description": "Objednávka nenalezena",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
def update_order_status(
    order_id: int = Path(..., ge=1, description="ID objednávky"),
    status_update: OrderStatusUpdate = ...,
    db: Session = Depends(get_db)
):
    """Změní stav objednávky (administrativní operace)."""
    updated = order_crud.update_order_status(db, order_id, status_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return updated


@router.post(
    "/{order_id}/pickup",
    response_model=OrderResponse,
    summary="Označit objednávku jako vyzvednutou",
    description="""
Kurýr označí, že vyzvednul objednávku v restauraci/obchodě.

## Co se stane
1. Stav se změní z `ASSIGNED` na `PICKED`
2. Kurýr nyní vozí zásilku k zákazníkovi

## Předpoklady
- Objednávka musí být ve stavu `ASSIGNED`
- Kurýr musí být přiřazen

## Další krok
Po doručení zavolejte `POST /orders/{id}/deliver`.

## Chyby
- **404 Not Found** - Objednávka neexistuje
- **400 Bad Request** - Objednávka není ve stavu ASSIGNED
    """,
    responses={
        200: {
            "description": "Objednávka označena jako vyzvednutá",
            "content": {
                "application/json": {
                    "example": {
                        "id": 42,
                        "status": "PICKED",
                        "courier_id": 5
                    }
                }
            }
        },
        400: {
            "description": "Neplatný stav pro vyzvednutí",
            "content": {
                "application/json": {
                    "example": {"detail": "Order cannot be picked up (status: CREATED)"}
                }
            }
        },
        404: {
            "description": "Objednávka nenalezena",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
def mark_order_picked(
    order_id: int = Path(..., ge=1, description="ID objednávky"),
    db: Session = Depends(get_db)
):
    """Označí objednávku jako vyzvednutou kurýrem."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status != OrderStatus.ASSIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be picked up (status: {order.status})"
        )

    return order_crud.update_order_status(
        db, order_id,
        OrderStatusUpdate(status=OrderStatus.PICKED)
    )


@router.post(
    "/{order_id}/deliver",
    response_model=OrderResponse,
    summary="Označit objednávku jako doručenou",
    description="""
Kurýr označí, že doručil objednávku zákazníkovi.

## Co se stane
1. Stav se změní z `PICKED` na `DELIVERED`
2. Kurýr se automaticky vrátí do stavu `available`
3. Kurýr může přijmout další objednávku

## Předpoklady
- Objednávka musí být ve stavu `PICKED`

## Poznámka
Toto je **konečný stav** objednávky. Po doručení nelze stav změnit.

## Chyby
- **404 Not Found** - Objednávka neexistuje
- **400 Bad Request** - Objednávka není ve stavu PICKED
    """,
    responses={
        200: {
            "description": "Objednávka doručena",
            "content": {
                "application/json": {
                    "example": {
                        "id": 42,
                        "status": "DELIVERED",
                        "courier_id": 5
                    }
                }
            }
        },
        400: {
            "description": "Neplatný stav pro doručení",
            "content": {
                "application/json": {
                    "example": {"detail": "Order cannot be delivered (status: ASSIGNED)"}
                }
            }
        },
        404: {
            "description": "Objednávka nenalezena",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
def mark_order_delivered(
    order_id: int = Path(..., ge=1, description="ID objednávky"),
    db: Session = Depends(get_db)
):
    """Označí objednávku jako doručenou."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status != OrderStatus.PICKED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be delivered (status: {order.status})"
        )

    updated_order = order_crud.update_order_status(
        db, order_id,
        OrderStatusUpdate(status=OrderStatus.DELIVERED)
    )

    # Uvolnit kurýra
    if order.courier_id:
        from app.schemas.courier import CourierStatusUpdate
        from app.models.courier import CourierStatus
        courier_crud.update_courier_status(
            db, order.courier_id,
            CourierStatusUpdate(status=CourierStatus.available)
        )

    return updated_order


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Zrušit objednávku",
    description="""
Zruší objednávku a uvolní kurýra (pokud byl přiřazen).

## Co se stane
1. Stav se změní na `CANCELLED`
2. Pokud byl přiřazen kurýr, vrátí se do stavu `available`
3. Objednávka je ukončena

## Kdy lze zrušit
- `CREATED` - Ano
- `SEARCHING` - Ano
- `ASSIGNED` - Ano (kurýr se uvolní)
- `PICKED` - Ano (kurýr se uvolní)
- `DELIVERED` - **NE** (již doručeno)
- `CANCELLED` - **NE** (již zrušeno)

## Důvody zrušení
- Zákazník si rozmyslel objednávku
- Restaurace nemůže objednávku připravit
- Technický problém

## Chyby
- **404 Not Found** - Objednávka neexistuje
- **400 Bad Request** - Objednávku nelze zrušit (DELIVERED/CANCELLED)
    """,
    responses={
        200: {
            "description": "Objednávka zrušena",
            "content": {
                "application/json": {
                    "example": {
                        "id": 42,
                        "status": "CANCELLED",
                        "courier_id": 5
                    }
                }
            }
        },
        400: {
            "description": "Objednávku nelze zrušit",
            "content": {
                "application/json": {
                    "example": {"detail": "Order cannot be cancelled (status: DELIVERED)"}
                }
            }
        },
        404: {
            "description": "Objednávka nenalezena",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
def cancel_order(
    order_id: int = Path(..., ge=1, description="ID objednávky"),
    db: Session = Depends(get_db)
):
    """Zruší objednávku."""
    order = order_crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order cannot be cancelled (status: {order.status})"
        )

    # Uvolnit kurýra pokud byl přiřazen
    if order.courier_id and order.status in [OrderStatus.ASSIGNED, OrderStatus.PICKED]:
        from app.schemas.courier import CourierStatusUpdate
        from app.models.courier import CourierStatus
        courier_crud.update_courier_status(
            db, order.courier_id,
            CourierStatusUpdate(status=CourierStatus.available)
        )

    return order_crud.update_order_status(
        db, order_id,
        OrderStatusUpdate(status=OrderStatus.CANCELLED)
    )


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Smazat objednávku",
    description="""
Trvale smaže objednávku ze systému.

## Upozornění
- Akce je **nevratná**!
- Používejte pouze pro testování nebo opravu chyb
- Pro běžné ukončení objednávky použijte `/orders/{id}/cancel`

## Doporučení
V produkci objednávky nemazat - slouží pro historii a reporting.

## Chyby
- **404 Not Found** - Objednávka neexistuje
    """,
    responses={
        204: {
            "description": "Objednávka smazána"
        },
        404: {
            "description": "Objednávka nenalezena",
            "content": {
                "application/json": {
                    "example": {"detail": "Order not found"}
                }
            }
        }
    }
)
def delete_order(
    order_id: int = Path(..., ge=1, description="ID objednávky"),
    db: Session = Depends(get_db)
):
    """Smaže objednávku (pouze pro admin/testování)."""
    deleted = order_crud.delete_order(db, order_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return None
