from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from backend.core.cache import SWRCache
import json

router = APIRouter()

# Initialize cache
cache = SWRCache(ttl=300, max_size=100)  # 5 minutes cache for widget config

# Default widget configuration
DEFAULT_WIDGET_CONFIG = {
    "theme": "default",
    "position": "bottom-right",
    "max_comments": 50,
    "auto_load": True,
    "show_timestamps": True,
    "allow_anonymous": False,
    "require_moderation": True,
    "custom_css": "",
    "colors": {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "background": "#ffffff",
        "text": "#212529"
    }
}

@router.get("/widget/config")
async def get_widget_config(thread_id: Optional[str] = Query(None, description="Thread ID for specific config")):
    """
    Get widget configuration.
    Returns default config or thread-specific config if available.
    """
    cache_key = f"widget_config:{thread_id or 'default'}"

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # For now, return default config
    # In a real implementation, this would fetch from database
    config = DEFAULT_WIDGET_CONFIG.copy()

    if thread_id:
        # Add thread-specific overrides if any
        config["thread_id"] = thread_id

    cache.set(cache_key, config)
    return config

@router.post("/widget/config")
async def update_widget_config(
    config: Dict[str, Any] = Body(..., description="Widget configuration object"),
    thread_id: Optional[str] = Query(None, description="Thread ID for specific config")
):
    """
    Update widget configuration.
    """
    try:
        # Validate configuration
        validated_config = DEFAULT_WIDGET_CONFIG.copy()
        validated_config.update(config)

        # Ensure required fields
        required_fields = ["theme", "position", "max_comments"]
        for field in required_fields:
            if field not in validated_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Validate theme
        valid_themes = ["default", "dark", "light", "custom"]
        if validated_config["theme"] not in valid_themes:
            raise HTTPException(status_code=400, detail=f"Invalid theme. Must be one of: {', '.join(valid_themes)}")

        # Validate position
        valid_positions = ["bottom-right", "bottom-left", "top-right", "top-left", "inline"]
        if validated_config["position"] not in valid_positions:
            raise HTTPException(status_code=400, detail=f"Invalid position. Must be one of: {', '.join(valid_positions)}")

        # In a real implementation, save to database
        # For now, just cache it
        cache_key = f"widget_config:{thread_id or 'default'}"
        cache.set(cache_key, validated_config)

        return {
            "message": "Widget configuration updated successfully",
            "config": validated_config
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update widget config: {str(e)}")

@router.get("/widget/embed/{thread_id}")
async def get_widget_embed_code(thread_id: str):
    """
    Generate embed code for a specific thread.
    """
    try:
        # Get widget config for this thread
        config_response = await get_widget_config(thread_id)
        config = config_response

        # Generate embed HTML
        embed_html = f"""
<div id="comment-widget-{thread_id}"></div>
<script>
(function() {{
    var script = document.createElement('script');
    script.src = '{{"{{ url_for('static', filename='js/widgetv01.js') }}"}}';
    script.onload = function() {{
        CommentWidget.init('{thread_id}', {json.dumps(config)});
    }};
    document.head.appendChild(script);
}})();
</script>
"""

        # Generate embed script
        embed_script = f"""
// Comment Widget Embed Code for Thread: {thread_id}
(function() {{
    var config = {json.dumps(config, indent=2)};
    // Widget initialization code would go here
    console.log('Comment widget loaded for thread: {thread_id}', config);
}})();
"""

        return {
            "thread_id": thread_id,
            "embed_html": embed_html.strip(),
            "embed_script": embed_script.strip(),
            "config": config
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embed code: {str(e)}")

@router.get("/widget/themes")
async def get_available_themes():
    """
    Get list of available widget themes.
    """
    cache_key = "widget_themes"

    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    themes = {
        "themes": [
            {
                "id": "default",
                "name": "Default",
                "description": "Clean, modern design with neutral colors",
                "preview": "/static/css/themes/default.css"
            },
            {
                "id": "dark",
                "name": "Dark",
                "description": "Dark theme for better contrast",
                "preview": "/static/css/themes/dark.css"
            },
            {
                "id": "light",
                "name": "Light",
                "description": "Bright, minimal design",
                "preview": "/static/css/themes/light.css"
            },
            {
                "id": "custom",
                "name": "Custom",
                "description": "Fully customizable theme",
                "preview": "/static/css/themes/custom.css"
            }
        ]
    }

    cache.set(cache_key, themes)
    return themes

@router.post("/widget/preview")
async def preview_widget(
    config: Dict[str, Any] = Body(..., description="Widget configuration for preview")
):
    """
    Generate a preview of the widget with given configuration.
    """
    try:
        # Validate and merge with defaults
        preview_config = DEFAULT_WIDGET_CONFIG.copy()
        preview_config.update(config)

        # Generate preview HTML
        preview_html = f"""
<div class="comment-widget-preview" style="border: 1px solid #ddd; padding: 20px; border-radius: 8px; background: {preview_config['colors']['background']}; color: {preview_config['colors']['text']};">
    <h4>Widget Preview - {preview_config['theme'].title()} Theme</h4>
    <p>This is how your comment widget will look with the current configuration.</p>
    <div class="preview-comment">
        <strong>Sample Comment</strong>
        <p>This is a preview of how comments will appear in your widget.</p>
        <small>Posted just now</small>
    </div>
    <button style="background: {preview_config['colors']['primary']}; color: white; border: none; padding: 8px 16px; border-radius: 4px;">
        Add Comment
    </button>
</div>
"""

        return {
            "preview_html": preview_html,
            "config": preview_config
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {str(e)}")