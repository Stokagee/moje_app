from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.form_data import (
    FormDataCreate,
    FormData as FormDataSchema,
    FormDataResponse,
    NameInput,
    GameResponse,
    AttachmentCreate,
    AttachmentOut,
    InstructionCreate,
    InstructionOut,
    DeleteResponse,
    ErrorResponse,
)
from app.crud.form_data import (
    get_form_data,
    get_all_form_data,
    create_form_data,
    delete_form_data,
    create_attachment,
    get_attachments_for_form,
    get_instruction_for_form,
    upsert_instruction,
)
from app.database import get_db
from app.services.form_data import build_easter_egg_from_names, evaluate_text_for_game
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================
# FORMULÁŘE - CRUD operace
# ============================================

@router.post(
    "/form/",
    response_model=FormDataResponse,
    response_model_exclude_none=True,
    status_code=201,
    summary="Vytvoření nového formuláře",
    description="""
Vytvoří nový záznam formuláře v databázi.

**Mini hra (Easter Egg):**
Pokud křestní jméno nebo příjmení odpovídá tajnému tokenu
(neo, trinity, morpheus, jan, pavla, matrix), vrátí se `easter_egg=true`
a `secret_message` s gratulací.

**Validace:**
- Email musí být unikátní v systému
- Pohlaví: male, female, other
- Telefon: 9-15 znaků
    """,
    tags=["Formuláře"],
    responses={
        201: {
            "description": "Formulář úspěšně vytvořen",
            "model": FormDataResponse,
        },
        400: {
            "description": "Email již existuje v systému",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validační chyba (neplatná data)",
        },
        500: {
            "description": "Interní chyba serveru",
            "model": ErrorResponse,
        },
    },
)
def create_form_data_endpoint(
    form_data: FormDataCreate = Body(
        ...,
        description="Data nového formuláře",
    ),
    db: Session = Depends(get_db),
):
    """Vytvoří nový záznam z dat formuláře."""
    try:
        logger.info(f"Pokus o vytvoření záznamu pro {form_data.email}")
        created_data = create_form_data(db=db, form_data=form_data)
        # Mini hra: easter egg podle jména/příjmení
        egg, msg = build_easter_egg_from_names(created_data.first_name, created_data.last_name)
        # Sestavíme odpověď a přidáme "egg" pole pouze při shodě
        base_kwargs = dict(
            id=created_data.id,
            first_name=created_data.first_name,
            last_name=created_data.last_name,
            phone=created_data.phone,
            gender=created_data.gender,
            email=created_data.email,
        )
        if egg:
            base_kwargs.update({"easter_egg": True, "secret_message": msg})
        response: FormDataResponse = FormDataResponse(**base_kwargs)
        logger.info(f"Záznam úspěšně vytvořen s ID {created_data.id}; easter_egg={egg}")
        return response
    except IntegrityError as e:
        logger.warning(f"Duplicate email attempt: {form_data.email}")
        raise HTTPException(status_code=400, detail="Email již existuje v systému")
    except Exception as e:
        logger.error(f"Chyba při vytváření záznamu: {str(e)}")
        raise HTTPException(status_code=500, detail="Nepodařilo se uložit data")


@router.get(
    "/form/",
    response_model=list[FormDataSchema],
    summary="Seznam všech formulářů",
    description="""
Vrátí stránkovaný seznam všech formulářů v databázi.

**Stránkování:**
- `skip`: Počet záznamů k přeskočení (výchozí: 0)
- `limit`: Maximální počet vrácených záznamů (výchozí: 100, max: 1000)

**Příklad:** `GET /form/?skip=10&limit=20` vrátí záznamy 11-30.
    """,
    tags=["Formuláře"],
    responses={
        200: {
            "description": "Seznam formulářů",
            "model": list[FormDataSchema],
        },
    },
)
def read_form_data(
    skip: int = Query(
        0,
        ge=0,
        description="Počet záznamů k přeskočení (pro stránkování)",
        example=0,
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximální počet vrácených záznamů",
        example=100,
    ),
    db: Session = Depends(get_db),
):
    """Získá všechny záznamy formuláře."""
    logger.debug(f"Získávání záznamů, skip: {skip}, limit: {limit}")
    form_data = get_all_form_data(db, skip=skip, limit=limit)
    return form_data


@router.get(
    "/form/{form_data_id}",
    response_model=FormDataSchema,
    summary="Detail formuláře",
    description="""
Vrátí detail jednoho konkrétního formuláře podle jeho ID.

Pokud formulář s daným ID neexistuje, vrátí se chyba 404.
    """,
    tags=["Formuláře"],
    responses={
        200: {
            "description": "Detail formuláře",
            "model": FormDataSchema,
        },
        404: {
            "description": "Formulář s daným ID nenalezen",
            "model": ErrorResponse,
        },
    },
)
def read_single_form_data(
    form_data_id: int = Path(
        ...,
        gt=0,
        description="Unikátní ID formuláře",
        example=1,
    ),
    db: Session = Depends(get_db),
):
    """Získá jeden konkrétní záznam formuláře podle ID."""
    logger.debug(f"Získávání záznamu s ID {form_data_id}")
    db_form_data = get_form_data(db, form_data_id=form_data_id)
    if db_form_data is None:
        logger.warning(f"Záznam s ID {form_data_id} nebyl nalezen")
        raise HTTPException(status_code=404, detail="Záznam nenalezen")
    return db_form_data


@router.delete(
    "/form/{form_data_id}",
    response_model=DeleteResponse,
    summary="Smazání formuláře",
    description="""
Smaže formulář podle ID včetně všech souvisejících dat (přílohy, instrukce).

**Kaskádové mazání:** Automaticky se smažou i všechny přílohy a instrukce
přiřazené k tomuto formuláři.

Pokud formulář s daným ID neexistuje, vrátí se chyba 404.
    """,
    tags=["Formuláře"],
    responses={
        200: {
            "description": "Formulář úspěšně smazán",
            "model": DeleteResponse,
        },
        404: {
            "description": "Formulář s daným ID nenalezen",
            "model": ErrorResponse,
        },
        500: {
            "description": "Chyba při mazání",
            "model": ErrorResponse,
        },
    },
)
def delete_form_data_endpoint(
    form_data_id: int = Path(
        ...,
        gt=0,
        description="ID formuláře ke smazání",
        example=1,
    ),
    db: Session = Depends(get_db),
):
    """Smaže záznam formuláře podle ID."""
    try:
        logger.info(f"Pokus o smazání záznamu s ID {form_data_id}")
        deleted = delete_form_data(db=db, form_data_id=form_data_id)
        if not deleted:
            logger.warning(f"Záznam s ID {form_data_id} nebyl nalezen pro smazání")
            raise HTTPException(status_code=404, detail="Záznam nenalezen")
        logger.info(f"Záznam s ID {form_data_id} úspěšně smazán")
        return DeleteResponse(message="Záznam úspěšně smazán")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při mazání záznamu: {str(e)}")
        raise HTTPException(status_code=500, detail="Nepodařilo se smazat záznam")


# ============================================
# MINI HRA - Easter Egg vyhodnocení
# ============================================

@router.post(
    "/form/evaluate-name",
    response_model=GameResponse,
    response_model_exclude_none=True,
    summary="Vyhodnocení tajného jména (Mini hra)",
    description="""
Zkontroluje, zda zadaný text odpovídá některému z tajných tokenů.

**Tajné tokeny:** neo, trinity, morpheus, jan, pavla, matrix

**Pravidla:**
- Vyhodnocení je case-insensitive (Neo = neo = NEO)
- Ignoruje bílé znaky na začátku a konci
- Neprovádí žádnou práci s databází

**Odpověď:**
- `matched=true` + `message` při shodě
- `matched=false` + `message=null` bez shody
    """,
    tags=["Mini hra"],
    responses={
        200: {
            "description": "Výsledek vyhodnocení",
            "content": {
                "application/json": {
                    "examples": {
                        "shoda": {
                            "summary": "Tajné jméno nalezeno",
                            "value": {
                                "matched": True,
                                "message": "Tajemství odhaleno: 'neo'! Máš oko sokola."
                            }
                        },
                        "bez_shody": {
                            "summary": "Tajné jméno nenalezeno",
                            "value": {
                                "matched": False,
                                "message": None
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Chyba při vyhodnocení",
            "model": ErrorResponse,
        },
    },
)
def evaluate_name_endpoint(
    payload: NameInput = Body(
        ...,
        description="Text k ověření proti tajným tokenům",
    ),
):
    """Vyhodnotí zadaný text proti tajným jménům a vrátí zprávu pro FE.

    Neprovádí žádnou práci s DB; čistě logika mini hry.
    """
    try:
        matched, message = evaluate_text_for_game(payload.text)
        logger.debug("Evaluate-name: '%s' => matched=%s", payload.text, matched)
        return GameResponse(matched=matched, message=message)
    except Exception as e:
        logger.error("Chyba v evaluate-name: %s", str(e))
        raise HTTPException(status_code=500, detail="Chyba při vyhodnocení jména")


# ============================================
# PŘÍLOHY - Nahrávání a správa souborů
# ============================================

@router.post(
    "/form/{form_id}/attachment",
    response_model=AttachmentOut,
    status_code=201,
    summary="Nahrání přílohy k formuláři",
    description="""
Nahraje soubor (přílohu) k existujícímu formuláři.

**Omezení:**
- Maximální velikost souboru: **1 MB** (po dekódování z base64)
- Povolené MIME typy: `application/pdf`, `text/plain`

**Formát dat:**
Data souboru se odesílají jako base64 string v JSON těle požadavku.

**Instrukce:**
Volitelně lze přidat textové instrukce k příloze.
    """,
    tags=["Přílohy"],
    responses={
        201: {
            "description": "Příloha úspěšně nahrána",
            "model": AttachmentOut,
        },
        400: {
            "description": "Neplatný soubor (špatný formát, velikost, MIME typ)",
            "model": ErrorResponse,
        },
        404: {
            "description": "Formulář s daným ID nenalezen",
            "model": ErrorResponse,
        },
        500: {
            "description": "Chyba při ukládání přílohy",
            "model": ErrorResponse,
        },
    },
)
def create_attachment_endpoint(
    form_id: int = Path(
        ...,
        gt=0,
        description="ID formuláře, ke kterému se přiloha přidává",
        example=1,
    ),
    payload: AttachmentCreate = Body(
        ...,
        description="Data přílohy (soubor v base64)",
    ),
    db: Session = Depends(get_db),
):
    """Vytvoří přílohu vázanou na existující form záznam.

    Příjem dat jako base64 (pro jednoduchost). Alternativně by šel multipart/form-data s UploadFile.
    """
    # Ověřit, že form existuje
    exists = get_form_data(db, form_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Záznam formuláře nenalezen")
    try:
        att = create_attachment(db, form_id=form_id, payload=payload)
        return att
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Chyba při ukládání přílohy: %s", str(e))
        raise HTTPException(status_code=500, detail="Nepodařilo se uložit přílohu")


@router.get(
    "/form/{form_id}/attachments",
    response_model=list[AttachmentOut],
    summary="Seznam příloh formuláře",
    description="""
Vrátí seznam všech příloh přiřazených k danému formuláři.

**Poznámka:** Vrací pouze metadata příloh (ID, název, typ), ne samotný obsah souborů.
    """,
    tags=["Přílohy"],
    responses={
        200: {
            "description": "Seznam příloh",
            "model": list[AttachmentOut],
        },
    },
)
def list_attachments_endpoint(
    form_id: int = Path(
        ...,
        gt=0,
        description="ID formuláře",
        example=1,
    ),
    db: Session = Depends(get_db),
):
    """Vrátí všechny přílohy pro daný formulář."""
    return get_attachments_for_form(db, form_id)


# ============================================
# INSTRUKCE - Textové pokyny k formulářům
# ============================================

@router.put(
    "/form/{form_id}/instructions",
    response_model=InstructionOut,
    summary="Vytvoření nebo aktualizace instrukcí",
    description="""
Vytvoří nebo aktualizuje instrukce k formuláři (upsert operace).

**Chování:**
- Pokud instrukce pro daný formulář **neexistují**, vytvoří se nové
- Pokud instrukce **existují**, přepíší se novým textem

Každý formulář může mít maximálně jedny instrukce (vztah 1:1).
    """,
    tags=["Instrukce"],
    responses={
        200: {
            "description": "Instrukce vytvořeny/aktualizovány",
            "model": InstructionOut,
        },
        404: {
            "description": "Formulář s daným ID nenalezen",
            "model": ErrorResponse,
        },
        500: {
            "description": "Chyba při ukládání instrukcí",
            "model": ErrorResponse,
        },
    },
)
def upsert_instructions_endpoint(
    form_id: int = Path(
        ...,
        gt=0,
        description="ID formuláře",
        example=1,
    ),
    payload: InstructionCreate = Body(
        ...,
        description="Text instrukcí",
    ),
    db: Session = Depends(get_db),
):
    """Vytvoří nebo aktualizuje instrukce pro formulář."""
    exists = get_form_data(db, form_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Záznam formuláře nenalezen")
    try:
        inst = upsert_instruction(db, form_id=form_id, payload=payload)
        return inst
    except Exception as e:
        logger.error("Chyba při ukládání instrukcí: %s", str(e))
        raise HTTPException(status_code=500, detail="Nepodařilo se uložit instrukce")


@router.get(
    "/form/{form_id}/instructions",
    response_model=InstructionOut | None,
    summary="Získání instrukcí formuláře",
    description="""
Vrátí instrukce přiřazené k formuláři.

**Návratové hodnoty:**
- Objekt instrukcí, pokud existují
- `null`, pokud formulář nemá žádné instrukce
    """,
    tags=["Instrukce"],
    responses={
        200: {
            "description": "Instrukce formuláře (nebo null)",
            "model": InstructionOut,
        },
    },
)
def get_instructions_endpoint(
    form_id: int = Path(
        ...,
        gt=0,
        description="ID formuláře",
        example=1,
    ),
    db: Session = Depends(get_db),
):
    """Vrátí instrukce pro daný formulář."""
    return get_instruction_for_form(db, form_id)
