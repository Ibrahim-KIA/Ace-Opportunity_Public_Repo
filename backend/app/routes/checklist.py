"""Checklist router -- POST /api/checklist.

Generates a tailored preparation checklist for a specific opportunity match,
including required documents, deadline notes, and actionable prep tips.
"""
from __future__ import annotations

import asyncio
import json
import logging
import pathlib
from typing import Any, Dict

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core.db import get_database
from ..core.llm import generate_checklist

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/checklist", tags=["Checklist"])

DATA_PATH = pathlib.Path(__file__).resolve().parents[2] / "data" / "opportunities.json"


class ChecklistRequest(BaseModel):
    profile_id: str | None = None
    opportunity_id: str | None = None
    profile: Dict[str, Any] | None = None
    opportunity: Dict[str, Any] | None = None


async def _get_profile_by_id(profile_id: str) -> Dict[str, Any] | None:
    """Find profile document across ObjectId, id, or profile_id fields."""
    try:
        db = get_database()
    except Exception as exc:
        logger.warning("MongoDB unavailable: %s", exc)
        return None

    if ObjectId.is_valid(profile_id):
        doc = await db["profiles"].find_one({"_id": ObjectId(profile_id)})
        if doc:
            return doc

    doc = await db["profiles"].find_one({"_id": profile_id})
    if doc:
        return doc

    return await db["profiles"].find_one(
        {"$or": [{"profile_id": profile_id}, {"id": profile_id}]}
    )


async def _get_opportunity_by_id(opportunity_id: str) -> Dict[str, Any] | None:
    """Find opportunity by ObjectId, string _id, or title."""
    try:
        db = get_database()
        if ObjectId.is_valid(opportunity_id):
            doc = await db["opportunities"].find_one({"_id": ObjectId(opportunity_id)})
            if doc:
                return doc

        doc = await db["opportunities"].find_one({"_id": opportunity_id})
        if doc:
            return doc

        doc = await db["opportunities"].find_one({"title": opportunity_id})
        if doc:
            return doc
    except Exception as exc:
        logger.warning("Error fetching opportunity from MongoDB: %s", exc)

    # Fallback search in static JSON
    if DATA_PATH.exists():
        with DATA_PATH.open(encoding="utf-8-sig") as fh:
            opps = json.load(fh)
        for opp in opps:
            if str(opp.get("_id", "")) == opportunity_id or opp.get("title") == opportunity_id:
                return opp

    return None


@router.post(
    "",
    summary="Generate tailored preparation checklist for an opportunity match",
    description=(
        "Produces an actionable application checklist specific to a candidate and "
        "opportunity pairing, detailing required documents, deadline timeline guidance, "
        "and concrete preparation tips."
    ),
)
async def create_checklist(req: ChecklistRequest) -> Dict[str, Any]:
    """Generate tailored application checklist."""
    # 1. Resolve Profile
    profile = req.profile
    if not profile:
        if not req.profile_id:
            raise HTTPException(
                status_code=400,
                detail="Either 'profile' object or 'profile_id' must be provided.",
            )
        profile = await _get_profile_by_id(req.profile_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"Candidate profile '{req.profile_id}' not found.",
            )

    # 2. Resolve Opportunity
    opportunity = req.opportunity
    if not opportunity:
        if not req.opportunity_id:
            raise HTTPException(
                status_code=400,
                detail="Either 'opportunity' object or 'opportunity_id' must be provided.",
            )
        opportunity = await _get_opportunity_by_id(req.opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=404,
                detail=f"Opportunity '{req.opportunity_id}' not found.",
            )

    # 3. Generate Checklist with AI / mock fallback
    try:
        checklist_data = await asyncio.to_thread(generate_checklist, profile, opportunity)
    except Exception as exc:
        logger.exception("Checklist generation failed")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to generate checklist: {exc}",
        )

    # Clean embeddings if present in opportunity
    clean_opp = {k: v for k, v in opportunity.items() if k != "embedding"}
    if "_id" in clean_opp:
        clean_opp["_id"] = str(clean_opp["_id"])

    return {
        "opportunity_title": clean_opp.get("title", ""),
        "organization": clean_opp.get("organization", ""),
        "type": clean_opp.get("type", ""),
        "deadline": clean_opp.get("deadline", "rolling"),
        "documents": checklist_data.get("documents", []),
        "deadline_note": checklist_data.get("deadline_note", ""),
        "tips": checklist_data.get("tips", []),
    }
