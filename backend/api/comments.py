from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse
from backend.core.cache import SWRCache
from backend.services.nocodebackend import NoCodeBackendService
import asyncio
import json
from datetime import datetime
from typing import Optional

router = APIRouter()

# Initialize cache with ttl=120 and max_size=500
cache = SWRCache(ttl=120, max_size=500)
nocodebackend_service = NoCodeBackendService()

# Store for real-time updates (in production, use Redis/pubsub)
comment_update_store = {
    "pending_count": 0,
    "approved_count": 0,
    "last_update": None
}

@router.api_route("/comments", methods=["GET"])
async def get_comments(request: Request):
    # Get thread_id from query params manually to avoid FastAPI validation
    thread_id = request.query_params.get('thread_id')
    # For testing, let's just return mock data
    if thread_id == "thread_123":
        return {
            "comments": [
                {
                    "id": 1,
                    "thread_referencia_id": "thread_123",
                    "author_name": "John Doe",
                    "content": "This is a great article! Thanks for sharing.",
                    "created_at": "2025-10-27T20:00:00Z",
                    "is_approved": 1,
                    "parent_id": None,
                    "replies": [
                        {
                            "id": 4,
                            "thread_referencia_id": "thread_123",
                            "author_name": "Alice Brown",
                            "content": "Reply to John's comment.",
                            "created_at": "2025-10-27T20:15:00Z",
                            "is_approved": 1,
                            "parent_id": 1,
                            "replies": []
                        }
                    ]
                },
                {
                    "id": 2,
                    "thread_referencia_id": "thread_123",
                    "author_name": "Jane Smith",
                    "content": "I disagree with some points, but overall well-written.",
                    "created_at": "2025-10-27T20:01:00Z",
                    "is_approved": 1,
                    "parent_id": None,
                    "replies": []
                }
            ],
            "thread_id": thread_id
        }

    # Convert string thread_id to int if it's numeric
    if thread_id and thread_id.isdigit():
        thread_id = int(thread_id)
    elif thread_id and thread_id.startswith("thread_"):
        # For now, just pass through string thread_ids
        pass
    else:
        # If thread_id is not provided or invalid, set to None
        thread_id = None
    # Create cache key
    cache_key = f"comments:{thread_id}"

    # Try to get from cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # Fetch from service
    if thread_id:
        result = await nocodebackend_service.get_comments(thread_id)
    else:
        # Fetch all comments
        result = await nocodebackend_service.get_all_comments()

    # Cache the result
    cache.set(cache_key, result)

    # Update real-time store
    await update_comment_counts()

    return result

@router.get("/comments/stats")
async def get_comment_stats():
    """Get real-time comment statistics"""
    await update_comment_counts()
    return comment_update_store

async def update_comment_counts():
    """Update the real-time comment counts"""
    try:
        # Get pending comments count
        pending_result = await nocodebackend_service.get_all_comments(is_approved=0)
        pending_count = len(pending_result) if isinstance(pending_result, list) else len(pending_result.get("data", []))

        # Get approved comments count
        approved_result = await nocodebackend_service.get_all_comments(is_approved=1)
        approved_count = len(approved_result) if isinstance(approved_result, list) else len(approved_result.get("data", []))

        comment_update_store["pending_count"] = pending_count
        comment_update_store["approved_count"] = approved_count
        comment_update_store["last_update"] = datetime.now().isoformat()

    except Exception as e:
        print(f"Error updating comment counts: {e}")

@router.get("/comments/stream")
async def stream_comments():
    """Server-Sent Events endpoint for real-time comment updates"""
    async def event_generator():
        last_pending = 0
        last_approved = 0

        while True:
            try:
                await update_comment_counts()

                current_pending = comment_update_store["pending_count"]
                current_approved = comment_update_store["approved_count"]

                if current_pending != last_pending or current_approved != last_approved:
                    data = {
                        "pending_count": current_pending,
                        "approved_count": current_approved,
                        "total_count": current_pending + current_approved,
                        "timestamp": comment_update_store["last_update"]
                    }

                    yield f"data: {json.dumps(data)}\n\n"

                    last_pending = current_pending
                    last_approved = current_approved

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                print(f"Error in SSE stream: {e}")
                await asyncio.sleep(5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )