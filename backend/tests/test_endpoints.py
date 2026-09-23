import io
import pytest
from starlette.testclient import TestClient
from app.main import app
from app.core.config import get_settings
from docx import Document


@pytest.fixture(autouse=True)
def enable_mock_llm(monkeypatch):
    """Enable mock LLM for deterministic offline testing without external API calls."""
    settings = get_settings()
    monkeypatch.setattr(settings, "mock_llm", True)


def create_docx_bytes(text: str) -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_health_check():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_cv_docx_success():
    client = TestClient(app)
    cv_content = (
        "Sarah Connor\n"
        "Email: sarah.connor@example.com\n"
        "Skills: Python, Machine Learning, Fastapi, React, Git\n"
        "Education: Tech Institute, BSc Robotics, 2024\n"
        "Experience: Cyberdyne Systems, Systems Intern, Jun 2023 - Sep 2023\n"
    )
    docx_bytes = create_docx_bytes(cv_content)

    response = client.post(
        "/api/cv/upload",
        files={"file": ("sarah_connor_cv.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    assert response.status_code == 200
    data = response.json()

    assert "profile_id" in data
    assert data["profile_id"] is not None
    assert "name" in data
    assert "skills" in data
    assert len(data["skills"]) > 0
    assert "education" in data
    assert "experience" in data
    assert "raw_text" in data
    assert "sarah_connor_cv" in data["raw_text"] or "Sarah Connor" in data["raw_text"]
    assert "profile" in data
    assert data["profile"]["name"] == data["name"]


def test_parse_cv_alias_endpoint():
    client = TestClient(app)
    cv_content = "John Doe\nEmail: john@doe.com\nSkills: Python, SQL"
    docx_bytes = create_docx_bytes(cv_content)

    response = client.post(
        "/api/cv/parse",
        files={"file": ("john_doe.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    assert response.status_code == 200
    data = response.json()
    assert "profile_id" in data
    assert "skills" in data


def test_upload_unsupported_file_type():
    client = TestClient(app)
    response = client.post(
        "/api/cv/upload",
        files={"file": ("resume.txt", b"plain text content", "text/plain")},
    )
    assert response.status_code == 422
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_oversized_file():
    client = TestClient(app)
    # File larger than 5 MB
    large_bytes = b"0" * (5 * 1024 * 1024 + 1024)
    response = client.post(
        "/api/cv/upload",
        files={"file": ("huge_resume.pdf", large_bytes, "application/pdf")},
    )
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]
