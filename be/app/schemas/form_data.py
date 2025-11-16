from pydantic import BaseModel, EmailStr
from typing import Optional

class FormDataBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    gender: str
    email: EmailStr

class FormDataCreate(FormDataBase):
    pass

class FormData(FormDataBase):
    id: int

    class Config:
        from_attributes = True  # Nahrazuje `orm_mode = True` ve Pydantic v2


class FormDataResponse(FormData):
    """Rozšířená odpověď pro FE s výsledkem mini-hry.

    - easter_egg: zda došlo k zásahu (jméno odpovídá některému tajnému seznamu)
    - secret_message: zpráva pro FE (zobrazitelná hláška)
    """
    easter_egg: bool | None = None
    secret_message: str | None = None


class NameInput(BaseModel):
    """Vstup pro samostatné ověření jména/slova."""
    text: str


class GameResponse(BaseModel):
    """Odpověď mini-hry pro FE."""
    matched: bool
    message: str | None = None


# Attachment schémata
class AttachmentBase(BaseModel):
    filename: str
    content_type: str
    instructions: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    # data jako base64 string (příjem přes JSON) – alternativně multipart v endpointu
    data_base64: str


class AttachmentOut(AttachmentBase):
    id: int
    form_id: int
    class Config:
        from_attributes = True


# Instructions schémata (nezávislá na přílohách)
class InstructionBase(BaseModel):
    text: str


class InstructionCreate(InstructionBase):
    pass


class InstructionOut(InstructionBase):
    id: int
    form_id: int
    class Config:
        from_attributes = True