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

def build_user_profile_from_args(args:Namespace) -> UserProfile:
    profile = DEFAULT_USER_PROFILE.copy()

    if args.lang:
        profile["preferred_languages"] = [lang.lower() for lang in args.lang]

    if args.domain:
        profile["preferred_domains"] = [domain.lower() for domain in args.domain]

    if args.global_flag:
        profile["prefer_global"] = True

    if args.exp:
        profile["experience_level"] = args.exp.lower()

    if args.mode:
        profile["priority_mode"] = args.mode.lower()

    if args.loc:
        profile["preferred_locations"] = [loc.lower for loc in args.loc]

    if args.remote:
        profile["allow_remote"] = True

    return profile