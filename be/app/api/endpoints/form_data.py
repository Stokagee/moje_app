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
# FORMS - CRUD operations
# ============================================

@router.post(
    "/form/",
    response_model=FormDataResponse,
    response_model_exclude_none=True,
    status_code=201,
    summary="Create a new form",
    description="""
Creates a new form record in the database.

**Mini game (Easter Egg):**
If the first name or last name matches a secret token
(neo, trinity, morpheus, jan, pavla, matrix), the response includes `easter_egg=true`
and a `secret_message` with a congratulation.

**Validation:**
- Email must be unique in the system
- Gender: male, female, other
- Phone: 9-15 characters
    """,
    tags=["Forms"],
    responses={
        201: {
            "description": "Form created successfully",
            "model": FormDataResponse,
        },
        400: {
            "description": "Email already exists in the system",
            "model": ErrorResponse,
        },
        409: {
            "description": "Conflict - email already exists",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validation error (invalid data)",
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        },
    },
)
def create_form_data_endpoint(
    form_data: FormDataCreate = Body(
        ...,
        description="New form data",
    ),
    db: Session = Depends(get_db),
):
    """Creates a new record from form data."""
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
        db.rollback()  # Reset session state after IntegrityError
        logger.warning(f"Duplicate email attempt: {form_data.email}")
        raise HTTPException(status_code=409, detail="Email již existuje v systému")
    except Exception as e:
        logger.error(f"Chyba při vytváření záznamu: {str(e)}")
        raise HTTPException(status_code=500, detail="Nepodařilo se uložit data")


@router.get(
    "/form/",
    response_model=list[FormDataSchema],
    summary="List all forms",
    description="""
Returns a paginated list of all forms in the database.

**Pagination:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)

**Example:** `GET /form/?skip=10&limit=20` returns records 11-30.
    """,
    tags=["Forms"],
    responses={
        200: {
            "description": "List of forms",
            "model": list[FormDataSchema],
        },
    },
)
def read_form_data(
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip (for pagination)",
        example=0,
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of records to return",
        example=100,
    ),
    db: Session = Depends(get_db),
):
    """Gets all form records."""
    logger.debug(f"Získávání záznamů, skip: {skip}, limit: {limit}")
    form_data = get_all_form_data(db, skip=skip, limit=limit)
    return form_data


@router.get(
    "/form/{form_data_id}",
    response_model=FormDataSchema,
    summary="Form detail",
    description="""
Returns the detail of a single form by its ID.

If no form with the given ID exists, a 404 error is returned.
    """,
    tags=["Forms"],
    responses={
        200: {
            "description": "Form detail",
            "model": FormDataSchema,
        },
        404: {
            "description": "Form with the given ID not found",
            "model": ErrorResponse,
        },
    },
)
def read_single_form_data(
    form_data_id: int = Path(
        ...,
        gt=0,
        description="Unique form ID",
        example=1,
    ),
    db: Session = Depends(get_db),
):
    """Gets a single form record by ID."""
    logger.debug(f"Získávání záznamu s ID {form_data_id}")
    db_form_data = get_form_data(db, form_data_id=form_data_id)
    if db_form_data is None:
        logger.warning(f"Záznam s ID {form_data_id} nebyl nalezen")
        raise HTTPException(status_code=404, detail="Záznam nenalezen")
    return db_form_data


@router.delete(
    "/form/{form_data_id}",
    response_model=DeleteResponse,
    summary="Delete a form",
    description="""
Deletes a form by ID including all related data (attachments, instructions).

**Cascade delete:** All attachments and instructions linked to this form
are automatically deleted as well.

If no form with the given ID exists, a 404 error is returned.
    """,
    tags=["Forms"],
    responses={
        200: {
            "description": "Form deleted successfully",
            "model": DeleteResponse,
        },
        404: {
            "description": "Form with the given ID not found",
            "model": ErrorResponse,
        },
        500: {
            "description": "Error during deletion",
            "model": ErrorResponse,
        },
    },
)
def delete_form_data_endpoint(
    form_data_id: int = Path(
        ...,
        gt=0,
        description="Form ID to delete",
        example=1,
    ),
    db: Session = Depends(get_db),
):
    """Deletes a form record by ID."""
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
# MINI GAME - Easter Egg evaluation
# ============================================

@router.post(
    "/form/evaluate-name",
    response_model=GameResponse,
    response_model_exclude_none=True,
    summary="Evaluate a secret name (Mini game)",
    description="""
Checks whether the given text matches one of the secret tokens.

**Secret tokens:** neo, trinity, morpheus, jan, pavla, matrix

**Rules:**
- Evaluation is case-insensitive (Neo = neo = NEO)
- Leading and trailing whitespace is ignored
- No database operations are performed

**Response:**
- `matched=true` + `message` on a match
- `matched=false` + `message=null` on no match
    """,
    tags=["Mini game"],
    responses={
        200: {
            "description": "Evaluation result",
            "content": {
                "application/json": {
                    "examples": {
                        "match": {
                            "summary": "Secret name found",
                            "value": {
                                "matched": True,
                                "message": "Secret revealed: 'neo'! You have the eyes of a hawk."
                            }
                        },
                        "no_match": {
                            "summary": "Secret name not found",
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
            "description": "Evaluation error",
            "model": ErrorResponse,
        },
    },
)
def evaluate_name_endpoint(
    payload: NameInput = Body(
        ...,
        description="Text to check against secret tokens",
    ),
):
    """Evaluates the given text against secret names and returns a message for the FE.

    Does not perform any DB operations; purely mini game logic.
    """
    try:
        matched, message = evaluate_text_for_game(payload.text)
        logger.debug("Evaluate-name: '%s' => matched=%s", payload.text, matched)
        return GameResponse(matched=matched, message=message)
    except Exception as e:
        logger.error("Chyba v evaluate-name: %s", str(e))
        raise HTTPException(status_code=500, detail="Chyba při vyhodnocení jména")


# ============================================
# ATTACHMENTS - File upload and management
# ============================================

@router.post(
    "/form/{form_id}/attachment",
    response_model=AttachmentOut,
    status_code=201,
    summary="Upload an attachment to a form",
    description="""
Uploads a file (attachment) to an existing form.

**Limits:**
- Maximum file size: **1 MB** (after base64 decoding)
- Allowed MIME types: `application/pdf`, `text/plain`

**Data format:**
File data is sent as a base64 string in the JSON request body.

**Instructions:**
Optionally, text instructions can be attached to the file.
    """,
    tags=["Attachments"],
    responses={
        201: {
            "description": "Attachment uploaded successfully",
            "model": AttachmentOut,
        },
        400: {
            "description": "Invalid file (wrong format, size, or MIME type)",
            "model": ErrorResponse,
        },
        404: {
            "description": "Form with the given ID not found",
            "model": ErrorResponse,
        },
        500: {
            "description": "Error saving attachment",
            "model": ErrorResponse,
        },
    },
)
def create_attachment_endpoint(
    form_id: int = Path(
        ...,
        gt=0,
        description="Form ID to attach the file to",
        example=1,
    ),
    payload: AttachmentCreate = Body(
        ...,
        description="Attachment data (file in base64)",
    ),
    db: Session = Depends(get_db),
):
    """Creates an attachment linked to an existing form record.

    Receives data as base64 (for simplicity). Alternatively multipart/form-data with UploadFile could be used.
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
    summary="List form attachments",
    description="""
Returns a list of all attachments linked to the given form.

**Note:** Returns only attachment metadata (ID, filename, type), not the file content itself.
    """,
    tags=["Attachments"],
    responses={
        200: {
            "description": "List of attachments",
            "model": list[AttachmentOut],
        },
    },
)
def list_attachments_endpoint(
    form_id: int = Path(
        ...,
        gt=0,
        description="Form ID",
        example=1,
    ),
    db: Session = Depends(get_db),
):
    """Returns all attachments for the given form."""
    return get_attachments_for_form(db, form_id)


# ============================================
# INSTRUCTIONS - Text instructions for forms
# ============================================

@router.put(
    "/form/{form_id}/instructions",
    response_model=InstructionOut,
    summary="Create or update instructions",
    description="""
Creates or updates instructions for a form (upsert operation).

**Behaviour:**
- If instructions for the given form **do not exist**, new ones are created
- If instructions **already exist**, they are overwritten with the new text

Each form can have at most one set of instructions (1:1 relationship).
    """,
    tags=["Instructions"],
    responses={
        200: {
            "description": "Instructions created/updated",
            "model": InstructionOut,
        },
        404: {
            "description": "Form with the given ID not found",
            "model": ErrorResponse,
        },
        500: {
            "description": "Error saving instructions",
            "model": ErrorResponse,
        },
    },
)
def upsert_instructions_endpoint(
    form_id: int = Path(
        ...,
        gt=0,
        description="Form ID",
        example=1,
    ),
    payload: InstructionCreate = Body(
        ...,
        description="Instructions text",
    ),
    db: Session = Depends(get_db),
):
    """Creates or updates instructions for a form."""
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
    summary="Get form instructions",
    description="""
Returns the instructions linked to a form.

**Return values:**
- Instructions object if they exist
- `null` if the form has no instructions
    """,
    tags=["Instructions"],
    responses={
        200: {
            "description": "Form instructions (or null)",
            "model": InstructionOut,
        },
    },
)
def get_instructions_endpoint(
    form_id: int = Path(
        ...,
        gt=0,
        description="Form ID",
        example=1,
    ),
    db: Session = Depends(get_db),
):
    """Returns instructions for the given form."""
    return get_instruction_for_form(db, form_id)
