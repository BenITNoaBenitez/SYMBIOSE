from fastapi import HTTPException, status
from typing import List

ROLE_PERMISSIONS: dict[str, List[str]] = {
    "direction": [
        "chat_agent1", "chat_agent2", "chat_agent3",
        "view_dashboard_global", "view_own_stats",
        "validate_skills", "manage_users", "configure_agents",
        "view_costs_global", "view_own_costs", "view_audit_log",
    ],
    "admin": [
        "chat_agent1", "chat_agent2", "chat_agent3",
        "manage_users", "configure_agents", "view_audit_log",
        "view_costs_global", "validate_skills",
    ],
    "commercial": [
        "chat_agent1", "view_own_stats", "view_own_costs",
    ],
    "bureau_etudes": [
        "chat_agent1", "chat_agent2", "view_own_stats", "view_own_costs",
    ],
    "conducteur": [
        "chat_agent1", "view_own_stats", "view_own_costs",
    ],
    "administratif": [
        "chat_agent1", "view_own_stats", "view_own_costs",
    ],
    "terrain": [
        "chat_agent1",
    ],
}

ROLE_QUOTAS: dict[str, int | None] = {
    "direction":    None,   # Illimité
    "admin":        None,   # Illimité
    "commercial":   200,
    "bureau_etudes": 150,
    "conducteur":   100,
    "administratif": 100,
    "terrain":      50,
}


def has_permission(role: str, feature: str) -> bool:
    return feature in ROLE_PERMISSIONS.get(role, [])


def require_permission(feature: str):
    """Décorateur FastAPI pour vérifier une permission sur un endpoint."""
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if current_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            if not has_permission(current_user.role, feature):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{feature}' requise",
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
