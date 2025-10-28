from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from backend.core.cache import SWRCache
from backend.services.thread_service import ThreadService

router = APIRouter()

# Initialize cache and services
cache = SWRCache(ttl=120, max_size=500)
thread_service = ThreadService()

@router.get("/threads")
async def get_threads(
    usuario_proprietario_id: Optional[int] = Query(None, description="Filter by owner ID"),
    limit: int = Query(50, description="Maximum number of threads to return"),
    offset: int = Query(0, description="Number of threads to skip")
):
    """
    Get threads with optional filtering.
    Returns all threads or filtered by owner.
    """
    cache_key = f"threads:{usuario_proprietario_id}:{limit}:{offset}"

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        threads = await thread_service.get_threads(
            owner_id=usuario_proprietario_id,
            limit=limit,
            offset=offset
        )

        result = {"threads": threads}
        cache.set(cache_key, result)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch threads: {str(e)}")

@router.post("/threads")
async def create_thread(
    title: str = Body(..., description="Thread title"),
    url: str = Body(..., description="Page URL for the thread"),
    owner_id: Optional[int] = Body(None, description="Owner ID")
):
    """
    Create a new thread.
    """
    if not title or not url:
        raise HTTPException(status_code=400, detail="Title and URL are required")

    try:
        thread_data = {
            "title": title,
            "url": url,
            "owner_id": owner_id or 1,  # Default owner
            "external_page_id": f"thread_{len(await thread_service.get_threads()) + 1}"  # Simple ID generation
        }

        thread = await thread_service.create_thread(thread_data)

        # Clear relevant caches
        cache.clear()

        return {"thread": thread, "message": "Thread created successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create thread: {str(e)}")

@router.get("/threads/{thread_id}")
async def get_thread(thread_id: int):
    """
    Get a specific thread by ID.
    """
    cache_key = f"thread:{thread_id}"

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        thread = await thread_service.get_thread(thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        cache.set(cache_key, thread)
        return thread

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch thread: {str(e)}")

@router.put("/threads/{thread_id}")
async def update_thread(
    thread_id: int,
    title: Optional[str] = Body(None, description="New thread title"),
    url: Optional[str] = Body(None, description="New page URL")
):
    """
    Update an existing thread.
    """
    try:
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if url is not None:
            update_data["url"] = url

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        success = await thread_service.update_thread(thread_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Clear relevant caches
        cache.clear()

        return {"message": "Thread updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update thread: {str(e)}")

@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: int):
    """
    Delete a thread by ID.
    """
    try:
        success = await thread_service.delete_thread(thread_id)
        if not success:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Clear relevant caches
        cache.clear()

        return {"message": "Thread deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete thread: {str(e)}")

@router.get("/threads/{thread_id}/stats")
async def get_thread_stats(thread_id: int):
    """
    Get statistics for a specific thread.
    """
    cache_key = f"thread_stats:{thread_id}"

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        stats = await thread_service.get_thread_stats(thread_id)
        cache.set(cache_key, stats)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch thread stats: {str(e)}")