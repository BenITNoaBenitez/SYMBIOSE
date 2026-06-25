import time
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel
from auth.dependencies import get_current_user
from database.models import User
from database.connection import get_db
from security.rbac import has_permission
from security.audit import log_action

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None
    has_attachment: bool = False
    attachment_type: Optional[str] = None


@router.post("/")
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    if not has_permission(current_user.role, "chat_agent1"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission refusée")

    start = time.monotonic()
    thread_id = body.thread_id or str(uuid.uuid4())

    # TODO: Initialiser le checkpointer LangGraph et invoquer le graph principal
    # from agents.router import build_main_graph
    # from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    # checkpointer = AsyncPostgresSaver(...)
    # graph = await build_main_graph(checkpointer)
    # result = await graph.ainvoke({...})

    duration_ms = int((time.monotonic() - start) * 1000)
    await log_action(
        action="chat_request",
        user_id=str(current_user.id),
        agent_id="agent1",
        success=True,
        duration_ms=duration_ms,
    )

    return {
        "thread_id": thread_id,
        "response": "NOA infrastructure en place — logique métier à implémenter",
        "agent_used": "agent1",
    }


@router.get("/threads")
async def list_threads(current_user: User = Depends(get_current_user)):
    async with get_db() as conn:
        await conn.execute("SELECT set_config('app.current_user_id', $1, true)", str(current_user.id))
        await conn.execute("SELECT set_config('app.current_role', $1, true)", current_user.role)
        rows = await conn.fetch(
            "SELECT * FROM threads WHERE user_id = $1 ORDER BY updated_at DESC",
            current_user.id,
        )
        return [dict(row) for row in rows]


@router.websocket("/ws/{thread_id}")
async def chat_ws(websocket: WebSocket, thread_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # TODO: Intégrer LangGraph streaming via websocket
            await websocket.send_json({"type": "message", "content": f"echo: {data}", "thread_id": thread_id})
    except WebSocketDisconnect:
        pass
