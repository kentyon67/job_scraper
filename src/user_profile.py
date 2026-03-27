from typing import TypedDict, List


class UserProfile(TypedDict):
    preferred_languages: List[str]
    preferred_domains: List[str]
    prefer_global: bool
    experience_level: str
    priority_mode: str

    preferred_locations: List[str]
    allow_remote: bool


DEFAULT_USER_PROFILE: UserProfile = {
    "preferred_languages": ["Python"],
    "preferred_domains": ["Backend", "Data"],
    "prefer_global": True,
    "experience_level": "Beginner",
    "priority_mode": "Growth",

    "preferred_locations": ["Tokyo"],
    "allow_remote": True,
}