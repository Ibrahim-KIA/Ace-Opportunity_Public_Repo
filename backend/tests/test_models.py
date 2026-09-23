import pytest
from app.models.profile import Profile, EducationEntry, ExperienceEntry
from app.schemas.cv import CVProfile


def test_education_entry_normalization():
    # start_year + end_year normalization to year
    entry = EducationEntry(
        institution="Stanford University",
        degree="BSc",
        field="Computer Science",
        start_year="2018",
        end_year="2022",
    )
    assert entry.year == "2018–2022"

    # year fallback
    entry2 = EducationEntry(
        institution="MIT",
        degree="MSc",
        field="AI",
        year="2024",
    )
    assert entry2.end_year == "2024"


def test_experience_entry_normalization():
    # organisation vs organization synchronization
    entry = ExperienceEntry(
        organisation="Google",
        role="Software Engineer Intern",
        start_date="Jun 2023",
        end_date="Sep 2023",
        description="Built internal tools",
    )
    assert entry.organization == "Google"
    assert entry.duration == "Jun 2023 – Sep 2023"

    entry2 = ExperienceEntry(
        organization="Microsoft",
        role="Product Manager",
        duration="2021 - 2023",
    )
    assert entry2.organisation == "Microsoft"


def test_profile_schema_completeness():
    profile = Profile(
        name="Alex Smith",
        email="alex@example.com",
        skills=["Python", "FastAPI", "React"],
        education=[
            EducationEntry(
                institution="Oxford",
                degree="BA",
                field="Physics",
                year="2023",
            )
        ],
        experience=[
            ExperienceEntry(
                organisation="DeepMind",
                role="Research Intern",
                duration="2023",
                description="Researched LLM agents",
            )
        ],
        interests=["Autonomous Agents", "Robotics"],
        summary="Passionate AI and systems engineer.",
        raw_text="Alex Smith CV ...",
    )

    data = profile.model_dump()
    assert data["name"] == "Alex Smith"
    assert data["email"] == "alex@example.com"
    assert "FastAPI" in data["skills"]
    assert len(data["education"]) == 1
    assert len(data["experience"]) == 1
    assert data["raw_text"] == "Alex Smith CV ..."

    # CVProfile is alias
    assert CVProfile == Profile
