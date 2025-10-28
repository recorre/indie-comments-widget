from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from backend.core.cache import SWRCache
from backend.services.comment_service import CommentService

router = APIRouter()

# Initialize cache and services
cache = SWRCache(ttl=120, max_size=500)
comment_service = CommentService()

@router.get("/moderation/comments")
async def get_comments_for_moderation(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    limit: int = Query(50, description="Maximum number of comments to return"),
    offset: int = Query(0, description="Number of comments to skip")
):
    """
    Get comments for moderation dashboard.
    Returns pending comments by default, or filtered by status.
    """
    cache_key = f"moderation_comments:{status}:{limit}:{offset}"

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        # Get comments based on status filter
        if status == "pending":
            comments = await comment_service.get_pending_comments(limit=limit, offset=offset)
        elif status == "approved":
            comments = await comment_service.get_approved_comments(limit=limit, offset=offset)
        elif status == "rejected":
            comments = await comment_service.get_rejected_comments(limit=limit, offset=offset)
        else:
            # Default: get all pending comments
            comments = await comment_service.get_pending_comments(limit=limit, offset=offset)

        result = {
            "comments": comments,
            "total": len(comments),
            "limit": limit,
            "offset": offset,
            "status": status or "pending"
        }

        # Cache the result
        cache.set(cache_key, result)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {str(e)}")

@router.post("/moderation/bulk")
async def bulk_moderate_comments(
    comment_ids: List[int] = Body(..., description="List of comment IDs to moderate"),
    action: str = Body(..., description="Action to perform: approve, reject, delete")
):
    """
    Bulk moderate multiple comments.
    Actions: approve, reject, delete
    """
    if action not in ["approve", "reject", "delete"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be: approve, reject, or delete")

    if not comment_ids:
        raise HTTPException(status_code=400, detail="No comment IDs provided")

    try:
        results = []
        for comment_id in comment_ids:
            if action == "approve":
                success = await comment_service.approve_comment(comment_id)
            elif action == "reject":
                success = await comment_service.reject_comment(comment_id)
            elif action == "delete":
                success = await comment_service.delete_comment(comment_id)

            results.append({"comment_id": comment_id, "success": success})

        # Clear relevant caches
        cache.clear()

        successful_count = sum(1 for r in results if r["success"])
        return {
            "message": f"Successfully {action}d {successful_count} out of {len(comment_ids)} comments",
            "results": results,
            "successful": successful_count,
            "total": len(comment_ids)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk moderate comments: {str(e)}")

@router.post("/moderation/{comment_id}")
async def moderate_comment(
    comment_id: int,
    action: str = Body(..., description="Action to perform: approve, reject, delete")
):
    """
    Moderate a single comment.
    Actions: approve, reject, delete
    """
    if action not in ["approve", "reject", "delete"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be: approve, reject, or delete")

    try:
        if action == "approve":
            success = await comment_service.approve_comment(comment_id)
        elif action == "reject":
            success = await comment_service.reject_comment(comment_id)
        elif action == "delete":
            success = await comment_service.delete_comment(comment_id)

        if not success:
            raise HTTPException(status_code=404, detail="Comment not found or already moderated")

        # Clear relevant caches
        cache.clear()

        return {
            "message": f"Comment {comment_id} successfully {action}d",
            "comment_id": comment_id,
            "action": action
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to moderate comment: {str(e)}")

@router.get("/moderation/stats")
async def get_moderation_stats():
    """
    Get moderation statistics for dashboard.
    """
    cache_key = "moderation_stats"

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        stats = await comment_service.get_moderation_stats()

        # Cache for shorter time since stats change frequently
        cache.set(cache_key, stats)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch moderation stats: {str(e)}")