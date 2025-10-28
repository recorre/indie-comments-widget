"""
Authentication routes for the Comment Widget API.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import structlog

from ..models import UserCreate, UserLogin
from ..dependencies import nocodebackend_request, hash_password, hash_email

router = APIRouter()
logger = structlog.get_logger()


@router.post("/register")
async def register(user: UserCreate) -> Dict[str, Any]:
    """Registra novo usuário"""
    data = {
        "name": user.name,
        "email": user.email,
        "password_hash": hash_password(user.password),
        "api_key": f"user_api_key_{user.email}",  # Generate a simple API key
        "plan_level": "free",
        "is_supporter": 0
    }

    result = await nocodebackend_request("POST", "create/users", data)

    # Retorna sem o password_hash
    return {
        "id": result.get("id") or result.get("data", {}).get("id"),
        "name": user.name,
        "email": user.email,
        "message": "User created successfully"
    }


@router.post("/login")
async def login(credentials: UserLogin) -> Dict[str, Any]:
    """Login do usuário (simplificado)"""
    # Busca usuário por email
    result = await nocodebackend_request(
        "GET",
        "read/users",
        params={"email": credentials.email}
    )

    users = result if isinstance(result, list) else result.get("data", [])

    if not users:
        logger.warning("login_attempt_failed", email=credentials.email, reason="user_not_found")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = users[0]

    # Verifica senha
    if user.get("password_hash") != hash_password(credentials.password):
        logger.warning("login_attempt_failed", email=credentials.email, reason="invalid_password")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Em produção, gerar JWT token aqui
    return {
        "user_id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "message": "Login successful"
    }