"""
FastAPI Proxy para NoCodeBackend
Deploy: Vercel
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
import httpx
import os
from datetime import datetime, timedelta
import hashlib
from dotenv import load_dotenv
import os
import structlog
import time

# Import route modules
from .routes import auth, threads, comments, widget, advanced

# Import monitoring routes
try:
    from core.monitoring import router as monitoring_router
except ImportError:
    monitoring_router = None

# Load environment variables from backend/.env
load_dotenv(dotenv_path='backend/.env')

# ========================
# LOGGING CONFIGURATION
# ========================

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Get logger
logger = structlog.get_logger()

# ========================
# APP CONFIGURATION
# ========================

app = FastAPI(
    title="Comment Widget Proxy API",
    description="Proxy para NoCodeBackend - Hackathon Edition",
    version="1.0.0"
)

# Add middleware
try:
    from core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
except ImportError:
    pass

# Include route modules
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(threads.router, prefix="/threads", tags=["threads"])
app.include_router(comments.router, prefix="/comments", tags=["comments"])
app.include_router(widget.router, prefix="/widget", tags=["widget"])
app.include_router(advanced.router, prefix="/api", tags=["advanced"])

# ========================
# HEALTH CHECK
# ========================

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "service": "Comment Widget Proxy",
        "status": "online",
        "version": "1.0.0",
        "instance": os.getenv("INSTANCE", "41300_teste")
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Verifica se a API está funcionando"""
    api_key = os.getenv("NOCODEBACKEND_API_KEY")
    if not api_key:
        return {"status": "error", "message": "API_KEY not configured"}
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ========================
# LIFESPAN MANAGEMENT
# ========================

# HTTP client for external requests (global variable)
http_client = None

@app.on_event("startup")
async def startup():
    """Initialize connections on startup"""
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown():
    """Close connections on shutdown"""
    global http_client
    if http_client:
        await http_client.aclose()
    logger.info("Application shutdown")

# ========================
# VERCEL HANDLER
# ========================

# Para Vercel, exportar o app
handler = app
