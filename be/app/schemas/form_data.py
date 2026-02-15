from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import base64


class FormDataBase(BaseModel):
    """Základní data formuláře."""

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Křestní jméno",
        json_schema_extra={"example": "Jan"}
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Příjmení",
        json_schema_extra={"example": "Novák"}
    )
    phone: str = Field(
        ...,
        min_length=9,
        max_length=25,
        description="Telefonní číslo (9-25 znaků)",
        json_schema_extra={"example": "+420 123 456 789"}
    )
    gender: str = Field(
        ...,
        description="Pohlaví: male, female nebo other",
        json_schema_extra={"example": "male"}
    )
    email: EmailStr = Field(
        ...,
        description="Emailová adresa (musí být unikátní v systému)",
        json_schema_extra={"example": "jan.novak@example.com"}
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        # Accept both full words and single letters
        allowed = ("male", "female", "other", "m", "f", "o")
        normalized = v.lower()
        if normalized not in allowed:
            raise ValueError(f"Pohlaví musí být jedno z: male, female, other")
        # Normalize to full word
        mapping = {"m": "male", "f": "female", "o": "other"}
        return mapping.get(normalized, normalized)


class FormDataCreate(FormDataBase):
    """Schéma pro vytvoření nového formuláře."""
    pass


class FormData(FormDataBase):
    """Schéma formuláře s ID (pro čtení z databáze)."""

    id: int = Field(
        ...,
        description="Unikátní identifikátor formuláře",
        json_schema_extra={"example": 1}
    )

    class Config:
        from_attributes = True


class FormDataResponse(FormData):
    """Rozšířená odpověď pro FE s výsledkem mini-hry.

    - easter_egg: zda došlo k zásahu (jméno odpovídá některému tajnému seznamu)
    - secret_message: zpráva pro FE (zobrazitelná hláška)
    """

    easter_egg: bool | None = Field(
        None,
        description="True pokud jméno/příjmení odpovídá tajnému tokenu (mini hra)"
    )
    secret_message: str | None = Field(
        None,
        description="Tajná zpráva zobrazená při shodě s easter egg",
        json_schema_extra={"example": "Tajemství odhaleno: 'neo'! Máš oko sokola."}
    )


class NameInput(BaseModel):
    """Vstup pro vyhodnocení tajného jména v mini hře."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Text k ověření (jméno, slovo)",
        json_schema_extra={"example": "neo"}
    )


class GameResponse(BaseModel):
    """Odpověď mini-hry - výsledek vyhodnocení tajného jména."""

    matched: bool = Field(
        ...,
        description="True pokud text odpovídá tajnému tokenu"
    )
    message: str | None = Field(
        None,
        description="Zpráva pro uživatele (pouze při matched=true)",
        json_schema_extra={"example": "Tajemství odhaleno: 'neo'! Máš oko sokola."}
    )


# ============================================
# Attachment schémata
# ============================================

class AttachmentBase(BaseModel):
    """Základní informace o příloze."""

    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Název souboru včetně přípony",
        json_schema_extra={"example": "dokument.pdf"}
    )
    content_type: str = Field(
        ...,
        description="MIME typ souboru (application/pdf, text/plain)",
        json_schema_extra={"example": "application/pdf"}
    )
    instructions: Optional[str] = Field(
        None,
        max_length=5000,
        description="Volitelné instrukce k příloze",
        json_schema_extra={"example": "Naskenovaný formulář k podpisu"}
    )


class AttachmentCreate(AttachmentBase):
    """Schéma pro nahrání nové přílohy (data jako base64)."""

    data_base64: str = Field(
        ...,
        description="Obsah souboru zakódovaný v base64. Maximální velikost po dekódování: 1 MB.",
        json_schema_extra={"example": "JVBERi0xLjQKJeLjz9MKMyAwIG9iago8PC..."}
    )

    @field_validator("data_base64")
    @classmethod
    def validate_base64_size(cls, v: str) -> str:
        try:
            decoded = base64.b64decode(v)
            max_size = 1 * 1024 * 1024  # 1 MB
            if len(decoded) > max_size:
                raise ValueError(f"Soubor překračuje limit 1 MB (aktuální: {len(decoded)} bajtů)")
        except base64.binascii.Error:
            raise ValueError("Neplatný base64 formát")
        return v

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        allowed = ("application/pdf", "text/plain")
        if v.lower() not in allowed:
            raise ValueError(f"Povolené typy souborů: {', '.join(allowed)}")
        return v.lower()


class AttachmentOut(AttachmentBase):
    """Schéma přílohy pro čtení (bez binárních dat)."""

    id: int = Field(
        ...,
        description="Unikátní identifikátor přílohy",
        json_schema_extra={"example": 1}
    )
    form_id: int = Field(
        ...,
        description="ID formuláře, ke kterému příloha patří",
        json_schema_extra={"example": 1}
    )

    class Config:
        from_attributes = True


# ============================================
# Instructions schémata
# ============================================

class InstructionBase(BaseModel):
    """Základní schéma instrukcí."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text instrukcí k formuláři",
        json_schema_extra={"example": "Vyplňte prosím všechna povinná pole a odešlete formulář."}
    )


class InstructionCreate(InstructionBase):
    """Schéma pro vytvoření/aktualizaci instrukcí."""
    pass


class InstructionOut(InstructionBase):
    """Schéma instrukcí pro čtení."""

    id: int = Field(
        ...,
        description="Unikátní identifikátor instrukcí",
        json_schema_extra={"example": 1}
    )
    form_id: int = Field(
        ...,
        description="ID formuláře, ke kterému instrukce patří",
        json_schema_extra={"example": 1}
    )

    class Config:
        from_attributes = True


# ============================================
# Response schémata pro speciální odpovědi
# ============================================

class DeleteResponse(BaseModel):
    """Odpověď po smazání záznamu."""

    message: str = Field(
        ...,
        description="Potvrzovací zpráva",
        json_schema_extra={"example": "Záznam úspěšně smazán"}
    )


class ErrorResponse(BaseModel):
    """Schéma chybové odpovědi."""

    detail: str = Field(
        ...,
        description="Popis chyby",
        json_schema_extra={"example": "Záznam nenalezen"}
    )
