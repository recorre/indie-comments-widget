"""
Authentication routes for the frontend application.
"""
from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Optional
from datetime import datetime, timedelta
import hashlib

try:
    from utils.helpers import (
        hash_password,
        generate_session_id,
        validate_email,
        validate_password
    )
except ImportError:
    # Fallback for direct execution
    from ..utils.helpers import (
        hash_password,
        generate_session_id,
        validate_email,
        validate_password
    )

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Backend API configuration
BACKEND_URL = "http://localhost:8000"
http_client = httpx.AsyncClient(timeout=30.0)

# Session management (simple in-memory for demo)
sessions = {}


async def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session"""
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return None

    user_data = sessions[session_id]
    if datetime.now() - user_data["created_at"] > timedelta(hours=24):
        del sessions[session_id]
        return None

    return user_data["user"]


async def backend_request(method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None):
    """Make request to backend API"""
    url = f"{BACKEND_URL}{endpoint}"

    try:
        if method == "GET":
            response = await http_client.get(url, params=params)
        elif method == "POST":
            response = await http_client.post(url, json=data, params=params)
        elif method == "PUT":
            response = await http_client.put(url, json=data, params=params)
        elif method == "DELETE":
            response = await http_client.delete(url, params=params)

        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(request: Request, email: str = Form(), password: str = Form()):
    """Handle login"""
    try:
        # Validate input
        if not validate_email(email) or not validate_password(password):
            raise HTTPException(status_code=400, detail="Invalid email or password format")

        # Authenticate with backend
        result = await backend_request("POST", "/auth/login", {
            "email": email,
            "password": password
        })

        # Create session
        session_id = generate_session_id(email)
        sessions[session_id] = {
            "user": result,
            "created_at": datetime.now()
        }

        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response

    except HTTPException:
        error_message = "Invalid credentials"
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": error_message
        })


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Register page"""
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register(request: Request, name: str = Form(), email: str = Form(), password: str = Form()):
    """Handle registration"""
    try:
        # Validate input
        if not name or len(name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
        if not validate_email(email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        if not validate_password(password):
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

        # Register with backend
        result = await backend_request("POST", "/auth/register", {
            "name": name.strip(),
            "email": email.lower(),
            "password": password
        })

        # Auto-login after registration
        session_id = generate_session_id(email)
        sessions[session_id] = {
            "user": result,
            "created_at": datetime.now()
        }

        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response

    except HTTPException as e:
        error_message = str(e.detail)
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": error_message
        })


@router.get("/logout")
async def logout(request: Request):
    """Logout"""
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        del sessions[session_id]

    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="session_id")
    return response