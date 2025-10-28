"""
Widget-specific routes for the Comment Widget API.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional

from ..dependencies import nocodebackend_request

router = APIRouter()


@router.get("/comments/{thread_id}")
async def get_widget_comments(thread_id: int) -> Dict[str, Any]:
    """
    Endpoint otimizado para o widget
    Retorna apenas comentários aprovados com estrutura aninhada
    """
    # Busca comentários aprovados
    result = await nocodebackend_request(
        "GET",
        "read/comments",
        params={
            "thread_referencia_id": thread_id,
            "is_approved": 1,
            "limit": 1000,
            "sort": "created_at",
            "order": "asc"
        }
    )

    comments = result if isinstance(result, list) else result.get("data", [])

    # Organiza em estrutura aninhada
    comment_map = {}
    root_comments = []

    for comment in comments:
        comment["replies"] = []
        comment_map[comment["id"]] = comment

        if comment.get("parent_id"):
            parent = comment_map.get(comment["parent_id"])
            if parent:
                parent["replies"].append(comment)
        else:
            root_comments.append(comment)

    return {
        "thread_id": thread_id,
        "comments": root_comments,
        "total": len(comments)
    }


@router.get("/demo/thread")
async def get_demo_thread() -> Dict[str, Any]:
    """Retorna thread de demonstração pública"""
    # Busca ou cria thread demo
    result = await nocodebackend_request(
        "GET",
        "read/threads",
        params={"external_page_id": "demo-public"}
    )

    threads = result if isinstance(result, list) else result.get("data", [])

    if threads:
        return threads[0]

    # Se não existe, cria (precisa de um user_id válido)
    # Por enquanto retorna erro - criar manualmente ou no setup
    raise HTTPException(status_code=404, detail="Demo thread not found")