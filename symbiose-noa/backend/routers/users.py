from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from auth.dependencies import get_current_user
from database.models import User
from database.connection import get_db
from security.rbac import has_permission

router = APIRouter()


class CreateUserRequest(BaseModel):
    email: str
    name: Optional[str] = None
    role: str = "terrain"
    quota_mensuel: Optional[int] = None


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/")
async def list_users(current_user: User = Depends(get_current_user)):
    if not has_permission(current_user.role, "manage_users"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission refusée")
    async with get_db() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(row) for row in rows]


@router.post("/")
async def create_user(
    body: CreateUserRequest,
    current_user: User = Depends(get_current_user),
):
    if not has_permission(current_user.role, "manage_users"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission refusée")
    async with get_db() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO users (email, name, role, quota_mensuel)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            body.email, body.name, body.role, body.quota_mensuel,
        )
        return dict(row)


@router.put("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
):
    if not has_permission(current_user.role, "manage_users"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission refusée")
    async with get_db() as conn:
        await conn.execute("UPDATE users SET actif = false WHERE id = $1", user_id)
    return {"status": "deactivated"}
