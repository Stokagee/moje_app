from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import base64


class FormDataBase(BaseModel):
    """Base form data."""

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="First name",
        json_schema_extra={"example": "Jan"}
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Last name",
        json_schema_extra={"example": "Novák"}
    )
    phone: str = Field(
        ...,
        min_length=9,
        max_length=25,
        description="Phone number (9-25 characters)",
        json_schema_extra={"example": "+420 123 456 789"}
    )
    gender: str = Field(
        ...,
        description="Gender: male, female, or other",
        json_schema_extra={"example": "male"}
    )
    email: EmailStr = Field(
        ...,
        description="Email address (must be unique in the system)",
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
    """Schema for creating a new form."""
    pass


class FormData(FormDataBase):
    """Form schema with ID (for reading from the database)."""

    id: int = Field(
        ...,
        description="Unique form identifier",
        json_schema_extra={"example": 1}
    )

    class Config:
        from_attributes = True


class FormDataResponse(FormData):
    """Extended response for the frontend with mini game result.

    - easter_egg: whether a match occurred (name matches a secret list)
    - secret_message: message for the frontend (displayable text)
    """

    easter_egg: bool | None = Field(
        None,
        description="True if the first/last name matches a secret token (mini game)"
    )
    secret_message: str | None = Field(
        None,
        description="Secret message displayed when an easter egg is triggered",
        json_schema_extra={"example": "Secret revealed: 'neo'! You have the eyes of a hawk."}
    )


class NameInput(BaseModel):
    """Input for evaluating a secret name in the mini game."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Text to check (name, word)",
        json_schema_extra={"example": "neo"}
    )


class GameResponse(BaseModel):
    """Mini game response — result of evaluating a secret name."""

    matched: bool = Field(
        ...,
        description="True if the text matches a secret token"
    )
    message: str | None = Field(
        None,
        description="Message for the user (only when matched=true)",
        json_schema_extra={"example": "Secret revealed: 'neo'! You have the eyes of a hawk."}
    )


# ============================================
# Attachment schemas
# ============================================

class AttachmentBase(BaseModel):
    """Basic attachment information."""

    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Filename including extension",
        json_schema_extra={"example": "document.pdf"}
    )
    content_type: str = Field(
        ...,
        description="File MIME type (application/pdf, text/plain)",
        json_schema_extra={"example": "application/pdf"}
    )
    instructions: Optional[str] = Field(
        None,
        max_length=5000,
        description="Optional instructions for the attachment",
        json_schema_extra={"example": "Scanned form to be signed"}
    )


class AttachmentCreate(AttachmentBase):
    """Schema for uploading a new attachment (data as base64)."""

    data_base64: str = Field(
        ...,
        description="File content encoded in base64. Maximum size after decoding: 1 MB.",
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
    """Attachment schema for reading (without binary data)."""

    id: int = Field(
        ...,
        description="Unique attachment identifier",
        json_schema_extra={"example": 1}
    )
    form_id: int = Field(
        ...,
        description="ID of the form this attachment belongs to",
        json_schema_extra={"example": 1}
    )

    class Config:
        from_attributes = True


# ============================================
# Instructions schemas
# ============================================

class InstructionBase(BaseModel):
    """Base instructions schema."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Instructions text for the form",
        json_schema_extra={"example": "Please fill in all required fields and submit the form."}
    )


class InstructionCreate(InstructionBase):
    """Schema for creating/updating instructions."""
    pass


class InstructionOut(InstructionBase):
    """Instructions schema for reading."""

    id: int = Field(
        ...,
        description="Unique instructions identifier",
        json_schema_extra={"example": 1}
    )
    form_id: int = Field(
        ...,
        description="ID of the form these instructions belong to",
        json_schema_extra={"example": 1}
    )

    class Config:
        from_attributes = True


# ============================================
# Response schemas for special responses
# ============================================

class DeleteResponse(BaseModel):
    """Response after deleting a record."""

    message: str = Field(
        ...,
        description="Confirmation message",
        json_schema_extra={"example": "Record deleted successfully"}
    )


class ErrorResponse(BaseModel):
    """Error response schema."""

    detail: str = Field(
        ...,
        description="Error description",
        json_schema_extra={"example": "Record not found"}
    )
