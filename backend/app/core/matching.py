"""Semantic matching module for Ace-Opportunity.

Computes cosine similarity between profile vector embeddings and opportunity
vector embeddings, ranking the best matching opportunities.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate the cosine similarity between two float vectors.

    Returns a float in [-1.0, 1.0]. If either vector is empty or all-zero, returns 0.0.
    """
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


def rank_opportunities(
    profile_embedding: List[float],
    opportunities: List[Dict[str, Any]],
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """Rank opportunities by cosine similarity against *profile_embedding*.

    Parameters
    ----------
    profile_embedding:
        Dense vector representation of candidate profile (e.g. 384 floats).
    opportunities:
        List of opportunity dictionaries, each containing an 'embedding' field.
    top_n:
        Maximum number of ranked results to return (default 5).

    Returns
    -------
    List of dictionary items:
        [
            {
                "opportunity": { ...clean opportunity dict without raw embedding... },
                "score": 0.85
            },
            ...
        ]
    sorted descending by similarity score.
    """
    scored: List[Dict[str, Any]] = []

    for opp in opportunities:
        opp_embedding = opp.get("embedding")
        if not opp_embedding or not isinstance(opp_embedding, list):
            continue

        sim = cosine_similarity(profile_embedding, opp_embedding)
        # Normalize and clamp similarity to [0.0, 1.0], rounded to 2 decimal places
        score = round(max(0.0, min(1.0, float(sim))), 2)

        # Clone opportunity dictionary without the large internal embedding
        clean_opp = {k: v for k, v in opp.items() if k != "embedding"}
        if "_id" in clean_opp:
            clean_opp["_id"] = str(clean_opp["_id"])

        scored.append(
            {
                "opportunity": clean_opp,
                "score": score,
            }
        )

    # Sort descending by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]
