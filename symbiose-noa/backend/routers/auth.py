import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import httpx
from database.connection import get_db
from auth.jwt_handler import create_access_token
from security.audit import log_action
from config import settings

router = APIRouter()

MAGIC_LINK_EXPIRE_MINUTES = 15


class MagicLinkRequest(BaseModel):
    email: str


class VerifyTokenRequest(BaseModel):
    token: str
    email: str


async def _send_magic_link_email(to_email: str, magic_link: str) -> None:
    """Envoie le lien de connexion via l'API Resend."""
    if settings.debug:
        # En développement, afficher le lien dans les logs plutôt que l'envoyer
        print(f"\n🔗 MAGIC LINK (dev) → {magic_link}\n")
        return

    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": settings.resend_from_email,
                "to": to_email,
                "subject": "Votre lien de connexion NOA",
                "html": f"""
                <div style="font-family:system-ui,sans-serif;max-width:480px;margin:0 auto;padding:40px 24px">
                  <p style="font-size:28px;margin:0 0 8px">🌿</p>
                  <h1 style="font-size:20px;font-weight:600;margin:0 0 8px">NOA — Symbiose Paysage</h1>
                  <p style="color:#555;margin:0 0 32px">Cliquez sur le bouton ci-dessous pour vous connecter :</p>
                  <a href="{magic_link}"
                     style="display:inline-block;background:#1D9E75;color:white;padding:12px 28px;
                            border-radius:8px;text-decoration:none;font-weight:500;font-size:14px">
                    Se connecter à NOA
                  </a>
                  <p style="color:#aaa;font-size:12px;margin:32px 0 0">
                    Ce lien est valable {MAGIC_LINK_EXPIRE_MINUTES} minutes.<br>
                    Si vous n'avez pas demandé cette connexion, ignorez cet email.
                  </p>
                </div>
                """,
            },
            timeout=10.0,
        )
        res.raise_for_status()


@router.post("/magic-link/request")
async def request_magic_link(body: MagicLinkRequest):
    """
    Génère un token et envoie un lien de connexion par email.
    Retourne toujours le même message pour ne pas révéler si l'email existe.
    """
    async with get_db() as conn:
        user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1 AND actif = true",
            body.email,
        )

    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=MAGIC_LINK_EXPIRE_MINUTES)

        async with get_db() as conn:
            await conn.execute(
                "INSERT INTO verification_tokens (email, token, expires_at) VALUES ($1, $2, $3)",
                body.email, token, expires_at,
            )

        magic_link = f"{settings.app_url}/auth/verify?token={token}&email={body.email}"
        await _send_magic_link_email(body.email, magic_link)
    else:
        await log_action(
            action="login",
            success=False,
            error_message=f"Magic link demandé pour email non enregistré : {body.email}",
        )

    return {"message": "Si cet email est enregistré, vous recevrez un lien de connexion."}


@router.post("/magic-link/verify")
async def verify_magic_link(body: VerifyTokenRequest):
    """Vérifie le token, le consomme et retourne un JWT backend."""
    async with get_db() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM verification_tokens WHERE token = $1 AND email = $2",
            body.token, body.email,
        )

    if not row:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien invalide")
    if row["used"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien déjà utilisé")
    if row["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lien expiré")

    async with get_db() as conn:
        await conn.execute(
            "UPDATE verification_tokens SET used = true WHERE token = $1",
            body.token,
        )
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1 AND actif = true",
            body.email,
        )

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")

    async with get_db() as conn:
        await conn.execute(
            "UPDATE users SET last_login = $1 WHERE id = $2",
            datetime.now(timezone.utc), user["id"],
        )

    await log_action(action="login", user_id=str(user["id"]))

    access_token = create_access_token({"sub": str(user["id"]), "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}
