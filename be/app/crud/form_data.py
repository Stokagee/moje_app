from sqlalchemy.orm import Session
from app.models.form_data import FormData
from app.schemas.form_data import FormDataCreate
from app.models.attachment import Attachment
from app.models.instruction import Instruction
from app.schemas.form_data import AttachmentCreate, InstructionCreate
import base64
from typing import Final

ALLOWED_CONTENT_TYPES: Final[set[str]] = {"application/pdf", "text/plain"}
MAX_BYTES: Final[int] = 1 * 1024 * 1024  # 1 MB

def get_form_data(db: Session, form_data_id: int):
    """Získá jeden záznam FormData podle ID."""
    return db.query(FormData).filter(FormData.id == form_data_id).first()

def get_all_form_data(db: Session, skip: int = 0, limit: int = 100):
    """Získá všechny záznamy FormData s možností stránkování."""
    return db.query(FormData).offset(skip).limit(limit).all()

def create_form_data(db: Session, form_data: FormDataCreate):
    """Vytvoří nový záznam FormData."""
    db_form_data = FormData(**form_data.model_dump())  # Použijte .dict() pro Pydantic v1
    db.add(db_form_data)
    db.commit()
    db.refresh(db_form_data)
    return db_form_data

def delete_form_data(db: Session, form_data_id: int):
    """Smaže záznam FormData podle ID."""
    db_form_data = db.query(FormData).filter(FormData.id == form_data_id).first()
    if db_form_data:
        db.delete(db_form_data)
        db.commit()
        return True
    return False


def create_attachment(db: Session, form_id: int, payload: AttachmentCreate) -> Attachment:
    raw = base64.b64decode(payload.data_base64)
    ctype = payload.content_type or "application/octet-stream"
    if ctype not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Nepovolený typ souboru. Povolené: .txt, .pdf")
    if len(raw) > MAX_BYTES:
        raise ValueError("Soubor je příliš velký (max 1MB)")
    att = Attachment(
        form_id=form_id,
        filename=payload.filename,
        content_type=ctype,
        data=raw,
        instructions=payload.instructions,
    )
    db.add(att)
    db.commit()
    db.refresh(att)

    # Pokud dorazily instrukce spolu s přílohou, ulož je také do instructions tabulky (upsert)
    if payload.instructions and payload.instructions.strip():
        existing = db.query(Instruction).filter(Instruction.form_id == form_id).first()
        if existing:
            existing.text = payload.instructions
            db.add(existing)
        else:
            db.add(Instruction(form_id=form_id, text=payload.instructions))
        db.commit()
    return att


def get_attachments_for_form(db: Session, form_id: int):
    return db.query(Attachment).filter(Attachment.form_id == form_id).all()


def get_instruction_for_form(db: Session, form_id: int) -> Instruction | None:
    return db.query(Instruction).filter(Instruction.form_id == form_id).first()


def upsert_instruction(db: Session, form_id: int, payload: InstructionCreate) -> Instruction:
    inst = get_instruction_for_form(db, form_id)
    if inst:
        inst.text = payload.text
        db.add(inst)
    else:
        inst = Instruction(form_id=form_id, text=payload.text)
        db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst