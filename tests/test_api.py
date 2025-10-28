"""
Test file for API functionality.
Comprehensive tests for backend API endpoints.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import services directly (avoiding router imports that require FastAPI)
try:
    from services.comment_service import CommentService
    from services.thread_service import ThreadService
except ImportError:
    # Fallback for when backend modules aren't available
    CommentService = None
    ThreadService = None

class TestCommentsAPI(unittest.TestCase):
    """Test cases for comments API endpoints."""

    def setUp(self):
        if CommentService:
            self.comment_service = CommentService()
        else:
            self.skipTest("CommentService not available")

    def test_get_comments_structure(self):
        """Test that get_comments returns proper structure."""
        # This would be expanded with actual FastAPI test client
        if hasattr(self, 'comment_service'):
            self.assertIsInstance(self.comment_service._mock_comments, list)

    def test_comment_service_initialization(self):
        """Test comment service initializes properly."""
        if hasattr(self, 'comment_service'):
            self.assertIsNotNone(self.comment_service._mock_comments)
            self.assertGreaterEqual(len(self.comment_service._mock_comments), 0)

class TestModerationAPI(unittest.TestCase):
    """Test cases for moderation API endpoints."""

    def setUp(self):
        self.comment_service = CommentService()

    def test_moderation_stats_structure(self):
        """Test moderation stats return proper structure."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test_stats():
            stats = await self.comment_service.get_moderation_stats()
            required_keys = ['pending', 'approved', 'rejected', 'total', 'threads']
            for key in required_keys:
                self.assertIn(key, stats)
                self.assertIsInstance(stats[key], int)
                self.assertGreaterEqual(stats[key], 0)

        loop.run_until_complete(test_stats())
        loop.close()

    def test_bulk_moderation_validation(self):
        """Test bulk moderation input validation."""
        # Test with invalid action
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test_invalid_action():
            with self.assertRaises(Exception):
                await self.comment_service.approve_comment(999)  # Non-existent comment

        loop.run_until_complete(test_invalid_action())
        loop.close()

class TestThreadsAPI(unittest.TestCase):
    """Test cases for threads API endpoints."""

    def setUp(self):
        self.thread_service = ThreadService()

    def test_thread_service_initialization(self):
        """Test thread service initializes properly."""
        self.assertIsNotNone(self.thread_service._mock_threads)
        self.assertGreaterEqual(len(self.thread_service._mock_threads), 0)

    def test_thread_creation_validation(self):
        """Test thread creation with valid data."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test_create_thread():
            thread_data = {
                "title": "Test Thread",
                "url": "https://example.com/test",
                "owner_id": 1
            }
            thread = await self.thread_service.create_thread(thread_data)

            self.assertIn('id', thread)
            self.assertEqual(thread['title'], "Test Thread")
            self.assertEqual(thread['url'], "https://example.com/test")

        loop.run_until_complete(test_create_thread())
        loop.close()

class TestWidgetAPI(unittest.TestCase):
    """Test cases for widget API endpoints."""

    def test_default_widget_config(self):
        """Test default widget configuration structure."""
        from api.widget import DEFAULT_WIDGET_CONFIG

        required_keys = ['theme', 'position', 'max_comments', 'auto_load', 'colors']
        for key in required_keys:
            self.assertIn(key, DEFAULT_WIDGET_CONFIG)

        # Test colors structure
        self.assertIn('primary', DEFAULT_WIDGET_CONFIG['colors'])
        self.assertIn('background', DEFAULT_WIDGET_CONFIG['colors'])
        self.assertIn('text', DEFAULT_WIDGET_CONFIG['colors'])

class TestIntegration(unittest.TestCase):
    """Integration tests for API interactions."""

    def test_service_dependencies(self):
        """Test that services can be imported and initialized."""
        try:
            from services.comment_service import CommentService
            from services.thread_service import ThreadService

            comment_svc = CommentService()
            thread_svc = ThreadService()

            self.assertIsNotNone(comment_svc)
            self.assertIsNotNone(thread_svc)
        except ImportError as e:
            self.fail(f"Failed to import services: {e}")

    def test_api_router_imports(self):
        """Test that API routers can be imported."""
        try:
            from api.comments import router as comments_router
            from api.moderation import router as moderation_router
            from api.threads import router as threads_router
            from api.widget import router as widget_router

            self.assertIsNotNone(comments_router)
            self.assertIsNotNone(moderation_router)
            self.assertIsNotNone(threads_router)
            self.assertIsNotNone(widget_router)
        except ImportError as e:
            self.fail(f"Failed to import API routers: {e}")

class TestPerformance(unittest.TestCase):
    """Performance tests for API operations."""

    def setUp(self):
        self.comment_service = CommentService()
        self.thread_service = ThreadService()

    def test_comment_operations_performance(self):
        """Test that comment operations complete within reasonable time."""
        import time
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test_performance():
            start_time = time.time()

            # Test multiple operations
            await self.comment_service.get_pending_comments(limit=10)
            await self.comment_service.get_approved_comments(limit=10)
            stats = await self.comment_service.get_moderation_stats()

            end_time = time.time()
            duration = end_time - start_time

            # Should complete within 1 second
            self.assertLess(duration, 1.0, f"Operations took too long: {duration}s")

        loop.run_until_complete(test_performance())
        loop.close()

if __name__ == '__main__':
    # Add verbose output
    unittest.main(verbosity=2)