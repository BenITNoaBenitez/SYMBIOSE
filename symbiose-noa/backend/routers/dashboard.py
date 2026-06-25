from fastapi import APIRouter, Depends, HTTPException, status
from auth.dependencies import get_current_user
from database.models import User
from database.connection import get_db
from security.rbac import has_permission

router = APIRouter()


@router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    async with get_db() as conn:
        thread_count = await conn.fetchval(
            "SELECT COUNT(*) FROM threads WHERE user_id = $1",
            current_user.id,
        )
        usage_today = await conn.fetchrow(
            "SELECT request_count, tokens_total, cost_eur FROM api_usage_daily "
            "WHERE user_id = $1 AND date = CURRENT_DATE",
            current_user.id,
        )
    return {
        "threads": thread_count,
        "today": dict(usage_today) if usage_today else {
            "request_count": 0,
            "tokens_total": 0,
            "cost_eur": 0,
        },
        "quota_mensuel": current_user.quota_mensuel,
    }


@router.get("/global")
async def get_global_stats(current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role, "view_dashboard_global"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission refusée")
    async with get_db() as conn:
        rows = await conn.fetch("""
            SELECT u.role,
                   COUNT(DISTINCT u.id) AS user_count,
                   COALESCE(SUM(d.request_count), 0) AS total_requests,
                   COALESCE(SUM(d.cost_eur), 0) AS total_cost
            FROM users u
            LEFT JOIN api_usage_daily d ON d.user_id = u.id AND d.date = CURRENT_DATE
            GROUP BY u.role
            ORDER BY u.role
        """)
    return [dict(row) for row in rows]


@router.get("/activity")
async def get_activity(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
):
    if not has_permission(current_user.role, "view_audit_log"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission refusée")
    async with get_db() as conn:
        rows = await conn.fetch(
            "SELECT id, user_id, action, agent_id, success, created_at "
            "FROM audit_log ORDER BY created_at DESC LIMIT $1",
            limit,
        )
    return [dict(row) for row in rows]
