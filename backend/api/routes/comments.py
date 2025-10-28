"""
Comment management routes for the Comment Widget API.
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, Optional, List
import time
import structlog
from datetime import datetime
import asyncio

from ..models import CommentCreate, CommentModerate
from ..dependencies import nocodebackend_request, hash_email, send_webhook_notification

router = APIRouter()
logger = structlog.get_logger()


@router.post("/")
async def create_comment(comment: CommentCreate) -> Dict[str, Any]:
    """Cria comentário (público - não precisa autenticação)"""
    start_time = time.time()

    logger.info(
        "comment_creation_started",
        thread_id=comment.thread_id,
        author_name=comment.author_name,
        content_length=len(comment.content),
        has_parent=bool(comment.parent_id),
        is_approved=comment.is_approved
    )

    try:
        data = {
            "thread_referencia_id": comment.thread_id,
            "author_name": comment.author_name,
            "author_email_hash": hash_email(comment.author_email),
            "content": comment.content,
            "is_approved": comment.is_approved  # Use provided value or default to 0
        }

        if comment.parent_id:
            data["parent_id"] = comment.parent_id

        result = await nocodebackend_request("POST", "create/comments", data)

        duration = time.time() - start_time
        logger.info(
            "comment_creation_success",
            thread_id=comment.thread_id,
            comment_id=result.get("id"),
            duration_ms=round(duration * 1000, 2),
            author_name=comment.author_name
        )

        # Send webhook notification asynchronously if configured
        from ..dependencies import WEBHOOK_URL
        if WEBHOOK_URL:
            asyncio.create_task(send_webhook_notification("comment.created", {
                "comment_id": result.get("id"),
                "thread_id": comment.thread_id,
                "author_name": comment.author_name,
                "content": comment.content,
                "is_approved": comment.is_approved,
                "created_at": datetime.now().isoformat(),
                "parent_id": comment.parent_id
            }))

        return result

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "comment_creation_failed",
            thread_id=comment.thread_id,
            author_name=comment.author_name,
            error=str(e),
            duration_ms=round(duration * 1000, 2)
        )
        raise


@router.get("/")
async def list_comments(
    thread_id: Optional[int] = None,
    is_approved: Optional[int] = None,
    page: int = 1,
    limit: int = 50
) -> Dict[str, Any]:
    """Lista comentários (com filtros opcionais)"""
    params = {"page": page, "limit": limit, "sort": "created_at", "order": "asc"}

    if thread_id:
        params["thread_referencia_id"] = thread_id
    if is_approved is not None:
        params["is_approved"] = is_approved

    result = await nocodebackend_request("GET", "read/comments", params=params)
    return result


@router.get("/{comment_id}")
async def get_comment(comment_id: int) -> Dict[str, Any]:
    """Busca comentário específico"""
    result = await nocodebackend_request("GET", f"read/comments/{comment_id}")
    return result


@router.put("/{comment_id}/moderate")
async def moderate_comment(comment_id: int, moderation: CommentModerate) -> Dict[str, Any]:
    """Modera comentário (aprovar/rejeitar)"""
    data = {"is_approved": moderation.is_approved}
    result = await nocodebackend_request("PUT", f"update/comments/{comment_id}", data)

    status = "approved" if moderation.is_approved == 1 else "rejected"
    return {"message": f"Comment {status} successfully"}


@router.post("/moderate")
async def moderate_comments_bulk(request: Request) -> Dict[str, Any]:
    """Endpoint para moderação em lote - relays to NoCodeBackend"""
    # This endpoint relays moderation requests to NoCodeBackend
    # In a real implementation, you'd add authentication here to ensure only site owners can moderate

    body = await request.json()
    comment_ids = body.get("comment_ids", [])
    action = body.get("action")  # "approve" or "reject"

    if not comment_ids or action not in ["approve", "reject"]:
        logger.warning("bulk_moderate_invalid_params", comment_ids_count=len(comment_ids), action=action)
        raise HTTPException(status_code=400, detail="Invalid request parameters")

    # Map action to is_approved value
    is_approved = 1 if action == "approve" else 2

    results = []
    for comment_id in comment_ids:
        try:
            data = {"is_approved": is_approved}
            result = await nocodebackend_request("PUT", f"update/comments/{comment_id}", data)
            results.append({"comment_id": comment_id, "status": "success"})
        except Exception as e:
            results.append({"comment_id": comment_id, "status": "error", "error": str(e)})

    return {"results": results, "total_processed": len(results)}


@router.delete("/{comment_id}")
async def delete_comment(comment_id: int) -> Dict[str, Any]:
    """Deleta comentário"""
    result = await nocodebackend_request("DELETE", f"delete/comments/{comment_id}")
    return {"message": "Comment deleted successfully"}