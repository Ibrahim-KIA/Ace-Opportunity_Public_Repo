"""LLM extraction module supporting Google Gemini with Anthropic fallback."""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

from .config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are an expert CV parser and career matching analyst. Given the raw text of a CV / resume, extract a structured candidate profile.
Return ONLY a valid JSON object matching the exact schema below. Do NOT output any markdown backticks, fences (e.g. ```json), or explanatory text.

{
  "name": "<candidate's full name, or null if not found>",
  "email": "<candidate's email address, or null if not found>",
  "skills": ["<skill 1>", "<skill 2>"],
  "education": [
    {
      "institution": "<school or university name>",
      "degree": "<degree type, e.g. BSc, MSc, High School, or null>",
      "field": "<major or field of study, or null>",
      "start_year": "<start year YYYY, or null>",
      "end_year": "<graduation year YYYY or 'Present', or null>",
      "year": "<year or graduation date, or null>"
    }
  ],
  "experience": [
    {
      "organisation": "<company or organization name>",
      "organization": "<company or organization name>",
      "role": "<job title / role>",
      "start_date": "<start date e.g. Sep 2022, or null>",
      "end_date": "<end date or 'Present', or null>",
      "duration": "<e.g. 2022 - 2024, or null>",
      "description": "<concise summary of accomplishments and duties, or null>"
    }
  ],
  "interests": ["<interest or career aspiration 1>", "<interest 2>"],
  "summary": "<2-3 sentence professional overview summarizing who the candidate is, their key strengths, and what opportunities they are suited for>"
}

Strict Rules:
- Output MUST be valid parseable JSON.
- Never invent information not present in the CV.
- Keep skills concise (e.g., "Python", "React", "Financial Modeling").
- If education or experience is empty or missing, provide an empty list [].
"""


def _clean_json_text(text: str) -> str:
    """Strip code fences, markdown tags, and leading/trailing whitespace."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    # Find first '{' and last '}'
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return text.strip()


def _parse_json_with_retry(raw_output: str) -> Dict[str, Any]:
    """Parse JSON string, attempting fence stripping on failure."""
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = _clean_json_text(raw_output)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Failed to parse LLM output as JSON. Output was: {raw_output[:300]}"
            ) from exc


def _mock_extract_profile(cv_text: str) -> Dict[str, Any]:
    """Fallback heuristic extractor for offline development and testing."""
    lines = [line.strip() for line in cv_text.splitlines() if line.strip()]
    first_line = lines[0] if lines else "Candidate"
    
    # Try finding an email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", cv_text)
    email = email_match.group(0) if email_match else None

    # Common skills detection
    common_skills = [
        "Python", "JavaScript", "TypeScript", "React", "FastAPI", "Node.js",
        "SQL", "MongoDB", "PostgreSQL", "Docker", "Git", "Machine Learning",
        "Data Analysis", "Communication", "Leadership", "Research"
    ]
    detected_skills = [s for s in common_skills if s.lower() in cv_text.lower()]
    if not detected_skills:
        detected_skills = ["Software Development", "Problem Solving"]

    return {
        "name": first_line[:50],
        "email": email,
        "skills": detected_skills,
        "education": [
            {
                "institution": "University / Institute",
                "degree": "Bachelor of Science",
                "field": "Computer Science / STEM",
                "start_year": "2020",
                "end_year": "2024",
                "year": "2024",
            }
        ],
        "experience": [
            {
                "organisation": "Technology Organization",
                "organization": "Technology Organization",
                "role": "Software Developer Intern",
                "start_date": "Jun 2023",
                "end_date": "Sep 2023",
                "duration": "Jun 2023 – Sep 2023",
                "description": "Contributed to software engineering projects and development.",
            }
        ],
        "interests": ["Technology", "Innovation", "Career Development"],
        "summary": f"Motivated candidate with background in {', '.join(detected_skills[:3])}.",
    }


def extract_profile_with_gemini(cv_text: str, api_key: str) -> Dict[str, Any]:
    """Extract profile using Google GenAI SDK (Gemini 2.5 Flash / 1.5 Flash)."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = f"{SYSTEM_PROMPT}\n\nHere is the CV text to extract:\n\n{cv_text[:20000]}"

    # Use gemini-2.5-flash for high quality and speed on the free tier
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    last_error: Exception | None = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
            raw_text = response.text or ""
            return _parse_json_with_retry(raw_text)
        except Exception as exc:
            last_error = exc
            logger.warning("Gemini model %s failed: %s; trying next", model_name, exc)
            continue

    if last_error:
        raise ValueError(f"Gemini API extraction failed: {last_error}") from last_error

    raise ValueError("Gemini API returned empty response")


def extract_profile_with_anthropic(cv_text: str, api_key: str) -> Dict[str, Any]:
    """Fallback extraction using Anthropic Claude API if configured."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Extract the profile from this CV:\n\n{cv_text[:18000]}",
            }
        ],
    )
    raw_text = message.content[0].text.strip()
    return _parse_json_with_retry(raw_text)


def extract_profile(cv_text: str) -> Dict[str, Any]:
    """Sends cv_text to the configured LLM and returns parsed profile dictionary.

    Priority:
        1. Google Gemini via google-genai
        2. Anthropic Claude (if ANTHROPIC_API_KEY is configured)
        3. Offline Mock extractor if MOCK_LLM=true or in test environment

    Raises:
        ValueError: if LLM fails or no API key is provided and mock is disabled.
    """
    settings = get_settings()

    if settings.mock_llm:
        return _mock_extract_profile(cv_text)

    # 1. Try Google Gemini
    gemini_key = settings.effective_gemini_key
    if gemini_key:
        return extract_profile_with_gemini(cv_text, gemini_key)

    # 2. Try Anthropic fallback
    anthropic_key = settings.effective_anthropic_key
    if anthropic_key:
        return extract_profile_with_anthropic(cv_text, anthropic_key)

    # 3. If no key, check if we should fall back to mock or raise clear error
    raise ValueError(
        "No AI API key found. Please set GOOGLE_API_KEY in backend/.env."
    )
