"""
Base service class with common functionality for all services.
"""
from typing import Dict, Any, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod
import structlog

logger = structlog.get_logger()

T = TypeVar('T')


class BaseService(ABC):
    """Abstract base class for all services"""

    def __init__(self):
        self.logger = logger.bind(service=self.__class__.__name__)

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource"""
        pass

    @abstractmethod
    async def get_by_id(self, resource_id: int) -> Optional[Dict[str, Any]]:
        """Get resource by ID"""
        pass

    @abstractmethod
    async def update(self, resource_id: int, data: Dict[str, Any]) -> bool:
        """Update resource"""
        pass

    @abstractmethod
    async def delete(self, resource_id: int) -> bool:
        """Delete resource"""
        pass

    async def list(self, filters: Optional[Dict[str, Any]] = None,
                   page: int = 1, limit: int = 50) -> List[Dict[str, Any]]:
        """List resources with pagination and filters"""
        pass

    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that required fields are present"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    def _log_operation(self, operation: str, resource_id: Optional[int] = None, **kwargs):
        """Log service operations"""
        log_data = {
            "operation": operation,
            "resource_id": resource_id,
            **kwargs
        }
        self.logger.info(f"service_operation_{operation}", **log_data)