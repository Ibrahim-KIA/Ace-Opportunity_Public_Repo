import pytest
from starlette.testclient import TestClient

from app.core.config import get_settings
from app.core.matching import cosine_similarity, rank_opportunities
from app.core.llm import explain_fit
from app.main import app


@pytest.fixture(autouse=True)
def enable_mock_llm(monkeypatch):
    """Enable mock LLM for deterministic offline testing."""
    settings = get_settings()
    monkeypatch.setattr(settings, "mock_llm", True)


def test_cosine_similarity_identical():
    v = [1.0, 2.0, 3.0]
    sim = cosine_similarity(v, v)
    assert round(sim, 5) == 1.0


def test_cosine_similarity_orthogonal():
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0]
    sim = cosine_similarity(v1, v2)
    assert sim == 0.0


def test_cosine_similarity_zero_vector():
    v1 = [0.0, 0.0]
    v2 = [1.0, 2.0]
    sim = cosine_similarity(v1, v2)
    assert sim == 0.0


def test_cosine_similarity_empty():
    assert cosine_similarity([], []) == 0.0
    assert cosine_similarity([1.0], [1.0, 2.0]) == 0.0


def test_rank_opportunities_ordering_and_projection():
    profile_vec = [1.0, 0.0, 0.0]
    opps = [
        {
            "title": "Low Match Opp",
            "type": "internship",
            "embedding": [0.1, 0.9, 0.0],
        },
        {
            "title": "High Match Opp",
            "type": "scholarship",
            "embedding": [0.95, 0.05, 0.0],
        },
        {
            "title": "Medium Match Opp",
            "type": "grant",
            "embedding": [0.6, 0.4, 0.0],
        },
    ]

    ranked = rank_opportunities(profile_vec, opps, top_n=2)

    assert len(ranked) == 2
    assert ranked[0]["opportunity"]["title"] == "High Match Opp"
    assert ranked[0]["score"] > ranked[1]["score"]
    assert "embedding" not in ranked[0]["opportunity"]
    assert "embedding" not in ranked[1]["opportunity"]


def test_explain_fit_mock():
    profile = {
        "name": "Jane Developer",
        "skills": ["Python", "FastAPI", "React"],
        "experience": [{"role": "Software Engineering Intern", "organisation": "TechCorp"}],
    }
    opportunity = {
        "title": "Google Summer of Code",
        "organization": "Google",
        "type": "internship",
    }

    explanation = explain_fit(profile, opportunity)
    assert isinstance(explanation, str)
    assert len(explanation) > 20
    assert "Python" in explanation
    assert "Google Summer of Code" in explanation


def test_match_endpoint_not_found():
    client = TestClient(app)
    response = client.get("/api/match/nonexistent_profile_id_12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
