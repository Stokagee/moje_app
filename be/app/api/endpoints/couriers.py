"""API endpointy pro správu kurýrů.

Tento modul poskytuje CRUD operace a správu stavu kurýrů.
Kurýr je osoba, která doručuje objednávky zákazníkům.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.courier import (
    CourierCreate,
    CourierUpdate,
    CourierResponse,
    CourierLocationUpdate,
    CourierStatusUpdate
)
from app.crud import courier as courier_crud

router = APIRouter(prefix="/couriers", tags=["couriers"])


@router.post(
    "/",
    response_model=CourierResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Vytvořit nového kurýra",
    description="""
Vytvoří nového kurýra v systému.

## Co se stane
1. Ověří se, že e-mail ještě není v systému použit
2. Vytvoří se nový záznam kurýra
3. Kurýr je automaticky ve stavu `offline` bez GPS polohy

## Další kroky po vytvoření
- Nastavte GPS polohu: `PATCH /couriers/{id}/location`
- Aktivujte kurýra: `PATCH /couriers/{id}/status` s hodnotou `available`

## Chyby
- **400 Bad Request** - E-mail již existuje v systému
- **422 Unprocessable Entity** - Neplatný formát dat (chybí povinná pole, špatný e-mail)
    """,
    responses={
        201: {
            "description": "Kurýr úspěšně vytvořen",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Jan Novák",
                        "phone": "+420777123456",
                        "email": "jan.novak@example.cz",
                        "tags": ["bike", "vip"],
                        "lat": None,
                        "lng": None,
                        "status": "offline",
                        "created_at": "2024-01-15T10:30:00",
                        "updated_at": None
                    }
                }
            }
        },
        400: {
            "description": "E-mail již existuje",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier with this email already exists"}
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
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    }
)
def create_courier(courier: CourierCreate, db: Session = Depends(get_db)):
    """Vytvoří nového kurýra v systému."""
    existing = courier_crud.get_courier_by_email(db, courier.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Courier with this email already exists"
        )
    return courier_crud.create_courier(db, courier)


@router.get(
    "/",
    response_model=List[CourierResponse],
    summary="Získat seznam všech kurýrů",
    description="""
Vrátí stránkovaný seznam všech kurýrů v systému.

## Parametry
- `skip` - Počet záznamů k přeskočení (pro stránkování)
- `limit` - Maximální počet vrácených záznamů (max 1000)

## Příklad stránkování
- První stránka (10 záznamů): `?skip=0&limit=10`
- Druhá stránka: `?skip=10&limit=10`
- Třetí stránka: `?skip=20&limit=10`

## Řazení
Kurýři jsou řazeni podle data vytvoření (nejnovější první).
    """,
    responses={
        200: {
            "description": "Seznam kurýrů",
            "content": {
                "application/json": {
                    "example": [
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
                    ]
                }
            }
        }
    }
)
def get_couriers(
    skip: int = Query(
        default=0,
        ge=0,
        description="Počet záznamů k přeskočení (offset pro stránkování)"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximální počet vrácených záznamů"
    ),
    db: Session = Depends(get_db)
):
    """Vrátí stránkovaný seznam všech kurýrů."""
    return courier_crud.get_couriers(db, skip=skip, limit=limit)


@router.get(
    "/available",
    response_model=List[CourierResponse],
    summary="Získat seznam dostupných kurýrů",
    description="""
Vrátí seznam všech kurýrů, kteří jsou právě **dostupní** pro přijetí objednávky.

## Kritéria "dostupného" kurýra
- Stav: `available`
- Má nastavenou GPS polohu (lat a lng nejsou null)

## Využití
- Operátor vidí, koho může přiřadit k objednávce
- Dashboard zobrazující aktivní kurýry
- Mobilní aplikace pro sledování flotily
    """,
    responses={
        200: {
            "description": "Seznam dostupných kurýrů",
            "content": {
                "application/json": {
                    "example": [
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
                    ]
                }
            }
        }
    }
)
def get_available_couriers(db: Session = Depends(get_db)):
    """Vrátí seznam všech dostupných kurýrů."""
    return courier_crud.get_available_couriers(db)


@router.get(
    "/{courier_id}",
    response_model=CourierResponse,
    summary="Získat detail kurýra",
    description="""
Vrátí kompletní informace o jednom kurýrovi podle jeho ID.

## Vrácené informace
- Základní údaje (jméno, telefon, e-mail)
- Aktuální GPS poloha
- Aktuální stav (offline/available/busy)
- Seznam tagů/specializací
- Časové údaje (vytvořeno, aktualizováno)

## Chyby
- **404 Not Found** - Kurýr s daným ID neexistuje
    """,
    responses={
        200: {
            "description": "Detail kurýra"
        },
        404: {
            "description": "Kurýr nenalezen",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def get_courier(
    courier_id: int = Path(
        ...,
        ge=1,
        description="Unikátní identifikátor kurýra"
    ),
    db: Session = Depends(get_db)
):
    """Vrátí detail kurýra podle ID."""
    courier = courier_crud.get_courier(db, courier_id)
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return courier


@router.put(
    "/{courier_id}",
    response_model=CourierResponse,
    summary="Aktualizovat údaje kurýra",
    description="""
Aktualizuje základní údaje kurýra (jméno, telefon, tagy).

## Co lze změnit
- `name` - Jméno kurýra
- `phone` - Telefonní číslo
- `tags` - Seznam tagů (nahradí stávající seznam)

## Co NELZE změnit
- `email` - E-mail je unikátní identifikátor a nelze ho měnit

## Poznámka
Pro změnu lokace použijte `PATCH /couriers/{id}/location`.
Pro změnu stavu použijte `PATCH /couriers/{id}/status`.

## Chyby
- **404 Not Found** - Kurýr neexistuje
    """,
    responses={
        200: {
            "description": "Kurýr úspěšně aktualizován"
        },
        404: {
            "description": "Kurýr nenalezen",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def update_courier(
    courier_id: int = Path(..., ge=1, description="ID kurýra"),
    courier: CourierUpdate = ...,
    db: Session = Depends(get_db)
):
    """Aktualizuje základní údaje kurýra."""
    updated = courier_crud.update_courier(db, courier_id, courier)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.patch(
    "/{courier_id}/location",
    response_model=CourierResponse,
    summary="Aktualizovat GPS polohu kurýra",
    description="""
Aktualizuje aktuální GPS polohu kurýra.

## Kdy volat
- Pravidelně z mobilní aplikace kurýra (např. každých 30 sekund)
- Po změně polohy o více než X metrů

## Důležité
- Kurýr musí mít platnou GPS polohu, aby mohl být přiřazen k objednávce
- Vzdálenost se počítá od místa vyzvednutí objednávky

## Formát souřadnic
- Latitude (šířka): -90 až 90 (Praha je cca 50.08)
- Longitude (délka): -180 až 180 (Praha je cca 14.42)

## Chyby
- **404 Not Found** - Kurýr neexistuje
- **422 Unprocessable Entity** - Neplatné souřadnice
    """,
    responses={
        200: {
            "description": "Lokace aktualizována"
        },
        404: {
            "description": "Kurýr nenalezen",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def update_courier_location(
    courier_id: int = Path(..., ge=1, description="ID kurýra"),
    location: CourierLocationUpdate = ...,
    db: Session = Depends(get_db)
):
    """Aktualizuje GPS polohu kurýra."""
    updated = courier_crud.update_courier_location(db, courier_id, location)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.patch(
    "/{courier_id}/status",
    response_model=CourierResponse,
    summary="Změnit stav kurýra",
    description="""
Změní provozní stav kurýra.

## Možné stavy

| Stav | Popis | Může přijmout objednávku |
|------|-------|--------------------------|
| `offline` | Kurýr není v práci | Ne |
| `available` | Kurýr je volný | Ano |
| `busy` | Kurýr doručuje | Ne |

## Typické přechody
- **Začátek směny**: `offline` → `available`
- **Konec směny**: `available` → `offline`
- **Přiřazení objednávky**: `available` → `busy` (automaticky)
- **Dokončení doručení**: `busy` → `available` (automaticky)

## Upozornění
- Stav `busy` je většinou nastaven automaticky při dispatch
- Stav se automaticky změní na `available` po dokončení doručení

## Chyby
- **404 Not Found** - Kurýr neexistuje
    """,
    responses={
        200: {
            "description": "Stav změněn"
        },
        404: {
            "description": "Kurýr nenalezen",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def update_courier_status(
    courier_id: int = Path(..., ge=1, description="ID kurýra"),
    status_update: CourierStatusUpdate = ...,
    db: Session = Depends(get_db)
):
    """Změní provozní stav kurýra."""
    updated = courier_crud.update_courier_status(db, courier_id, status_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return updated


@router.delete(
    "/{courier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Smazat kurýra",
    description="""
Trvale smaže kurýra ze systému.

## Upozornění
- Akce je **nevratná**!
- Kurýr by neměl mít aktivní objednávky (stav `busy`)
- Historie objednávek zůstane zachována

## Doporučení
Místo mazání zvažte nastavení stavu na `offline` pro deaktivaci.

## Chyby
- **404 Not Found** - Kurýr neexistuje
    """,
    responses={
        204: {
            "description": "Kurýr smazán"
        },
        404: {
            "description": "Kurýr nenalezen",
            "content": {
                "application/json": {
                    "example": {"detail": "Courier not found"}
                }
            }
        }
    }
)
def delete_courier(
    courier_id: int = Path(..., ge=1, description="ID kurýra"),
    db: Session = Depends(get_db)
):
    """Smaže kurýra ze systému."""
    deleted = courier_crud.delete_courier(db, courier_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found"
        )
    return None
