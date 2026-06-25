from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timezone
from database.connection import get_db
from auth.jwt_handler import create_access_token
from security.audit import log_action

router = APIRouter()


class GoogleAuthRequest(BaseModel):
    email: str
    name: str
    google_id: str


@router.post("/google")
async def auth_google(body: GoogleAuthRequest):
    async with get_db() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1 AND actif = true",
            body.email,
        )
        if row is None:
            await log_action(
                action="login",
                success=False,
                error_message=f"Tentative d'accès compte non enregistré : {body.email}",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé — compte non enregistré",
            )

        await conn.execute(
            "UPDATE users SET last_login = $1 WHERE id = $2",
            datetime.now(timezone.utc),
            row["id"],
        )

    await log_action(action="login", user_id=str(row["id"]))

    token = create_access_token({"sub": str(row["id"]), "role": row["role"]})
    return {"access_token": token, "token_type": "bearer", "role": row["role"]}
