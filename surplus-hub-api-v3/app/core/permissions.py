ROLE_HIERARCHY = {
    "SUPER_ADMIN": 3,
    "ADMIN": 2,
    "MODERATOR": 1,
}


def check_permission(user_role: str | None, min_role: str) -> bool:
    user_level = ROLE_HIERARCHY.get(user_role or "", 0)
    required_level = ROLE_HIERARCHY.get(min_role, 0)
    return user_level >= required_level
