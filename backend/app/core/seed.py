"""Seed script -- populates the MongoDB opportunities collection.

Usage (from the backend/ directory with the venv active):

    python -m app.core.seed

This is idempotent: re-running performs upserts keyed on title, so
documents are updated rather than duplicated.
"""
from __future__ import annotations

import asyncio
import json
import logging
import pathlib
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# Path to the opportunities dataset: backend/data/opportunities.json
# seed.py is at backend/app/core/seed.py → parents[2] = backend/
DATA_PATH = pathlib.Path(__file__).resolve().parents[2] / "data" / "opportunities.json"


async def seed() -> None:
    """Read opportunities JSON, embed each entry, upsert into MongoDB."""
    # Import here to avoid loading everything at the top level
    from .db import get_database
    from .embeddings import embed_text

    if not DATA_PATH.exists():
        logger.error("Dataset not found at %s", DATA_PATH)
        sys.exit(1)

    with DATA_PATH.open(encoding="utf-8-sig") as fh:
        opportunities = json.load(fh)

    logger.info("Loaded %d opportunities from %s", len(opportunities), DATA_PATH)

    db = get_database()
    collection = db["opportunities"]

    upserted = 0
    for opp in opportunities:
        # Build a single text blob for embedding
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

        result = await collection.update_one(
            {"title": opp["title"]},
            {"$set": opp},
            upsert=True,
        )
        action = "upserted" if result.upserted_id else "updated"
        logger.info("  %s  '%s'", action, opp["title"])
        upserted += 1

    logger.info("Done. %d/%d opportunities seeded.", upserted, len(opportunities))


if __name__ == "__main__":
    asyncio.run(seed())
