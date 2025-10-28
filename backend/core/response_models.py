"""
Response models for consistent API responses across the application.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.now()


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """User response model"""
    id: int
    name: str
    email: str
    created_at: Optional[datetime] = None


class CommentResponse(BaseModel):
    """Comment response model"""
    id: int
    thread_id: int
    author_name: str
    author_email_hash: str
    content: str
    parent_id: Optional[int] = None
    is_approved: int
    created_at: Optional[datetime] = None
    replies: List['CommentResponse'] = []


class ThreadResponse(BaseModel):
    """Thread response model"""
    id: int
    external_page_id: str
    url: str
    title: str
    usuario_proprietario_id: int
    created_at: Optional[datetime] = None


class CommentListResponse(BaseResponse):
    """Response for comment listing endpoints"""
    comments: List[CommentResponse]
    total: int
    page: int
    limit: int


class ThreadListResponse(BaseResponse):
    """Response for thread listing endpoints"""
    threads: List[ThreadResponse]
    total: int
    page: int
    limit: int


class ModerationStatsResponse(BaseResponse):
    """Response for moderation statistics"""
    pending_count: int
    approved_count: int
    rejected_count: int
    total_count: int


class WidgetCommentsResponse(BaseResponse):
    """Response for widget comments endpoint"""
    thread_id: int
    comments: List[CommentResponse]
    total: int


class HealthCheckResponse(BaseResponse):
    """Health check response"""
    status: str
    version: str
    instance: str
    uptime: Optional[float] = None