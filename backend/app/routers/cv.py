"""CV router — POST /api/cv/upload and POST /api/cv/parse."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..core.config import get_settings
from ..core.db import get_database
from ..core.llm import extract_profile
from ..core.parsing import MAX_FILE_BYTES, extract_text
from ..models.profile import Profile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cv", tags=["CV"])


async def _handle_cv_upload(file: UploadFile) -> Dict[str, Any]:
    """Core handler for parsing an uploaded CV and persisting to MongoDB."""
    # 1. Size check
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_BYTES // (1024 * 1024)} MB.",
        )

    # 2. Text extraction
    try:
        raw_text = extract_text(
            filename=file.filename or "",
            file_bytes=file_bytes,
            content_type=file.content_type or "",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error extracting text from CV")
        raise HTTPException(status_code=422, detail=f"Error reading file: {exc}")

    # 3. LLM extraction
    try:
        extracted_data = extract_profile(raw_text)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error calling LLM for CV extraction")
        raise HTTPException(status_code=502, detail=f"AI extraction failed: {exc}")

    # 4. Build Profile model
    try:
        extracted_data["raw_text"] = raw_text
        profile = Profile.model_validate(extracted_data)
    except Exception as exc:
        logger.exception("Validation error building Profile model")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to validate structured profile: {exc}",
        )

    # 5. Persist to MongoDB Atlas 'profiles' collection
    inserted_id: str | None = None
    settings = get_settings()

    if settings.mongodb_uri:
        try:
            db = get_database()
            doc = profile.model_dump(exclude={"id", "profile_id"})
            result = await db["profiles"].insert_one(doc)
            inserted_id = str(result.inserted_id)
            logger.info("Successfully persisted profile %s to MongoDB", inserted_id)
        except Exception as exc:
            logger.warning("MongoDB insertion failed (%s); generating local ID", exc)
            inserted_id = str(uuid.uuid4())
    else:
        inserted_id = str(uuid.uuid4())

    profile.id = inserted_id
    profile.profile_id = inserted_id
    profile_dict = profile.model_dump()

    # 6. Return response with both top-level and nested structure
    return {
        "profile_id": inserted_id,
        "id": inserted_id,
        "name": profile.name,
        "email": profile.email,
        "skills": profile.skills,
        "education": [e.model_dump() for e in profile.education],
        "experience": [ex.model_dump() for ex in profile.experience],
        "interests": profile.interests,
        "summary": profile.summary,
        "raw_text": profile.raw_text,
        "profile": profile_dict,
    }


@router.post(
    "/upload",
    summary="Upload a CV, extract profile with AI, and persist to MongoDB",
    description=(
        "Upload a PDF or DOCX CV file. Extracts text, extracts structured profile "
        "using AI (Google Gemini / Claude), saves to MongoDB 'profiles' collection, "
        "and returns the saved profile and profile_id."
    ),
)
async def upload_cv(file: UploadFile = File(...)) -> Dict[str, Any]:
    return await _handle_cv_upload(file)


@router.post(
    "/parse",
    summary="Parse a CV and extract a structured profile (alias to /upload)",
)
async def parse_cv(file: UploadFile = File(...)) -> Dict[str, Any]:
    return await _handle_cv_upload(file)
