"""Opportunities router -- GET /api/opportunities."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from ..core.db import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get(
    "",
    summary="List all seeded opportunities",
    description=(
        "Returns all opportunities from the MongoDB opportunities collection. "
        "The embedding field is excluded from the response as it is large and "
        "only needed internally for similarity matching."
    ),
)
async def list_opportunities() -> List[Dict[str, Any]]:
    """Fetch all opportunities, excluding the embedding vector."""
    try:
        db = get_database()
        cursor = db["opportunities"].find({}, {"embedding": 0, "_id": 0})
        results = await cursor.to_list(length=None)
        return results
    except Exception as exc:
        logger.exception("Failed to fetch opportunities from MongoDB")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch opportunities: {exc}",
        )
