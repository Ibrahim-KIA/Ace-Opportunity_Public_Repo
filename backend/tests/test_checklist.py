import pytest
from starlette.testclient import TestClient

from app.core.config import get_settings
from app.core.llm import generate_checklist, _mock_generate_checklist
from app.main import app


@pytest.fixture(autouse=True)
def enable_mock_llm(monkeypatch):
    """Enable mock LLM for deterministic offline testing."""
    settings = get_settings()
    monkeypatch.setattr(settings, "mock_llm", True)


def test_mock_generate_checklist_internship():
    profile = {
        "name": "Alex Rivers",
        "skills": ["Python", "FastAPI", "React"],
    }
    opportunity = {
        "title": "Google Summer of Code",
        "organization": "Google",
        "type": "internship",
        "deadline": "2026-04-08",
    }

    res = _mock_generate_checklist(profile, opportunity)
    assert "documents" in res
    assert "deadline_note" in res
    assert "tips" in res
    assert len(res["documents"]) >= 3
    assert len(res["tips"]) >= 2
    assert "2026-04-08" in res["deadline_note"]
    # Check that technical portfolio or github is recommended for internship
    assert any("portfolio" in d.lower() or "github" in d.lower() for d in res["documents"])


def test_mock_generate_checklist_scholarship():
    profile = {
        "name": "Sam Taylor",
        "skills": ["Machine Learning", "Data Analysis"],
    }
    opportunity = {
        "title": "DeepMind Scholarship",
        "organization": "Google DeepMind",
        "type": "scholarship",
        "deadline": "rolling",
    }

    res = _mock_generate_checklist(profile, opportunity)
    assert any("recommendation" in d.lower() for d in res["documents"])
    assert "rolling" in res["deadline_note"].lower()


def test_generate_checklist_function():
    profile = {"name": "Test User", "skills": ["Python"]}
    opp = {"title": "Test Opp", "type": "grant"}
    res = generate_checklist(profile, opp)
    assert isinstance(res, dict)
    assert "documents" in res
    assert "tips" in res


def test_checklist_endpoint_inline_success():
    client = TestClient(app)
    payload = {
        "profile": {
            "name": "Jane Doe",
            "skills": ["TypeScript", "React"],
            "summary": "Full stack engineer",
        },
        "opportunity": {
            "title": "Meta Front End Fellowship",
            "organization": "Meta",
            "type": "internship",
            "deadline": "2026-06-01",
        },
    }

    response = client.post("/api/checklist", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["opportunity_title"] == "Meta Front End Fellowship"
    assert data["organization"] == "Meta"
    assert "documents" in data
    assert len(data["documents"]) > 0
    assert "deadline_note" in data
    assert "tips" in data
    assert len(data["tips"]) > 0


def test_checklist_endpoint_missing_params():
    client = TestClient(app)
    response = client.post("/api/checklist", json={})
    assert response.status_code == 400
    assert "must be provided" in response.json()["detail"].lower()


def test_checklist_endpoint_profile_not_found():
    client = TestClient(app)
    response = client.post(
        "/api/checklist",
        json={"profile_id": "nonexistent_profile_id_9999", "opportunity": {"title": "Test"}},
    )
    assert response.status_code == 404
