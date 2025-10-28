"""
Shared dependencies and utilities for API routes.
"""
import os
import hashlib
import httpx
import structlog
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

# Configuration
NOCODEBACKEND_URL = "https://openapi.nocodebackend.com"
INSTANCE = os.getenv("INSTANCE", "41300_teste")
API_KEY = os.getenv("NOCODEBACKEND_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Global HTTP client
http_client = httpx.AsyncClient(timeout=30.0)

# Logger
logger = structlog.get_logger()


def get_headers() -> Dict[str, str]:
    """Get headers for NoCodeBackend API requests"""
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def hash_password(password: str) -> str:
    """Hash simples de senha (em produção use bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()


def hash_email(email: str) -> str:
    """Hash de email para privacidade"""
    return hashlib.md5(email.lower().encode()).hexdigest()


async def nocodebackend_request(method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Wrapper para requisições ao NoCodeBackend"""
    url = f"{NOCODEBACKEND_URL}/{endpoint}"

    # Adiciona Instance aos params
    if params is None:
        params = {}
    params["Instance"] = INSTANCE

    try:
        logger.info(
            "nocodebackend_request",
            method=method,
            endpoint=endpoint,
            has_data=bool(data),
            params=params
        )

        if method == "GET":
            response = await http_client.get(url, headers=get_headers(), params=params)
        elif method == "POST":
            response = await http_client.post(url, headers=get_headers(), json=data, params=params)
        elif method == "PUT":
            response = await http_client.put(url, headers=get_headers(), json=data, params=params)
        elif method == "DELETE":
            response = await http_client.delete(url, headers=get_headers(), params=params)
        else:
            raise ValueError(f"Método HTTP não suportado: {method}")

        response.raise_for_status()
        result = response.json()

        logger.info(
            "nocodebackend_request_success",
            method=method,
            endpoint=endpoint,
            status_code=response.status_code
        )

        return result

    except httpx.HTTPStatusError as e:
        logger.error(
            "nocodebackend_request_failed",
            method=method,
            endpoint=endpoint,
            status_code=e.response.status_code,
            response_text=e.response.text
        )
        raise
    except Exception as e:
        logger.error(
            "nocodebackend_request_exception",
            method=method,
            endpoint=endpoint,
            error=str(e)
        )
        raise


async def send_webhook_notification(event_type: str, payload: Dict[str, Any]) -> None:
    """Send webhook notification asynchronously"""
    if not WEBHOOK_URL:
        return

    try:
        webhook_payload = {
            "event": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": payload
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(WEBHOOK_URL, json=webhook_payload)
            response.raise_for_status()

        logger.info(
            "webhook_sent",
            event_type=event_type,
            webhook_url=WEBHOOK_URL,
            status_code=response.status_code
        )

    except Exception as e:
        logger.error(
            "webhook_failed",
            event_type=event_type,
            webhook_url=WEBHOOK_URL,
            error=str(e)
        )