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

    # Use latest high-availability Gemini Flash models (ordered by preference)
    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
    ]
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


EXPLAIN_FIT_SYSTEM_PROMPT = """\
You are an expert career advisor and fellowship evaluator.
Given a candidate's structured profile and a specific opportunity (internship, scholarship, or grant), provide a concise 2 to 3 sentence explanation of why this specific candidate is an outstanding fit.

Strict Rules:
- Ground your explanation strictly in the candidate's actual skills, education, projects, or work experiences.
- You MUST explicitly reference by name at least one concrete skill or real experience from the candidate's profile.
- Do NOT use generic filler like "this role aligns well with your background" or "you are a great candidate".
- Directly connect their specific skills or background to the mission, focus, or eligibility of the opportunity.
- Output ONLY the 2-3 sentence explanation text without any markdown formatting, quotation marks, or prefixes.
"""


def _mock_explain_fit(profile: Dict[str, Any], opportunity: Dict[str, Any]) -> str:
    """Generate a realistic, grounded explanation referencing actual profile details."""
    skills = profile.get("skills", [])
    primary_skill = skills[0] if skills else "technical expertise"
    second_skill = skills[1] if len(skills) > 1 else "practical problem solving"
    title = opportunity.get("title", "this program")
    org = opportunity.get("organization", "the host organization")

    # Check for experience
    exp = profile.get("experience", [])
    role_mention = ""
    if exp and isinstance(exp[0], dict) and exp[0].get("role"):
        role_mention = f" Building on your background as a {exp[0]['role']},"

    return (
        f"Your demonstrated capabilities in {primary_skill} and {second_skill} directly align with the core requirements of {title} at {org}.{role_mention} "
        f"your hands-on experience provides the concrete foundation needed to excel and make an immediate impact."
    )


def explain_fit_with_gemini(
    profile: Dict[str, Any], opportunity: Dict[str, Any], api_key: str
) -> str:
    """Generate personalized fit explanation using Google Gemini Flash."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    skills_str = ", ".join(profile.get("skills", [])) or "None listed"
    interests_str = ", ".join(profile.get("interests", [])) or "None listed"
    tags_str = ", ".join(opportunity.get("tags", [])) or "None listed"

    edu_summary = []
    for e in profile.get("education", []):
        if isinstance(e, dict):
            deg = " · ".join(filter(None, [e.get("institution"), e.get("degree"), e.get("field")]))
            if deg:
                edu_summary.append(deg)

    exp_summary = []
    for ex in profile.get("experience", []):
        if isinstance(ex, dict):
            r = ex.get("role", "")
            o = ex.get("organisation") or ex.get("organization") or ""
            d = ex.get("description") or ""
            line = f"{r} at {o}: {d}".strip(" :")
            if line:
                exp_summary.append(line)

    prompt = f"""{EXPLAIN_FIT_SYSTEM_PROMPT}

Candidate Profile:
- Name: {profile.get('name') or 'Candidate'}
- Skills: {skills_str}
- Education: {'; '.join(edu_summary) or 'Not specified'}
- Experience: {'; '.join(exp_summary) or 'Not specified'}
- Interests: {interests_str}
- Summary: {profile.get('summary', '')}

Opportunity:
- Title: {opportunity.get('title', '')}
- Organization: {opportunity.get('organization', '')}
- Type: {opportunity.get('type', '')}
- Eligibility: {opportunity.get('eligibility', '')}
- Description: {opportunity.get('description', '')}
- Focus Tags: {tags_str}

Explanation:"""

    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
    ]
    last_error: Exception | None = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=300,
                ),
            )
            text = (response.text or "").strip()
            # Clean enclosing quotes if LLM added them
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1].strip()
            if text:
                return text
        except Exception as exc:
            last_error = exc
            logger.warning("Gemini model %s failed in explain_fit: %s", model_name, exc)
            continue

    if last_error:
        logger.warning("All Gemini models failed for explain_fit; falling back to mock")
    return _mock_explain_fit(profile, opportunity)


def explain_fit_with_anthropic(
    profile: Dict[str, Any], opportunity: Dict[str, Any], api_key: str
) -> str:
    """Generate personalized fit explanation using Anthropic Claude."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""Candidate Profile:
- Name: {profile.get('name') or 'Candidate'}
- Skills: {', '.join(profile.get('skills', []))}
- Summary: {profile.get('summary', '')}

Opportunity:
- Title: {opportunity.get('title', '')}
- Organization: {opportunity.get('organization', '')}
- Type: {opportunity.get('type', '')}
- Description: {opportunity.get('description', '')}

Explain why this candidate is a great fit in 2-3 sentences, citing specific skills or experiences:"""

    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=400,
            system=EXPLAIN_FIT_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text.strip()
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1].strip()
        return text
    except Exception as exc:
        logger.warning("Anthropic explain_fit failed: %s", exc)
        return _mock_explain_fit(profile, opportunity)


def explain_fit(profile: Dict[str, Any], opportunity: Dict[str, Any]) -> str:
    """Generates a grounded 2-3 sentence rationale for why *profile* fits *opportunity*.

    Mentions specific skills or experiences from *profile*.
    """
    settings = get_settings()

    if settings.mock_llm:
        return _mock_explain_fit(profile, opportunity)

    gemini_key = settings.effective_gemini_key
    if gemini_key:
        try:
            return explain_fit_with_gemini(profile, opportunity, gemini_key)
        except Exception as exc:
            logger.warning("explain_fit_with_gemini raised: %s", exc)

    anthropic_key = settings.effective_anthropic_key
    if anthropic_key:
        try:
            return explain_fit_with_anthropic(profile, opportunity, anthropic_key)
        except Exception as exc:
            logger.warning("explain_fit_with_anthropic raised: %s", exc)

    return _mock_explain_fit(profile, opportunity)


CHECKLIST_SYSTEM_PROMPT = """\
You are an expert career mentor and opportunity application advisor.
Given a candidate's profile and a specific opportunity (internship, scholarship, or grant), generate a structured, actionable preparation checklist.

Return ONLY a valid JSON object matching the exact schema below. Do NOT output any markdown backticks, fences (e.g. ```json), or explanatory text.

{
  "documents": [
    "<Document / Material 1 tailored with specific detail, e.g. 'Updated CV highlighting Python & FastAPI experience'>",
    "<Document / Material 2, e.g. 'Official university transcript or enrollment verification'>",
    "<Document / Material 3, e.g. 'Statement of Purpose addressing how your background aligns with program mission'>"
  ],
  "deadline_note": "<Actionable deadline guidance and submission timeline recommendation>",
  "tips": [
    "<Concrete action tip 1 directly addressing a strength or gap in candidate's profile for this role>",
    "<Concrete action tip 2 regarding portfolio, essays, or code repositories>",
    "<Concrete action tip 3 for interview or review process>"
  ]
}

Strict Rules:
- Output MUST be valid parseable JSON.
- Tailor the items specifically to the requirements of the opportunity and the candidate's actual background.
- Keep tips actionable, concrete, and concise (1-2 sentences each).
- Provide 3 to 5 documents and 2 to 3 concrete tips.
"""


def _mock_generate_checklist(
    profile: Dict[str, Any], opportunity: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate a realistic, tailored preparation checklist for offline or fallback mode."""
    skills = profile.get("skills", [])
    primary_skill = skills[0] if skills else "technical problem solving"
    title = opportunity.get("title", "this program")
    opp_type = (opportunity.get("type") or "internship").lower()
    deadline = opportunity.get("deadline") or "rolling"

    if deadline.lower() == "rolling":
        deadline_text = "Rolling admissions — apply as early as possible before cohort capacity is filled."
    else:
        deadline_text = f"Official deadline is {deadline}. Aim to submit at least 7–10 days early to avoid portal slowdowns."

    docs = [
        f"Tailored CV/Resume highlighting your hands-on background in {primary_skill}",
        "Official or unofficial academic transcript reflecting your coursework",
        f"Statement of Interest / Cover Letter addressing your motivation for {title}",
    ]

    if opp_type in ("scholarship", "grant"):
        docs.append("1–2 letters of academic or professional recommendation")
    else:
        docs.append("Link to technical portfolio, GitHub repository, or live project demonstrations")

    tips = [
        f"Emphasize tangible projects where you applied {primary_skill} to solve a real-world problem.",
        f"Review the eligibility criteria for {title} and clearly articulate how your educational background qualifies you.",
        "Request letters of recommendation or references early, sharing a brief summary of the opportunity with your referees.",
    ]

    return {
        "documents": docs,
        "deadline_note": deadline_text,
        "tips": tips,
    }


def generate_checklist_with_gemini(
    profile: Dict[str, Any], opportunity: Dict[str, Any], api_key: str
) -> Dict[str, Any]:
    """Generate structured application checklist using Google Gemini."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    skills_str = ", ".join(profile.get("skills", [])) or "General STEM / academic background"
    prompt = f"""{CHECKLIST_SYSTEM_PROMPT}

Candidate Profile:
- Name: {profile.get('name') or 'Candidate'}
- Skills: {skills_str}
- Summary: {profile.get('summary', '')}

Opportunity:
- Title: {opportunity.get('title', '')}
- Organization: {opportunity.get('organization', '')}
- Type: {opportunity.get('type', '')}
- Eligibility: {opportunity.get('eligibility', '')}
- Description: {opportunity.get('description', '')}
- Deadline: {opportunity.get('deadline', 'Rolling')}
- Tags: {', '.join(opportunity.get('tags', []))}

Generate the structured JSON checklist:"""

    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash",
    ]
    last_error: Exception | None = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
            raw_text = response.text or ""
            data = _parse_json_with_retry(raw_text)
            if isinstance(data, dict) and "documents" in data and "tips" in data:
                return data
        except Exception as exc:
            last_error = exc
            logger.warning("Gemini model %s failed in generate_checklist: %s", model_name, exc)
            continue

    if last_error:
        logger.warning("All Gemini models failed for generate_checklist; falling back to mock")
    return _mock_generate_checklist(profile, opportunity)


def generate_checklist_with_anthropic(
    profile: Dict[str, Any], opportunity: Dict[str, Any], api_key: str
) -> Dict[str, Any]:
    """Generate structured application checklist using Anthropic Claude."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""Candidate Profile:
- Name: {profile.get('name') or 'Candidate'}
- Skills: {', '.join(profile.get('skills', []))}
- Summary: {profile.get('summary', '')}

Opportunity:
- Title: {opportunity.get('title', '')}
- Organization: {opportunity.get('organization', '')}
- Type: {opportunity.get('type', '')}
- Eligibility: {opportunity.get('eligibility', '')}
- Description: {opportunity.get('description', '')}
- Deadline: {opportunity.get('deadline', 'Rolling')}

Generate structured JSON checklist:"""

    try:
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=600,
            system=CHECKLIST_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = message.content[0].text.strip()
        data = _parse_json_with_retry(raw_text)
        if isinstance(data, dict) and "documents" in data:
            return data
    except Exception as exc:
        logger.warning("Anthropic generate_checklist failed: %s", exc)

    return _mock_generate_checklist(profile, opportunity)


def generate_checklist(
    profile: Dict[str, Any], opportunity: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate tailored checklist of documents, deadline guidance, and prep tips.

    Returns:
        Dict with keys "documents" (list), "deadline_note" (str), and "tips" (list).
    """
    settings = get_settings()

    if settings.mock_llm:
        return _mock_generate_checklist(profile, opportunity)

    gemini_key = settings.effective_gemini_key
    if gemini_key:
        try:
            return generate_checklist_with_gemini(profile, opportunity, gemini_key)
        except Exception as exc:
            logger.warning("generate_checklist_with_gemini raised: %s", exc)

    anthropic_key = settings.effective_anthropic_key
    if anthropic_key:
        try:
            return generate_checklist_with_anthropic(profile, opportunity, anthropic_key)
        except Exception as exc:
            logger.warning("generate_checklist_with_anthropic raised: %s", exc)

    return _mock_generate_checklist(profile, opportunity)
