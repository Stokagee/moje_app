from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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

@router.post("/form/", response_model=FormDataResponse, response_model_exclude_none=True)
def create_form_data_endpoint(form_data: FormDataCreate, db: Session = Depends(get_db)):
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
    except Exception as e:
        logger.error(f"Chyba při vytváření záznamu: {str(e)}")
        raise HTTPException(status_code=500, detail="Nepodařilo se uložit data")

@router.get("/form/", response_model=list[FormDataSchema])
def read_form_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Získá všechny záznamy formuláře."""
    logger.debug(f"Získávání záznamů, skip: {skip}, limit: {limit}")
    form_data = get_all_form_data(db, skip=skip, limit=limit)
    return form_data

@router.get("/form/{form_data_id}", response_model=FormDataSchema)
def read_single_form_data(form_data_id: int, db: Session = Depends(get_db)):
    """Získá jeden konkrétní záznam formuláře podle ID."""
    logger.debug(f"Získávání záznamu s ID {form_data_id}")
    db_form_data = get_form_data(db, form_data_id=form_data_id)
    if db_form_data is None:
        logger.warning(f"Záznam s ID {form_data_id} nebyl nalezen")
        raise HTTPException(status_code=404, detail="Záznam nenalezen")
    return db_form_data

@router.delete("/form/{form_data_id}")
def delete_form_data_endpoint(form_data_id: int, db: Session = Depends(get_db)):
    """Smaže záznam formuláře podle ID."""
    try:
        logger.info(f"Pokus o smazání záznamu s ID {form_data_id}")
        deleted = delete_form_data(db=db, form_data_id=form_data_id)
        if not deleted:
            logger.warning(f"Záznam s ID {form_data_id} nebyl nalezen pro smazání")
            raise HTTPException(status_code=404, detail="Záznam nenalezen")
        logger.info(f"Záznam s ID {form_data_id} úspěšně smazán")
        return {"message": "Záznam úspěšně smazán"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při mazání záznamu: {str(e)}")
        raise HTTPException(status_code=500, detail="Nepodařilo se smazat záznam")


@router.post("/form/evaluate-name", response_model=GameResponse, response_model_exclude_none=True)
def evaluate_name_endpoint(payload: NameInput):
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


@router.post("/form/{form_id}/attachment", response_model=AttachmentOut)
def create_attachment_endpoint(form_id: int, payload: AttachmentCreate, db: Session = Depends(get_db)):
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


@router.get("/form/{form_id}/attachments", response_model=list[AttachmentOut])
def list_attachments_endpoint(form_id: int, db: Session = Depends(get_db)):
    # Ověřit existenci formu je volitelné (optimalizace); zde přeskočíme kvůli rychlosti
    return get_attachments_for_form(db, form_id)


@router.put("/form/{form_id}/instructions", response_model=InstructionOut)
def upsert_instructions_endpoint(form_id: int, payload: InstructionCreate, db: Session = Depends(get_db)):
    exists = get_form_data(db, form_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Záznam formuláře nenalezen")
    try:
        inst = upsert_instruction(db, form_id=form_id, payload=payload)
        return inst
    except Exception as e:
        logger.error("Chyba při ukládání instrukcí: %s", str(e))
        raise HTTPException(status_code=500, detail="Nepodařilo se uložit instrukce")


@router.get("/form/{form_id}/instructions", response_model=InstructionOut | None)
def get_instructions_endpoint(form_id: int, db: Session = Depends(get_db)):
    # nepovinně lze ověřit existenci formuláře
    return get_instruction_for_form(db, form_id)