"""
Dashboard routes for the frontend application.
"""
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Optional, Dict, Any

from .auth import get_current_user, backend_request

try:
    from utils.helpers import calculate_stats, group_threads_by_site, generate_site_id
except ImportError:
    # Fallback for direct execution
    from ..utils.helpers import calculate_stats, group_threads_by_site, generate_site_id

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Dashboard home"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Get user's threads
        threads = await backend_request("GET", "/threads", params={"usuario_proprietario_id": user.get("user_id")})

        # Get recent comments for moderation
        comments = await backend_request("GET", "/comments", params={"is_approved": 0, "limit": 10})

        # Calculate stats for dashboard
        total_comments = len(comments.get("data", []) if isinstance(comments, dict) else comments)
        approved_comments = len([c for c in (comments.get("data", []) if isinstance(comments, dict) else comments) if c.get("is_approved") == 1])
        pending_comments_count = len([c for c in (comments.get("data", []) if isinstance(comments, dict) else comments) if c.get("is_approved") == 0])
        rejected_comments = len([c for c in (comments.get("data", []) if isinstance(comments, dict) else comments) if c.get("is_approved") == 2])

        stats = {
            "total": total_comments,
            "approved": approved_comments,
            "pending": pending_comments_count,
            "rejected": rejected_comments,
            "threads": len(threads.get("data", []) if isinstance(threads, dict) else threads)
        }

        return templates.TemplateResponse("dashboard/home.html", {
            "request": request,
            "user": user,
            "threads": threads.get("data", []) if isinstance(threads, dict) else threads,
            "pending_comments": comments.get("data", []) if isinstance(comments, dict) else comments,
            "stats": stats
        })

    except HTTPException:
        return templates.TemplateResponse("dashboard/home.html", {
            "request": request,
            "user": user,
            "threads": [],
            "pending_comments": []
        })


@router.get("/dashboard/threads", response_class=HTMLResponse)
async def threads_page(request: Request, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Thread management page"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        threads = await backend_request("GET", "/threads", params={"usuario_proprietario_id": user.get("user_id")})

        return templates.TemplateResponse("dashboard/threads.html", {
            "request": request,
            "user": user,
            "threads": threads.get("data", []) if isinstance(threads, dict) else threads
        })

    except HTTPException:
        return templates.TemplateResponse("dashboard/threads.html", {
            "request": request,
            "user": user,
            "threads": []
        })


@router.get("/dashboard/comments", response_class=HTMLResponse)
async def comments_page(request: Request, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Comment moderation page"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Get pending comments
        pending_comments = await backend_request("GET", "/comments", params={"is_approved": 0})

        # Get approved comments
        approved_comments = await backend_request("GET", "/comments", params={"is_approved": 1, "limit": 50})

        return templates.TemplateResponse("dashboard/comments.html", {
            "request": request,
            "user": user,
            "pending_comments": pending_comments.get("data", []) if isinstance(pending_comments, dict) else pending_comments,
            "approved_comments": approved_comments.get("data", []) if isinstance(approved_comments, dict) else approved_comments
        })

    except HTTPException:
        return templates.TemplateResponse("dashboard/comments.html", {
            "request": request,
            "user": user,
            "pending_comments": [],
            "approved_comments": []
        })


@router.post("/dashboard/comments/{comment_id}/moderate")
async def moderate_comment(comment_id: int, action: str = Form(), user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Moderate a comment (approve/reject)"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        is_approved = 1 if action == "approve" else 2  # 2 = rejected

        result = await backend_request("PUT", f"/comments/{comment_id}/moderate", {
            "is_approved": is_approved
        })

        return RedirectResponse(url="/dashboard/comments", status_code=302)

    except HTTPException:
        raise HTTPException(status_code=500, detail="Failed to moderate comment")


@router.delete("/dashboard/comments/{comment_id}")
async def delete_comment(comment_id: int, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Delete a comment"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        result = await backend_request("DELETE", f"/comments/{comment_id}")
        return RedirectResponse(url="/dashboard/comments", status_code=302)

    except HTTPException:
        raise HTTPException(status_code=500, detail="Failed to delete comment")


@router.post("/dashboard/sites")
async def create_site(site_name: str = Form(), site_url: str = Form(), user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Create a new site with main thread"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Generate site_id from URL (this will be the external_page_id)
        site_id = generate_site_id(site_url)

        # Create main thread for the site
        result = await backend_request("POST", "/threads", {
            "usuario_proprietario_id": user["user_id"],
            "external_page_id": site_id,
            "url": site_url,
            "title": f"{site_name} - Main Thread"
        })

        return RedirectResponse(url="/dashboard/sites", status_code=302)

    except HTTPException:
        raise HTTPException(status_code=500, detail="Failed to create site")


@router.get("/dashboard/sites", response_class=HTMLResponse)
async def sites_page(request: Request, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Sites management page"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Get user's threads (each thread represents a site)
        threads = await backend_request("GET", "/threads", params={"usuario_proprietario_id": user.get("user_id")})

        # Group threads by site (external_page_id)
        sites = group_threads_by_site(threads.get("data", []) if isinstance(threads, dict) else threads)
        sites_list = list(sites.values())

        return templates.TemplateResponse("dashboard/sites.html", {
            "request": request,
            "user": user,
            "sites": sites_list
        })

    except HTTPException:
        return templates.TemplateResponse("dashboard/sites.html", {
            "request": request,
            "user": user,
            "sites": []
        })


@router.get("/dashboard/sites/{site_id}", response_class=HTMLResponse)
async def site_detail_page(site_id: str, request: Request, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Site detail page with threads and comments"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Get all threads for this site
        threads = await backend_request("GET", "/threads", params={
            "usuario_proprietario_id": user.get("user_id"),
            "external_page_id": site_id
        })

        site_info = None
        site_threads = []
        if isinstance(threads, dict) and "data" in threads:
            for thread in threads["data"]:
                if not site_info:
                    site_info = {
                        "site_id": site_id,
                        "site_name": thread.get("title", "").replace(" - Main Thread", ""),
                        "site_url": thread.get("url")
                    }
                site_threads.append(thread)

        # Get comments for all threads in this site
        all_comments = []
        for thread in site_threads:
            try:
                comments = await backend_request("GET", "/comments", params={
                    "thread_referencia_id": thread["id"]
                })
                if isinstance(comments, dict) and "data" in comments:
                    for comment in comments["data"]:
                        comment["thread_title"] = thread.get("title")
                        all_comments.append(comment)
            except:
                pass

        return templates.TemplateResponse("dashboard/site_detail.html", {
            "request": request,
            "user": user,
            "site": site_info,
            "threads": site_threads,
            "comments": all_comments
        })

    except HTTPException:
        return templates.TemplateResponse("dashboard/site_detail.html", {
            "request": request,
            "user": user,
            "site": None,
            "threads": [],
            "comments": []
        })


@router.post("/dashboard/threads")
async def create_thread(title: str = Form(), url: str = Form(), user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Create a new thread"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Generate external_page_id from URL
        external_page_id = generate_site_id(url)

        result = await backend_request("POST", "/threads", {
            "usuario_proprietario_id": user["user_id"],
            "external_page_id": external_page_id,
            "url": url,
            "title": title
        })

        return RedirectResponse(url="/dashboard/threads", status_code=302)

    except HTTPException:
        raise HTTPException(status_code=500, detail="Failed to create thread")


@router.delete("/dashboard/threads/{thread_id}")
async def delete_thread(thread_id: int, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Delete a thread"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        result = await backend_request("DELETE", f"/threads/{thread_id}")
        return RedirectResponse(url="/dashboard/threads", status_code=302)

    except HTTPException:
        raise HTTPException(status_code=500, detail="Failed to delete thread")


@router.get("/dashboard/theme-customizer", response_class=HTMLResponse)
async def theme_customizer(request: Request, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Theme customization page"""
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("dashboard/theme-customizer.html", {
        "request": request,
        "user": user
    })