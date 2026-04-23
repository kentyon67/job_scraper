from argparse import Namespace
from typing import TypedDict



class UserProfile(TypedDict):
    preferred_languages: list[str]
    preferred_domains: list[str]
    prefer_global: bool
    experience_level: str
    priority_mode: str
    preferred_locations: list[str]
    allow_remote: bool


DEFAULT_USER_PROFILE: UserProfile = {
    "preferred_languages": ["Python"],
    "preferred_domains": ["Backend", "Data"],
    "prefer_global": False,
    "experience_level": "Beginner",
    "priority_mode": "Growth",
    "preferred_locations": ["Tokyo"],
    "allow_remote": False,
}

def build_user_profile_from_args(args) -> UserProfile:
    profile = DEFAULT_USER_PROFILE.copy()

    lang = getattr(args, "lang", None)
    domain = getattr(args, "domain", None)
    global_flag = getattr(args, "global_flag", False)
    exp = getattr(args, "exp", None)
    mode_profile = getattr(args, "mode_profile", None)
    mode = getattr(args, "mode", None)
    loc = getattr(args, "loc", None)
    remote = getattr(args, "remote", False)

    if lang:
      profile["preferred_languages"] = [str(x).lower() for x in lang]

    if domain:
        profile["preferred_domains"] = [str(x).lower() for x in domain]

    if global_flag:
        profile["prefer_global"] = True

    if exp:
        profile["experience_level"] = str(exp).lower()

    if mode_profile:
        profile["priority_mode"] = str(mode_profile).lower()
    elif mode and mode not in {"full", "analysis"}:
        profile["priority_mode"] = str(mode).lower()

    if loc:
        profile["preferred_locations"] = [str(x).lower() for x in loc]

    if remote:
        profile["allow_remote"] = True

    return profile