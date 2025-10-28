"""
Public pages routes for the frontend application.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page with widget demo"""
    # Get URL parameter for theme
    theme = request.query_params.get('tema', 'default')

    # Validate theme
    valid_themes = ['default', 'dark', 'matrix', 'neocities', 'serene-mist', 'neon-pulse', 'geometric-prime', 'forest-flow', 'digital-chaos']
    if theme not in valid_themes:
        theme = 'default'

    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_theme": theme,
        "available_themes": valid_themes
    })


# Note: Exception handlers should be added to the main app, not individual routers