import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_settings

_client: AsyncIOMotorClient | None = None


def _get_client() -> AsyncIOMotorClient:
    global _client
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError(
            "MONGODB_URI is not configured. Set it in your .env file or environment."
        )

    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _client is not None:
        try:
            client_loop = _client.get_io_loop()
            if client_loop.is_closed() or (current_loop and client_loop != current_loop):
                _client = None
        except Exception:
            _client = None

    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """Return the 'ace_opportunity' database handle."""
    return _get_client()["ace_opportunity"]
