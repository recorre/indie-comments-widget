"""
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ThreadCreate(BaseModel):
    external_page_id: str
    url: str
    title: str


class CommentCreate(BaseModel):
    thread_id: int
    author_name: str
    author_email: EmailStr
    content: str
    parent_id: Optional[int] = None
    is_approved: Optional[int] = 0


class CommentModerate(BaseModel):
    is_approved: int  # 0 = pending, 1 = approved, 2 = rejected