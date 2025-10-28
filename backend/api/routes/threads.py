"""
Thread management routes for the Comment Widget API.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional

from ..models import ThreadCreate
from ..dependencies import nocodebackend_request

router = APIRouter()


@router.post("/")
async def create_thread(thread: ThreadCreate, user_id: Optional[int] = None) -> Dict[str, Any]:
    """Cria nova thread (opcionalmente autenticado)"""
    data = {
        "usuario_proprietario_id": user_id or 1,  # Default to user 1 if not provided
        "external_page_id": thread.external_page_id,
        "url": thread.url,
        "title": thread.title
    }

    result = await nocodebackend_request("POST", "create/threads", data)
    return result


@router.get("/")
async def list_threads(user_id: Optional[int] = None, page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """Lista threads (opcionalmente filtra por usuário)"""
    params = {"page": page, "limit": limit}
    if user_id:
        params["usuario_proprietario_id"] = user_id

    result = await nocodebackend_request("GET", "read/threads", params=params)
    return result


@router.get("/{thread_id}")
async def get_thread(thread_id: int) -> Dict[str, Any]:
    """Busca thread específica"""
    result = await nocodebackend_request("GET", f"read/threads/{thread_id}")
    return result


@router.delete("/{thread_id}")
async def delete_thread(thread_id: int) -> Dict[str, Any]:
    """Deleta thread (e seus comentários em cascade)"""
    result = await nocodebackend_request("DELETE", f"delete/threads/{thread_id}")
    return {"message": "Thread deleted successfully"}