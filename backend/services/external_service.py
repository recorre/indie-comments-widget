"""
Service for handling external API calls to NoCodeBackend.
"""
import httpx
from typing import Dict, Any, Optional, List
import structlog
from ..core.exceptions import ExternalServiceError, ConfigurationError
from ..core.config import settings

logger = structlog.get_logger()


class ExternalAPIService:
    """Service for communicating with external APIs"""

    def __init__(self, base_url: str, api_key: str, instance: str, timeout: float = 30.0):
        self.base_url = base_url
        self.api_key = api_key
        self.instance = instance
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("ExternalAPIService must be used as async context manager")
        return self._client

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _prepare_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare query parameters with instance"""
        params = params or {}
        params["Instance"] = self.instance
        return params

    async def request(self, method: str, endpoint: str,
                     data: Optional[Dict[str, Any]] = None,
                     params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the external API"""
        url = f"{self.base_url}/{endpoint}"
        params = self._prepare_params(params)

        try:
            logger.info(
                "external_api_request",
                method=method,
                url=url,
                params=params,
                has_data=bool(data)
            )

            if method.upper() == "GET":
                response = await self.client.get(url, headers=self._get_headers(), params=params)
            elif method.upper() == "POST":
                response = await self.client.post(url, headers=self._get_headers(), json=data, params=params)
            elif method.upper() == "PUT":
                response = await self.client.put(url, headers=self._get_headers(), json=data, params=params)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=self._get_headers(), params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            result = response.json()

            logger.info(
                "external_api_success",
                method=method,
                url=url,
                status_code=response.status_code
            )

            return result

        except httpx.HTTPStatusError as e:
            logger.error(
                "external_api_error",
                method=method,
                url=url,
                status_code=e.response.status_code,
                response_text=e.response.text
            )
            raise ExternalServiceError(
                service="NoCodeBackend",
                message=f"HTTP {e.response.status_code}: {e.response.text}",
                status_code=502,
                details={"status_code": e.response.status_code, "response": e.response.text}
            )
        except Exception as e:
            logger.error(
                "external_api_exception",
                method=method,
                url=url,
                error=str(e)
            )
            raise ExternalServiceError(
                service="NoCodeBackend",
                message=str(e),
                status_code=502,
                details={"error": str(e)}
            )

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET request"""
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST request"""
        return await self.request("POST", endpoint, data=data, params=params)

    async def put(self, endpoint: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """PUT request"""
        return await self.request("PUT", endpoint, data=data, params=params)

    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """DELETE request"""
        return await self.request("DELETE", endpoint, params=params)


class NoCodeBackendService:
    """Service specifically for NoCodeBackend API"""

    def __init__(self):
        if not settings.NOCODEBACKEND_API_KEY:
            raise ConfigurationError("NOCODEBACKEND_API_KEY not configured")

        self.service = ExternalAPIService(
            base_url=settings.NOCODEBACKEND_URL,
            api_key=settings.NOCODEBACKEND_API_KEY,
            instance=settings.INSTANCE
        )

    async def __aenter__(self):
        await self.service.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.service.__aexit__(exc_type, exc_val, exc_tb)

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        return await self.service.post("create/users", user_data)

    async def get_users(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get users with optional filters"""
        result = await self.service.get("read/users", params=filters or {})
        return result if isinstance(result, list) else result.get("data", [])

    async def create_thread(self, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new thread"""
        return await self.service.post("create/threads", thread_data)

    async def get_threads(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get threads with optional filters"""
        result = await self.service.get("read/threads", params=filters or {})
        return result if isinstance(result, list) else result.get("data", [])

    async def update_thread(self, thread_id: int, thread_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a thread"""
        return await self.service.put(f"update/threads/{thread_id}", thread_data)

    async def delete_thread(self, thread_id: int) -> Dict[str, Any]:
        """Delete a thread"""
        return await self.service.delete(f"delete/threads/{thread_id}")

    async def create_comment(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new comment"""
        return await self.service.post("create/comments", comment_data)

    async def get_comments(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get comments with optional filters"""
        result = await self.service.get("read/comments", params=filters or {})
        return result if isinstance(result, list) else result.get("data", [])

    async def update_comment(self, comment_id: int, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a comment"""
        return await self.service.put(f"update/comments/{comment_id}", comment_data)

    async def delete_comment(self, comment_id: int) -> Dict[str, Any]:
        """Delete a comment"""
        return await self.service.delete(f"delete/comments/{comment_id}")