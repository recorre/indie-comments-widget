"""
API endpoint tests for comments and moderation functionality.
Tests FastAPI endpoints using TestClient.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import routers and services
from api.comments import router as comments_router
from api.moderation import router as moderation_router
from services.comment_service import CommentService


class TestCommentsAPI(unittest.TestCase):
    """Test cases for comments API endpoints."""

    def setUp(self):
        """Set up test client and fixtures."""
        self.app = FastAPI()
        self.app.include_router(comments_router, prefix="/api/v1")
        self.app.include_router(moderation_router, prefix="/api/v1")

        self.client = TestClient(self.app)
        self.comment_service = CommentService()

    @patch('api.comments.nocodebackend_service')
    def test_get_comments_endpoint(self, mock_service):
        """Test GET /comments endpoint."""
        # Mock the service response
        mock_service.get_comments.return_value = [
            {
                "id": 1,
                "thread_referencia_id": "thread_123",
                "author_name": "Test User",
                "content": "Test comment",
                "created_at": "2024-01-01T00:00:00Z",
                "is_approved": 1,
                "parent_id": None
            }
        ]

        response = self.client.get("/api/v1/comments?thread_id=thread_123")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("comments", data)
        self.assertIn("thread_id", data)
        self.assertEqual(data["thread_id"], "thread_123")

    @patch('api.comments.nocodebackend_service')
    def test_get_comments_mock_data(self, mock_service):
        """Test GET /comments with mock data for thread_123."""
        response = self.client.get("/api/v1/comments?thread_id=thread_123")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("comments", data)
        self.assertEqual(len(data["comments"]), 2)  # Mock data has 2 comments

        # Check comment structure
        comment = data["comments"][0]
        required_keys = ["id", "thread_referencia_id", "author_name", "content", "created_at", "is_approved", "parent_id", "replies"]
        for key in required_keys:
            self.assertIn(key, comment)

    def test_get_comment_stats_endpoint(self):
        """Test GET /comments/stats endpoint."""
        response = self.client.get("/api/v1/comments/stats")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        required_keys = ["pending_count", "approved_count", "last_update"]
        for key in required_keys:
            self.assertIn(key, data)

    @patch('api.comments.update_comment_counts')
    def test_comment_stats_updates(self, mock_update):
        """Test that comment stats trigger updates."""
        mock_update.return_value = None

        response = self.client.get("/api/v1/comments/stats")
        self.assertEqual(response.status_code, 200)
        mock_update.assert_called_once()

    def test_stream_comments_endpoint(self):
        """Test GET /comments/stream endpoint."""
        # Test that endpoint exists and returns proper content type
        response = self.client.get("/api/v1/comments/stream", timeout=1)
        # Should return 200 and be a streaming response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "text/event-stream")


class TestModerationAPI(unittest.TestCase):
    """Test cases for moderation API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.app = FastAPI()
        self.app.include_router(moderation_router, prefix="/api/v1")
        self.client = TestClient(self.app)

    def test_get_comments_for_moderation_default(self):
        """Test GET /moderation/comments with default parameters."""
        response = self.client.get("/api/v1/moderation/comments")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        required_keys = ["comments", "total", "limit", "offset", "status"]
        for key in required_keys:
            self.assertIn(key, data)

        self.assertEqual(data["status"], "pending")  # Default status

    def test_get_comments_for_moderation_with_status(self):
        """Test GET /moderation/comments with different statuses."""
        for status in ["pending", "approved", "rejected"]:
            response = self.client.get(f"/api/v1/moderation/comments?status={status}")
            self.assertEqual(response.status_code, 200)

            data = response.json()
            self.assertEqual(data["status"], status)

    def test_get_comments_for_moderation_pagination(self):
        """Test GET /moderation/comments with pagination."""
        response = self.client.get("/api/v1/moderation/comments?limit=5&offset=0")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["limit"], 5)
        self.assertEqual(data["offset"], 0)

    def test_bulk_moderate_comments_approve(self):
        """Test POST /moderation/bulk approve action."""
        payload = {
            "comment_ids": [1, 2],
            "action": "approve"
        }

        response = self.client.post("/api/v1/moderation/bulk", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("message", data)
        self.assertIn("results", data)
        self.assertIn("successful", data)
        self.assertIn("total", data)

    def test_bulk_moderate_comments_reject(self):
        """Test POST /moderation/bulk reject action."""
        payload = {
            "comment_ids": [1],
            "action": "reject"
        }

        response = self.client.post("/api/v1/moderation/bulk", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("Successfully rejected", data["message"])

    def test_bulk_moderate_comments_delete(self):
        """Test POST /moderation/bulk delete action."""
        payload = {
            "comment_ids": [1],
            "action": "delete"
        }

        response = self.client.post("/api/v1/moderation/bulk", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("Successfully deleted", data["message"])

    def test_bulk_moderate_invalid_action(self):
        """Test POST /moderation/bulk with invalid action."""
        payload = {
            "comment_ids": [1],
            "action": "invalid_action"
        }

        response = self.client.post("/api/v1/moderation/bulk", json=payload)
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn("Invalid action", data["detail"])

    def test_bulk_moderate_empty_ids(self):
        """Test POST /moderation/bulk with empty comment IDs."""
        payload = {
            "comment_ids": [],
            "action": "approve"
        }

        response = self.client.post("/api/v1/moderation/bulk", json=payload)
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn("No comment IDs provided", data["detail"])

    def test_moderate_single_comment_approve(self):
        """Test POST /moderation/{comment_id} approve."""
        payload = {"action": "approve"}

        response = self.client.post("/api/v1/moderation/1", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["comment_id"], 1)
        self.assertEqual(data["action"], "approve")

    def test_moderate_single_comment_reject(self):
        """Test POST /moderation/{comment_id} reject."""
        payload = {"action": "reject"}

        response = self.client.post("/api/v1/moderation/2", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["action"], "reject")

    def test_moderate_single_comment_delete(self):
        """Test POST /moderation/{comment_id} delete."""
        payload = {"action": "delete"}

        response = self.client.post("/api/v1/moderation/3", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["action"], "delete")

    def test_moderate_single_invalid_action(self):
        """Test POST /moderation/{comment_id} with invalid action."""
        payload = {"action": "invalid"}

        response = self.client.post("/api/v1/moderation/1", json=payload)
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn("Invalid action", data["detail"])

    def test_moderate_single_nonexistent_comment(self):
        """Test POST /moderation/{comment_id} with non-existent comment."""
        payload = {"action": "approve"}

        response = self.client.post("/api/v1/moderation/999", json=payload)
        self.assertEqual(response.status_code, 404)

        data = response.json()
        self.assertIn("Comment not found", data["detail"])

    def test_get_moderation_stats(self):
        """Test GET /moderation/stats endpoint."""
        response = self.client.get("/api/v1/moderation/stats")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        required_keys = ["pending", "approved", "rejected", "total", "threads"]
        for key in required_keys:
            self.assertIn(key, data)
            self.assertIsInstance(data[key], int)


class TestAPIErrorHandling(unittest.TestCase):
    """Test error handling in API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.app = FastAPI()
        self.app.include_router(moderation_router, prefix="/api/v1")
        self.client = TestClient(self.app)

    @patch('api.moderation.comment_service.get_moderation_stats')
    def test_moderation_stats_service_error(self, mock_stats):
        """Test moderation stats endpoint when service fails."""
        mock_stats.side_effect = Exception("Service error")

        response = self.client.get("/api/v1/moderation/stats")
        self.assertEqual(response.status_code, 500)

        data = response.json()
        self.assertIn("Failed to fetch moderation stats", data["detail"])

    @patch('api.moderation.comment_service.get_pending_comments')
    def test_comments_moderation_service_error(self, mock_get):
        """Test comments moderation endpoint when service fails."""
        mock_get.side_effect = Exception("Service error")

        response = self.client.get("/api/v1/moderation/comments")
        self.assertEqual(response.status_code, 500)

        data = response.json()
        self.assertIn("Failed to fetch comments", data["detail"])


class TestAPICaching(unittest.TestCase):
    """Test caching behavior in API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.app = FastAPI()
        self.app.include_router(moderation_router, prefix="/api/v1")
        self.client = TestClient(self.app)

    @patch('api.moderation.cache.get')
    @patch('api.moderation.cache.set')
    def test_moderation_comments_caching(self, mock_set, mock_get):
        """Test that moderation comments endpoint uses caching."""
        # Mock cache miss
        mock_get.return_value = None

        response = self.client.get("/api/v1/moderation/comments")
        self.assertEqual(response.status_code, 200)

        # Verify cache was checked and set
        mock_get.assert_called_once()
        mock_set.assert_called_once()

    @patch('api.moderation.cache.get')
    def test_moderation_comments_cache_hit(self, mock_get):
        """Test that moderation comments endpoint returns cached data."""
        cached_data = {
            "comments": [{"id": 1, "content": "cached comment"}],
            "total": 1,
            "limit": 50,
            "offset": 0,
            "status": "pending"
        }
        mock_get.return_value = cached_data

        response = self.client.get("/api/v1/moderation/comments")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data, cached_data)


if __name__ == '__main__':
    unittest.main(verbosity=2)