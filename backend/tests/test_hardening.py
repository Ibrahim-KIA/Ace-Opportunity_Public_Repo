"""Hardening test suite for edge cases, sparse CVs, and diverse candidate profiles."""
import pytest
from starlette.testclient import TestClient

from app.core.config import get_settings
from app.core.llm import extract_profile, explain_fit, generate_checklist
from app.core.matching import rank_opportunities
from app.models.profile import Profile
from app.main import app


@pytest.fixture(autouse=True)
def enable_mock_llm(monkeypatch):
    """Enable mock LLM for offline deterministic edge case validation."""
    settings = get_settings()
    monkeypatch.setattr(settings, "mock_llm", True)


def test_sparse_cv_minimal_text():
    """Verify that a minimal 1-line CV extracts safely without crashing."""
    raw_text = "Taylor Swift\nMusician and songwriter exploring arts grants."
    profile_data = extract_profile(raw_text)
    profile = Profile.model_validate(profile_data)

    assert profile.name is not None
    assert isinstance(profile.skills, list)
    assert len(profile.skills) > 0
    assert isinstance(profile.education, list)
    assert isinstance(profile.experience, list)


def test_cv_with_no_experience():
    """Verify candidate with only education and no job experience."""
    profile_dict = {
        "name": "First Year Student",
        "email": "student@college.edu",
        "skills": ["Python", "Mathematics"],
        "education": [
            {
                "institution": "City College",
                "degree": "BSc",
                "field": "Data Science",
                "year": "2026",
            }
        ],
        "experience": [],
        "interests": ["Machine Learning"],
        "summary": "First year student eager for early internship opportunities.",
    }

    opp = {
        "title": "Microsoft Explore Internship",
        "organization": "Microsoft",
        "type": "internship",
        "deadline": "rolling",
    }

    # Verify explain_fit doesn't crash on empty experience
    explanation = explain_fit(profile_dict, opp)
    assert isinstance(explanation, str)
    assert len(explanation) > 10

    # Verify checklist generation works without experience
    checklist = generate_checklist(profile_dict, opp)
    assert isinstance(checklist, dict)
    assert len(checklist.get("documents", [])) > 0
    assert len(checklist.get("tips", [])) > 0


def test_cv_with_no_education():
    """Verify candidate with industry experience but no formal degree listed."""
    profile_dict = {
        "name": "Self Taught Builder",
        "email": "builder@open.source",
        "skills": ["Rust", "Distributed Systems", "Git"],
        "education": [],
        "experience": [
            {
                "role": "Open Source Maintainer",
                "organisation": "OSS Project",
                "description": "Maintained high-throughput data tools.",
            }
        ],
        "interests": ["Open Source"],
        "summary": "Self-taught developer building open source tooling.",
    }

    opp = {
        "title": "Google Summer of Code",
        "organization": "Google",
        "type": "internship",
        "deadline": "2026-04-08",
    }

    explanation = explain_fit(profile_dict, opp)
    assert "Rust" in explanation or "technical" in explanation.lower()

    checklist = generate_checklist(profile_dict, opp)
    assert "documents" in checklist


def test_humanities_business_profile_matching():
    """Verify non-STEM humanities or business candidate."""
    profile_dict = {
        "name": "Jordan Bell",
        "email": "jordan@business.edu",
        "skills": ["Financial Modeling", "Communication", "Leadership", "Market Research"],
        "education": [
            {
                "institution": "London School of Economics",
                "degree": "BSc",
                "field": "Economics & Management",
                "year": "2025",
            }
        ],
        "experience": [
            {
                "role": "Consulting Analyst Intern",
                "organisation": "Strategy Partners",
                "description": "Conducted market diligence.",
            }
        ],
        "interests": ["Social Enterprise", "Venture Grants"],
        "summary": "Economics undergraduate interested in impact enterprise and leadership fellowships.",
    }

    opps = [
        {
            "title": "Global Leaders Fellowship",
            "type": "scholarship",
            "embedding": [0.8, 0.2, 0.1],
        },
        {
            "title": "Kernel Systems Internship",
            "type": "internship",
            "embedding": [0.05, 0.95, 0.1],
        },
    ]

    # Candidate vector aligned with first opp
    candidate_vec = [0.85, 0.15, 0.1]
    ranked = rank_opportunities(candidate_vec, opps, top_n=2)

    assert ranked[0]["opportunity"]["title"] == "Global Leaders Fellowship"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_checklist_endpoint_with_sparse_payload():
    """Verify checklist endpoint handles minimal profile payload gracefully."""
    client = TestClient(app)
    response = client.post(
        "/api/checklist",
        json={
            "profile": {
                "name": "Sparse User",
                "skills": [],
            },
            "opportunity": {
                "title": "Open Grant Initiative",
                "type": "grant",
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert len(data["documents"]) > 0
    assert "tips" in data
