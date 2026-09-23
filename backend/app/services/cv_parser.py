"""CV text extraction and AI-powered profile parsing service."""
from __future__ import annotations

from typing import Dict, Any
from ..core.parsing import extract_text, MAX_FILE_BYTES, ALLOWED_EXTENSIONS
from ..core.llm import extract_profile
from ..schemas.cv import CVProfile, Profile


def parse_cv_with_ai(raw_text: str) -> Profile:
    """Send CV text to configured LLM (Gemini free tier / fallback) and return validated Profile."""
    profile_data: Dict[str, Any] = extract_profile(raw_text)
    profile_data["raw_text"] = raw_text
    return Profile.model_validate(profile_data)


# Alias for backward compatibility
parse_cv_with_claude = parse_cv_with_ai

__all__ = [
    "ALLOWED_EXTENSIONS",
    "CVProfile",
    "MAX_FILE_BYTES",
    "Profile",
    "extract_text",
    "extract_profile",
    "parse_cv_with_ai",
    "parse_cv_with_claude",
]
