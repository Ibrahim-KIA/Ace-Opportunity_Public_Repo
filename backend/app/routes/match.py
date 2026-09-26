"""Match router -- GET /api/match/{profile_id}.

Calculates semantic vector similarity between candidate profile and curated
opportunities, ranking top matches with grounded AI fit explanations.
"""
from __future__ import annotations

import asyncio
import json
import logging
import pathlib
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from ..core.db import get_database
from ..core.embeddings import embed_text
from ..core.llm import explain_fit
from ..core.matching import rank_opportunities

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/match", tags=["Matching"])

DATA_PATH = pathlib.Path(__file__).resolve().parents[2] / "data" / "opportunities.json"


def _build_profile_text(profile: Dict[str, Any]) -> str:
    """Compose semantic text blob from structured profile fields."""
    skills = " ".join(profile.get("skills", []))
    interests = " ".join(profile.get("interests", []))
    summary = profile.get("summary", "")

    edu_parts = []
    for edu in profile.get("education", []):
        if isinstance(edu, dict):
            parts = [
                edu.get("institution", ""),
                edu.get("degree") or "",
                edu.get("field") or "",
            ]
            edu_parts.append(" ".join(filter(None, parts)))
    education_text = " ".join(edu_parts)

    exp_parts = []
    for exp in profile.get("experience", []):
        if isinstance(exp, dict):
            parts = [
                exp.get("role", ""),
                exp.get("organisation") or exp.get("organization") or "",
                exp.get("description") or "",
            ]
            exp_parts.append(" ".join(filter(None, parts)))
    experience_text = " ".join(exp_parts)

    combined = " ".join(
        filter(None, [skills, interests, education_text, experience_text, summary])
    ).strip()

    if not combined:
        combined = profile.get("raw_text", "").strip()

    return combined


async def _get_profile_by_id(profile_id: str) -> Dict[str, Any] | None:
    """Find profile document across ObjectId, id, or profile_id fields."""
    try:
        db = get_database()
    except Exception as exc:
        logger.warning("MongoDB client unavailable: %s", exc)
        return None

    # 1. Try ObjectId lookup
    if ObjectId.is_valid(profile_id):
        doc = await db["profiles"].find_one({"_id": ObjectId(profile_id)})
        if doc:
            return doc

    # 2. Try string _id lookup
    doc = await db["profiles"].find_one({"_id": profile_id})
    if doc:
        return doc

    # 3. Try profile_id or id field lookup
    doc = await db["profiles"].find_one(
        {"$or": [{"profile_id": profile_id}, {"id": profile_id}]}
    )
    return doc


async def _load_opportunities() -> List[Dict[str, Any]]:
    """Load opportunities with embeddings from MongoDB or fallback JSON."""
    opportunities: List[Dict[str, Any]] = []

    try:
        db = get_database()
        cursor = db["opportunities"].find({})
        opportunities = await cursor.to_list(length=None)
    except Exception as exc:
        logger.warning("Failed to fetch opportunities from MongoDB (%s); checking local file", exc)

    if not opportunities and DATA_PATH.exists():
        logger.info("Loading opportunities from static dataset %s", DATA_PATH)
        with DATA_PATH.open(encoding="utf-8-sig") as fh:
            raw_opps = json.load(fh)
        # Generate embeddings if missing
        for opp in raw_opps:
            if "embedding" not in opp:
                blob = " ".join(
                    [
                        opp.get("title", ""),
                        opp.get("organization", ""),
                        opp.get("description", ""),
                        opp.get("eligibility", ""),
                        " ".join(opp.get("tags", [])),
                    ]
                )
                opp["embedding"] = embed_text(blob)
            opportunities.append(opp)

    return opportunities


@router.get(
    "/{profile_id}",
    summary="Get top ranked opportunity matches with grounded AI fit explanations",
    description=(
        "Retrieves a candidate's profile, calculates its dense vector embedding, "
        "ranks all opportunities using cosine similarity, generates grounded "
        "AI explanations for why the candidate fits the top 5 opportunities, "
        "and returns the ranked matches."
    ),
)
async def get_matches(profile_id: str) -> List[Dict[str, Any]]:
    """Calculate and return top 5 ranked opportunity matches with fit rationales."""
    # 1. Retrieve profile
    profile = await _get_profile_by_id(profile_id)
    if not profile:
        logger.warning("Profile not found: %s", profile_id)
        raise HTTPException(
            status_code=404,
            detail=f"Candidate profile '{profile_id}' not found.",
        )

    # 2. Embed candidate profile
    profile_text = _build_profile_text(profile)
    if not profile_text:
        profile_text = "Candidate seeking scholarships, internships, and opportunities."

    try:
        profile_embedding = embed_text(profile_text)
    except Exception as exc:
        logger.exception("Failed to generate embedding for candidate profile")
        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation failed: {exc}",
        )

    # 3. Load opportunities with embeddings
    opportunities = await _load_opportunities()
    if not opportunities:
        logger.warning("No opportunities found in database or local dataset")
        return []

    # 4. Rank top 5 opportunities using cosine similarity
    ranked = rank_opportunities(profile_embedding, opportunities, top_n=5)

    # 5. Generate personalized fit explanations concurrently
    async def _explain_single(item: Dict[str, Any]) -> Dict[str, Any]:
        opp = item["opportunity"]
        try:
            why_you_fit = await asyncio.to_thread(explain_fit, profile, opp)
        except Exception as exc:
            logger.warning("Failed generating explanation for %s: %s", opp.get("title"), exc)
            why_you_fit = (
                f"Your skills and background make you a strong candidate for {opp.get('title', 'this program')} "
                f"at {opp.get('organization', 'the organization')}."
            )

        return {
            "opportunity": opp,
            "score": item["score"],
            "why_you_fit": why_you_fit,
        }

    results = await asyncio.gather(*[_explain_single(item) for item in ranked])
    return list(results)
