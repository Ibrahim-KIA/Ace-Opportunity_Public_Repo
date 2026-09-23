from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class EducationEntry(BaseModel):
    institution: str
    degree: str | None = None
    field: str | None = None
    start_year: str | None = None
    end_year: str | None = None
    year: str | None = None

    def model_post_init(self, __context: Any) -> None:
        if not self.year and (self.start_year or self.end_year):
            parts = [p for p in (self.start_year, self.end_year) if p]
            self.year = "–".join(parts)
        elif self.year and not self.start_year and not self.end_year:
            self.end_year = self.year


class ExperienceEntry(BaseModel):
    organisation: str | None = None
    organization: str | None = None
    role: str
    start_date: str | None = None
    end_date: str | None = None
    duration: str | None = None
    description: str | None = None

    def model_post_init(self, __context: Any) -> None:
        # Normalize organisation / organization
        if self.organisation and not self.organization:
            self.organization = self.organisation
        elif self.organization and not self.organisation:
            self.organisation = self.organization

        # Normalize duration / dates
        if not self.duration and (self.start_date or self.end_date):
            parts = [p for p in (self.start_date, self.end_date) if p]
            self.duration = " – ".join(parts)
        elif self.duration and not self.start_date and not self.end_date:
            self.end_date = self.duration


class Profile(BaseModel):
    id: str | None = None
    profile_id: str | None = None
    name: str | None = None
    email: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    summary: str = ""
    raw_text: str = ""
