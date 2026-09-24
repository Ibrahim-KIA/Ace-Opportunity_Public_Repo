"""Embeddings module using sentence-transformers (all-MiniLM-L6-v2).

The model is loaded once at module level so it is ready for the first request
without a cold-start penalty on every call.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import List

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model():
    """Load and cache the SentenceTransformer model (called lazily on first use)."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore

        logger.info("Loading sentence-transformers model: %s", MODEL_NAME)
        model = SentenceTransformer(MODEL_NAME)
        logger.info("Model loaded successfully.")
        return model
    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers is not installed. "
            "Run: pip install sentence-transformers"
        ) from exc


def embed_text(text: str) -> List[float]:
    """Return the embedding for *text* as a plain Python list of floats.

    The output is JSON-serialisable and Mongo-serialisable.
    """
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()
