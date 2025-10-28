# Comment service module for handling comment-related operations

from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta

class CommentService:
    """
    Service class for comment management operations.
    Provides methods for comment creation, retrieval, update, deletion, and moderation.
    """

    def __init__(self):
        # Initialize service dependencies here
        self._mock_comments = self._initialize_mock_data()

    def _initialize_mock_data(self) -> List[Dict[str, Any]]:
        """Initialize mock comment data for development."""
        return [
            {
                "id": 1,
                "thread_referencia_id": "thread_123",
                "author_name": "John Doe",
                "content": "This is a great article! Thanks for sharing.",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "is_approved": 0,  # 0=pending, 1=approved, 2=rejected
                "parent_id": None
            },
            {
                "id": 2,
                "thread_referencia_id": "thread_123",
                "author_name": "Jane Smith",
                "content": "I disagree with some points, but overall well-written.",
                "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                "is_approved": 0,
                "parent_id": None
            },
            {
                "id": 3,
                "thread_referencia_id": "thread_456",
                "author_name": "Bob Wilson",
                "content": "Could you elaborate on the second point?",
                "created_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "is_approved": 1,
                "parent_id": None
            },
            {
                "id": 4,
                "thread_referencia_id": "thread_123",
                "author_name": "Alice Brown",
                "content": "Reply to John's comment.",
                "created_at": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "is_approved": 1,
                "parent_id": 1
            }
        ]

    async def get_comment(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a comment by ID.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        return next((c for c in self._mock_comments if c["id"] == comment_id), None)

    async def get_pending_comments(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get comments pending moderation.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        pending = [c for c in self._mock_comments if c["is_approved"] == 0]
        return pending[offset:offset + limit]

    async def get_approved_comments(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get approved comments.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        approved = [c for c in self._mock_comments if c["is_approved"] == 1]
        return approved[offset:offset + limit]

    async def get_rejected_comments(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get rejected comments.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        rejected = [c for c in self._mock_comments if c["is_approved"] == 2]
        return rejected[offset:offset + limit]

    async def approve_comment(self, comment_id: int) -> bool:
        """
        Approve a comment.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        comment = next((c for c in self._mock_comments if c["id"] == comment_id), None)
        if comment and comment["is_approved"] == 0:
            comment["is_approved"] = 1
            return True
        return False

    async def reject_comment(self, comment_id: int) -> bool:
        """
        Reject a comment.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        comment = next((c for c in self._mock_comments if c["id"] == comment_id), None)
        if comment and comment["is_approved"] == 0:
            comment["is_approved"] = 2
            return True
        return False

    async def delete_comment(self, comment_id: int) -> bool:
        """
        Delete a comment by ID.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        comment = next((c for c in self._mock_comments if c["id"] == comment_id), None)
        if comment:
            self._mock_comments.remove(comment)
            return True
        return False

    async def create_comment(self, comment_data: dict) -> Dict[str, Any]:
        """
        Create a new comment.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        new_id = max(c["id"] for c in self._mock_comments) + 1 if self._mock_comments else 1
        comment = {
            "id": new_id,
            "thread_referencia_id": comment_data.get("thread_id"),
            "author_name": comment_data.get("author_name"),
            "content": comment_data.get("content"),
            "created_at": datetime.now().isoformat(),
            "is_approved": 0,  # Default to pending
            "parent_id": comment_data.get("parent_id")
        }
        self._mock_comments.append(comment)
        return comment

    async def update_comment(self, comment_id: int, comment_data: dict) -> bool:
        """
        Update an existing comment.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        comment = next((c for c in self._mock_comments if c["id"] == comment_id), None)
        if comment:
            for key, value in comment_data.items():
                if key in comment:
                    comment[key] = value
            return True
        return False

    async def get_threaded_comments(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        Get comments for a thread with nested replies.
        """
        await asyncio.sleep(0.01)  # Simulate async operation

        # Get all comments for the thread
        thread_comments = [c for c in self._mock_comments if c["thread_referencia_id"] == thread_id]

        # Build nested structure
        comment_map = {c["id"]: c.copy() for c in thread_comments}
        for comment in comment_map.values():
            comment["replies"] = []

        # Organize into tree structure
        root_comments = []
        for comment in thread_comments:
            if comment["parent_id"] is None:
                root_comments.append(comment_map[comment["id"]])
            else:
                parent = comment_map.get(comment["parent_id"])
                if parent:
                    parent["replies"].append(comment_map[comment["id"]])

        return root_comments

    async def get_moderation_stats(self) -> Dict[str, Any]:
        """
        Get moderation statistics.
        """
        await asyncio.sleep(0.01)  # Simulate async operation
        pending = len([c for c in self._mock_comments if c["is_approved"] == 0])
        approved = len([c for c in self._mock_comments if c["is_approved"] == 1])
        rejected = len([c for c in self._mock_comments if c["is_approved"] == 2])
        total = len(self._mock_comments)

        return {
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "total": total,
            "threads": len(set(c["thread_referencia_id"] for c in self._mock_comments))
        }