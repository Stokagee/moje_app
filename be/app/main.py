from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.api.endpoints.form_data import router as form_data_router
from app.api.endpoints.couriers import router as couriers_router
from app.api.endpoints.orders import router as orders_router
from app.api.endpoints.dispatch import router as dispatch_router
from app.database import engine, Base
# DŮLEŽITÉ: naimportovat modely před create_all, aby se tabulky vytvořily
from app.models import form_data as _model_form_data  # noqa: F401
from app.models import attachment as _model_attachment  # noqa: F401
from app.models import instruction as _model_instruction  # noqa: F401
from app.models import courier as _model_courier  # noqa: F401
from app.models import order as _model_order  # noqa: F401
from app.models import dispatch_log as _model_dispatch_log  # noqa: F401

# Vytvoření tabulek (pro vývoj, v produkci použít migrace)
Base.metadata.create_all(bind=engine)

# Nastavení logování
setup_logging()

app = FastAPI(
    title="Food Delivery API",
    version="2.0.0",
    description="""
# Food Delivery API - Systém pro správu rozvozové služby

Toto API poskytuje kompletní řešení pro správu **kurýrů**, **objednávek** a **dispečinku**
rozvozové služby jídla.

## Hlavní funkce

### Kurýři (`/couriers`)
- Vytváření, úprava a mazání kurýrů
- Správa GPS polohy v reálném čase
- Stavy kurýrů: **available** (volný), **busy** (zaneprázdněný), **offline** (nedostupný)
- Systém tagů pro specializace (např. `bike`, `car`, `vip`, `fragile_ok`, `fast`)

### Objednávky (`/orders`)
- Kompletní životní cyklus objednávky
- Stavy: **CREATED** → **SEARCHING** → **ASSIGNED** → **PICKED** → **DELIVERED**
- Podpora VIP objednávek s prioritním zpracováním
- Požadavky na tagy kurýra (např. objednávka vyžadující `fragile_ok`)

### Dispečink (`/dispatch`)
- **Automatický dispatch**: Algoritmus vybírá nejbližšího vhodného kurýra
- **Manuální dispatch**: Operátor může přiřadit konkrétního kurýra
- Fázový algoritmus: 2km → 5km radius
- VIP objednávky preferují kurýry s tagem `vip`
- Historie všech přiřazení v logu

## Stavový diagram objednávky

```
CREATED ──────────────────────────────────────┐
    │                                          │
    ▼                                          │
SEARCHING (hledá se kurýr)                     │
    │                                          │
    ▼                                          ▼
ASSIGNED (kurýr přijal) ──────────────────► CANCELLED
    │                                          ▲
    ▼                                          │
PICKED (vyzvednuto) ───────────────────────────┤
    │                                          │
    ▼                                          │
DELIVERED (doručeno)                           │
```

## Stavový diagram kurýra

```
offline ◄───────────────────────────────────────┐
    │                                            │
    ▼                                            │
available (čeká na objednávku) ◄────────────────┤
    │                                            │
    ▼ (dispatch)                                 │ (deliver/cancel)
busy (doručuje) ─────────────────────────────────┘
```

## Algoritmus automatického dispatchnutí

1. Najde všechny **available** kurýry s platnou GPS polohou
2. Odfiltruje kurýry, kteří nemají požadované tagy
3. Pro VIP objednávky preferuje kurýry s tagem `vip`
4. **Fáze 1**: Hledá kurýry do 2 km od místa vyzvednutí
5. **Fáze 2**: Pokud nikdo není, rozšíří na 5 km
6. Vybere nejbližšího kurýra podle GPS vzdálenosti
7. Přiřadí kurýra a změní jeho stav na `busy`

## Příklady použití

### Kompletní workflow doručení
1. `POST /couriers` - Vytvoř kurýra
2. `PATCH /couriers/{id}/status` - Nastav `available`
3. `PATCH /couriers/{id}/location` - Aktualizuj GPS
4. `POST /orders` - Vytvoř objednávku
5. `POST /dispatch/auto/{order_id}` - Přiřaď kurýra
6. `POST /orders/{id}/pickup` - Kurýr vyzvednul
7. `POST /orders/{id}/deliver` - Kurýr doručil

---
**Kontakt**: support@fooddelivery.cz | **Verze**: 2.0.0
""",
    openapi_tags=[
        {
            "name": "couriers",
            "description": "Správa kurýrů - vytváření, editace, lokace a stavy. Kurýr je osoba, která doručuje objednávky zákazníkům.",
        },
        {
            "name": "orders",
            "description": "Správa objednávek - vytváření, lifecycle a doručení. Objednávka představuje požadavek na doručení od místa vyzvednutí k zákazníkovi.",
        },
        {
            "name": "dispatch",
            "description": "Dispečink - přiřazování kurýrů k objednávkám. Automatické i manuální přiřazení s logováním historie.",
        },
        {
            "name": "Formuláře",
            "description": "CRUD operace nad formuláři - vytváření, čtení, mazání záznamů. Obsahuje easter egg mini hru.",
        },
        {
            "name": "Přílohy",
            "description": "Nahrávání a správa souborových příloh k formulářům. Podporuje PDF a TXT, max 1 MB.",
        },
        {
            "name": "Instrukce",
            "description": "Textové instrukce k formulářům - vytvoření, aktualizace, čtení.",
        },
        {
            "name": "Mini hra",
            "description": "Easter egg funkce - vyhodnocení tajných jmen (neo, trinity, morpheus, jan, pavla, matrix).",
        },
    ],
    contact={
        "name": "Food Delivery Support",
        "email": "support@fooddelivery.cz",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS - allow requests from mobile apps and development clients
# In production, replace allow_origins with explicit trusted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Přidání routerů
app.include_router(form_data_router, prefix="/api/v1")
app.include_router(couriers_router, prefix="/api/v1", tags=["couriers"])
app.include_router(orders_router, prefix="/api/v1", tags=["orders"])
app.include_router(dispatch_router, prefix="/api/v1", tags=["dispatch"])

@app.get("/")
def root():
    return {"message": "Moje App API is running!", "docs": "/docs"}