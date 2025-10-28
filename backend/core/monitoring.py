"""
Monitoring and metrics endpoints for the Comment Widget API
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import psutil
import time
from datetime import datetime
from typing import Dict, Any
import os

from .performance import metrics_collector, cache_manager

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "comment-widget-api",
        "checks": {}
    }

    # System health checks
    try:
        # Memory usage
        memory = psutil.virtual_memory()
        health_status["checks"]["memory"] = {
            "usage_percent": memory.percent,
            "available_mb": memory.available / 1024 / 1024,
            "status": "healthy" if memory.percent < 90 else "warning"
        }

        # Disk usage
        disk = psutil.disk_usage('/')
        health_status["checks"]["disk"] = {
            "usage_percent": disk.percent,
            "free_gb": disk.free / 1024 / 1024 / 1024,
            "status": "healthy" if disk.percent < 90 else "warning"
        }

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        health_status["checks"]["cpu"] = {
            "usage_percent": cpu_percent,
            "status": "healthy" if cpu_percent < 80 else "warning"
        }

    except Exception as e:
        health_status["checks"]["system"] = {
            "status": "error",
            "error": str(e)
        }

    # Application health checks
    try:
        # Environment variables
        required_vars = ["NOCODEBACKEND_API_KEY", "INSTANCE"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        health_status["checks"]["environment"] = {
            "status": "healthy" if not missing_vars else "error",
            "missing_variables": missing_vars
        }

        # Cache health (if enabled)
        if cache_manager.enabled:
            health_status["checks"]["cache"] = {
                "status": "healthy",
                "enabled": True
            }
        else:
            health_status["checks"]["cache"] = {
                "status": "disabled",
                "enabled": False
            }

    except Exception as e:
        health_status["checks"]["application"] = {
            "status": "error",
            "error": str(e)
        }

    # Determine overall status
    if any(check.get("status") == "error" for check in health_status["checks"].values()):
        health_status["status"] = "unhealthy"
    elif any(check.get("status") == "warning" for check in health_status["checks"].values()):
        health_status["status"] = "warning"

    # Set HTTP status code
    status_code = 200
    if health_status["status"] == "warning":
        status_code = 200  # Still OK, but with warnings
    elif health_status["status"] == "unhealthy":
        status_code = 503  # Service unavailable

    return JSONResponse(content=health_status, status_code=status_code)


@router.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """Prometheus-style metrics endpoint"""
    stats = metrics_collector.get_stats()

    # Format as Prometheus metrics
    metrics_output = f"""# HELP comment_widget_requests_total Total number of requests
# TYPE comment_widget_requests_total counter
comment_widget_requests_total {stats['requests_total']}

# HELP comment_widget_errors_total Total number of errors
# TYPE comment_widget_errors_total counter
comment_widget_errors_total {stats['errors_total']}

# HELP comment_widget_cache_hit_ratio Cache hit ratio
# TYPE comment_widget_cache_hit_ratio gauge
comment_widget_cache_hit_ratio {stats['cache_hit_ratio']}

# HELP comment_widget_response_time_seconds Response time statistics
# TYPE comment_widget_response_time_seconds gauge
comment_widget_avg_response_time_seconds {stats['avg_response_time']}
comment_widget_min_response_time_seconds {stats['min_response_time']}
comment_widget_max_response_time_seconds {stats['max_response_time']}

# HELP comment_widget_up Service uptime
# TYPE comment_widget_up gauge
comment_widget_up 1
"""

    return JSONResponse(
        content={"metrics": metrics_output},
        media_type="text/plain; charset=utf-8"
    )


@router.get("/stats")
async def application_stats() -> Dict[str, Any]:
    """Detailed application statistics"""
    stats = metrics_collector.get_stats()

    # System information
    system_info = {
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "memory_percent": psutil.virtual_memory().percent,
        "disk_total": psutil.disk_usage('/').total,
        "disk_free": psutil.disk_usage('/').free,
        "disk_percent": psutil.disk_usage('/').percent,
    }

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "application": {
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "instance": os.getenv("INSTANCE", "unknown")
        },
        "performance": stats,
        "system": system_info,
        "cache": {
            "enabled": cache_manager.enabled,
            "connected": cache_manager.redis_client is not None if cache_manager.enabled else False
        }
    }


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Simple ping endpoint for load balancer health checks"""
    return {"status": "pong", "timestamp": datetime.utcnow().isoformat()}