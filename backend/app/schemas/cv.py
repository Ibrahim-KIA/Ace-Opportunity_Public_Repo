from __future__ import annotations

from ..models.profile import EducationEntry, ExperienceEntry, Profile

# CVProfile is an alias to Profile for backward compatibility
CVProfile = Profile

__all__ = ["CVProfile", "EducationEntry", "ExperienceEntry", "Profile"]
