"""
API client for frontend to communicate with backend.
"""
import httpx
from typing import Dict, Any, Optional, List
import json


class FrontendAPIClient:
    """API client for frontend-backend communication"""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for endpoint"""
        return f"{self.base_url}{endpoint}"

    async def _request(self, method: str, endpoint: str,
                      data: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request"""
        url = self._build_url(endpoint)

        try:
            if method.upper() == "GET":
                response = await self._client.get(url, params=params)
            elif method.upper() == "POST":
                response = await self._client.post(url, json=data, params=params)
            elif method.upper() == "PUT":
                response = await self._client.put(url, json=data, params=params)
            elif method.upper() == "DELETE":
                response = await self._client.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise Exception(f"API Error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    # Authentication endpoints
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """User login"""
        return await self._request("POST", "/auth/login", {
            "email": email,
            "password": password
        })

    async def register(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """User registration"""
        return await self._request("POST", "/auth/register", {
            "name": name,
            "email": email,
            "password": password
        })

    # Thread endpoints
    async def get_threads(self, user_id: Optional[int] = None,
                         page: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Get threads"""
        params = {"page": page, "limit": limit}
        if user_id:
            params["usuario_proprietario_id"] = user_id

        result = await self._request("GET", "/threads", params=params)
        return result if isinstance(result, list) else result.get("data", [])

    async def create_thread(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new thread"""
        return await self._request("POST", "/threads", thread_data)

    async def get_thread(self, thread_id: int) -> Dict[str, Any]:
        """Get specific thread"""
        return await self._request("GET", f"/threads/{thread_id}")

    async def delete_thread(self, thread_id: int) -> Dict[str, Any]:
        """Delete thread"""
        return await self._request("DELETE", f"/threads/{thread_id}")

    # Comment endpoints
    async def get_comments(self, thread_id: Optional[int] = None,
                          is_approved: Optional[int] = None,
                          page: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
        """Get comments with filters"""
        params = {"page": page, "limit": limit}
        if thread_id:
            params["thread_referencia_id"] = thread_id
        if is_approved is not None:
            params["is_approved"] = is_approved

        result = await self._request("GET", "/comments", params=params)
        return result if isinstance(result, list) else result.get("data", [])

    async def create_comment(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new comment"""
        return await self._request("POST", "/comments", comment_data)

    async def moderate_comment(self, comment_id: int, is_approved: int) -> Dict[str, Any]:
        """Moderate comment"""
        return await self._request("PUT", f"/comments/{comment_id}/moderate", {
            "is_approved": is_approved
        })

    async def delete_comment(self, comment_id: int) -> Dict[str, Any]:
        """Delete comment"""
        return await self._request("DELETE", f"/comments/{comment_id}")

    # Bulk operations
    async def bulk_moderate_comments(self, comment_ids: List[int], action: str) -> Dict[str, Any]:
        """Bulk moderate comments"""
        return await self._request("POST", "/moderate", {
            "comment_ids": comment_ids,
            "action": action
        })

    # Widget endpoints
    async def get_widget_comments(self, thread_id: int) -> Dict[str, Any]:
        """Get comments for widget"""
        return await self._request("GET", f"/widget/comments/{thread_id}")

    # API endpoints with advanced filtering
    async def get_comments_api(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get comments with advanced filtering"""
        params = filters or {}
        return await self._request("GET", "/api/comments", params=params)

    async def get_comment_stats(self) -> Dict[str, Any]:
        """Get comment statistics"""
        return await self._request("GET", "/api/comments/stats")

    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """API health check"""
        return await self._request("GET", "/health")