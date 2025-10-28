"""
Advanced API routes with additional filtering and analytics.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime

from ..dependencies import nocodebackend_request

router = APIRouter()


@router.get("/comments")
async def api_list_comments(
    thread_id: Optional[int] = None,
    is_approved: Optional[int] = None,
    status: Optional[str] = None,  # "pending", "approved", "rejected"
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    limit: int = 50
) -> Dict[str, Any]:
    """API endpoint for comments (prefixed with /api/) with advanced filtering"""
    params = {"page": page, "limit": limit, "sort": "created_at", "order": "asc"}

    if thread_id:
        params["thread_referencia_id"] = thread_id

    # Handle status parameter
    if status:
        if status == "pending":
            params["is_approved"] = 0
        elif status == "approved":
            params["is_approved"] = 1
        elif status == "rejected":
            params["is_approved"] = 2
    elif is_approved is not None:
        params["is_approved"] = is_approved

    # Handle search parameter (client-side filtering since backend doesn't support LIKE)
    # Don't add to params, we'll filter after fetching

    # Handle date range
    if date_from:
        params["created_at_gte"] = date_from
    if date_to:
        params["created_at_lte"] = date_to

    result = await nocodebackend_request("GET", "read/comments", params=params)

    # If search is specified, filter client-side since backend doesn't support LIKE queries
    if search:
        comments = result if isinstance(result, list) else result.get("data", [])
        filtered_comments = [
            comment for comment in comments
            if search.lower() in comment.get("content", "").lower() or
               search.lower() in comment.get("author_name", "").lower()
        ]
        if isinstance(result, list):
            return filtered_comments
        else:
            result["data"] = filtered_comments
            return result

    return result


@router.get("/comments/stats")
async def api_get_comment_stats() -> Dict[str, Any]:
    """API endpoint for comment statistics"""
    # Simple implementation - in production this would aggregate from database
    return {
        "pending_count": 0,
        "approved_count": 0,
        "total_count": 0,
        "last_update": datetime.now().isoformat()
    }