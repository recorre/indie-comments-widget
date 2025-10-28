"""
Frontend Dashboard - FastAPI + Jinja2
Comment Widget Management Interface
"""

from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Optional
from datetime import datetime, timedelta
import hashlib
import logging

# Import route modules
try:
    from routes import pages, auth, dashboard
except ImportError:
    # Fallback for direct execution
    from .routes import pages, auth, dashboard

# Create FastAPI app
app = FastAPI(
    title="Comment Widget Dashboard",
    description="Management interface for Comment Widget system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount widget files
app.mount("/widget", StaticFiles(directory="../widget"), name="widget")

# Templates
templates = Jinja2Templates(directory="templates")

# Include route modules
app.include_router(pages.router, tags=["pages"])
app.include_router(auth.router, tags=["auth"])
app.include_router(dashboard.router, tags=["dashboard"])

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return templates.TemplateResponse("errors/404.html", {"request": request})

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc):
    return templates.TemplateResponse("errors/500.html", {"request": request})

# Legacy routes (will be removed after full migration to route modules)
# These are kept temporarily for backward compatibility

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000, reload=True)