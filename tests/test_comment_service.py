"""
Unit tests for CommentService.
Comprehensive tests for comment moderation functionality.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.comment_service import CommentService


class TestCommentService(unittest.TestCase):
    """Test cases for CommentService functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = CommentService()
        # Reset mock data for each test
        self.service._mock_comments = self.service._initialize_mock_data()

    def test_initialization(self):
        """Test service initializes with mock data."""
        self.assertIsInstance(self.service._mock_comments, list)
        self.assertGreater(len(self.service._mock_comments), 0)

        # Check structure of first comment
        comment = self.service._mock_comments[0]
        required_keys = ['id', 'thread_referencia_id', 'author_name', 'content', 'created_at', 'is_approved', 'parent_id']
        for key in required_keys:
            self.assertIn(key, comment)

    async def _test_get_comment(self):
        """Test retrieving a comment by ID."""
        # Test existing comment
        comment = await self.service.get_comment(1)
        self.assertIsNotNone(comment)
        self.assertEqual(comment['id'], 1)
        self.assertEqual(comment['author_name'], 'John Doe')

        # Test non-existing comment
        comment = await self.service.get_comment(999)
        self.assertIsNone(comment)

    async def _test_get_pending_comments(self):
        """Test retrieving pending comments."""
        pending = await self.service.get_pending_comments()
        self.assertIsInstance(pending, list)

        # All should be pending (is_approved = 0)
        for comment in pending:
            self.assertEqual(comment['is_approved'], 0)

        # Test with limit and offset
        limited = await self.service.get_pending_comments(limit=1, offset=0)
        self.assertEqual(len(limited), 1)

    async def _test_get_approved_comments(self):
        """Test retrieving approved comments."""
        # First approve a comment
        await self.service.approve_comment(3)  # Comment 3 is already approved in mock data

        approved = await self.service.get_approved_comments()
        self.assertIsInstance(approved, list)

        # Should have at least one approved comment
        approved_count = sum(1 for c in approved if c['is_approved'] == 1)
        self.assertGreaterEqual(approved_count, 1)

    async def _test_get_rejected_comments(self):
        """Test retrieving rejected comments."""
        # First reject a comment
        await self.service.reject_comment(1)

        rejected = await self.service.get_rejected_comments()
        self.assertIsInstance(rejected, list)

        # Should have at least one rejected comment
        rejected_count = sum(1 for c in rejected if c['is_approved'] == 2)
        self.assertGreaterEqual(rejected_count, 1)

    async def _test_approve_comment(self):
        """Test approving a comment."""
        # Test approving pending comment
        success = await self.service.approve_comment(1)
        self.assertTrue(success)

        # Verify comment is approved
        comment = await self.service.get_comment(1)
        self.assertEqual(comment['is_approved'], 1)

        # Test approving already approved comment
        success = await self.service.approve_comment(1)
        self.assertFalse(success)  # Should fail

        # Test approving non-existing comment
        success = await self.service.approve_comment(999)
        self.assertFalse(success)

    async def _test_reject_comment(self):
        """Test rejecting a comment."""
        # Test rejecting pending comment
        success = await self.service.reject_comment(1)
        self.assertTrue(success)

        # Verify comment is rejected
        comment = await self.service.get_comment(1)
        self.assertEqual(comment['is_approved'], 2)

        # Test rejecting non-existing comment
        success = await self.service.reject_comment(999)
        self.assertFalse(success)

    async def _test_delete_comment(self):
        """Test deleting a comment."""
        initial_count = len(self.service._mock_comments)

        # Test deleting existing comment
        success = await self.service.delete_comment(1)
        self.assertTrue(success)
        self.assertEqual(len(self.service._mock_comments), initial_count - 1)

        # Verify comment is gone
        comment = await self.service.get_comment(1)
        self.assertIsNone(comment)

        # Test deleting non-existing comment
        success = await self.service.delete_comment(999)
        self.assertFalse(success)

    async def _test_create_comment(self):
        """Test creating a new comment."""
        initial_count = len(self.service._mock_comments)

        comment_data = {
            'thread_id': 'thread_new',
            'author_name': 'New User',
            'content': 'New comment content',
            'parent_id': None
        }

        comment = await self.service.create_comment(comment_data)
        self.assertIsNotNone(comment)
        self.assertEqual(len(self.service._mock_comments), initial_count + 1)

        # Verify comment structure
        self.assertIn('id', comment)
        self.assertEqual(comment['thread_referencia_id'], 'thread_new')
        self.assertEqual(comment['author_name'], 'New User')
        self.assertEqual(comment['content'], 'New comment content')
        self.assertEqual(comment['is_approved'], 0)  # Default to pending

    async def _test_update_comment(self):
        """Test updating a comment."""
        # Test updating existing comment
        success = await self.service.update_comment(1, {'content': 'Updated content'})
        self.assertTrue(success)

        # Verify update
        comment = await self.service.get_comment(1)
        self.assertEqual(comment['content'], 'Updated content')

        # Test updating non-existing comment
        success = await self.service.update_comment(999, {'content': 'test'})
        self.assertFalse(success)

    async def _test_get_threaded_comments(self):
        """Test retrieving threaded comments."""
        threaded = await self.service.get_threaded_comments('thread_123')
        self.assertIsInstance(threaded, list)

        # Should have root comments
        root_comments = [c for c in threaded if c['parent_id'] is None]
        self.assertGreater(len(root_comments), 0)

        # Check replies structure
        for comment in threaded:
            self.assertIn('replies', comment)
            self.assertIsInstance(comment['replies'], list)

    async def _test_get_moderation_stats(self):
        """Test getting moderation statistics."""
        stats = await self.service.get_moderation_stats()
        self.assertIsInstance(stats, dict)

        required_keys = ['pending', 'approved', 'rejected', 'total', 'threads']
        for key in required_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], int)
            self.assertGreaterEqual(stats[key], 0)

        # Total should equal sum of pending + approved + rejected
        self.assertEqual(stats['total'], stats['pending'] + stats['approved'] + stats['rejected'])

    async def _test_bulk_operations(self):
        """Test bulk operations on comments."""
        # Create multiple comments
        comment_ids = []
        for i in range(3):
            comment_data = {
                'thread_id': f'thread_bulk_{i}',
                'author_name': f'Bulk User {i}',
                'content': f'Bulk comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Bulk approve
        results = []
        for comment_id in comment_ids:
            success = await self.service.approve_comment(comment_id)
            results.append(success)

        # All should succeed
        self.assertTrue(all(results))

        # Verify all are approved
        for comment_id in comment_ids:
            comment = await self.service.get_comment(comment_id)
            self.assertEqual(comment['is_approved'], 1)

    # Synchronous test runners
    def test_get_comment(self):
        """Run async test for get_comment."""
        asyncio.run(self._test_get_comment())

    def test_get_pending_comments(self):
        """Run async test for get_pending_comments."""
        asyncio.run(self._test_get_pending_comments())

    def test_get_approved_comments(self):
        """Run async test for get_approved_comments."""
        asyncio.run(self._test_get_approved_comments())

    def test_get_rejected_comments(self):
        """Run async test for get_rejected_comments."""
        asyncio.run(self._test_get_rejected_comments())

    def test_approve_comment(self):
        """Run async test for approve_comment."""
        asyncio.run(self._test_approve_comment())

    def test_reject_comment(self):
        """Run async test for reject_comment."""
        asyncio.run(self._test_reject_comment())

    def test_delete_comment(self):
        """Run async test for delete_comment."""
        asyncio.run(self._test_delete_comment())

    def test_create_comment(self):
        """Run async test for create_comment."""
        asyncio.run(self._test_create_comment())

    def test_update_comment(self):
        """Run async test for update_comment."""
        asyncio.run(self._test_update_comment())

    def test_get_threaded_comments(self):
        """Run async test for get_threaded_comments."""
        asyncio.run(self._test_get_threaded_comments())

    def test_get_moderation_stats(self):
        """Run async test for get_moderation_stats."""
        asyncio.run(self._test_get_moderation_stats())

    def test_bulk_operations(self):
        """Run async test for bulk operations."""
        asyncio.run(self._test_bulk_operations())


class TestCommentServiceEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        self.service = CommentService()

    async def _test_empty_thread_comments(self):
        """Test getting comments for non-existing thread."""
        threaded = await self.service.get_threaded_comments('non_existing_thread')
        self.assertEqual(len(threaded), 0)

    async def _test_comment_validation(self):
        """Test comment creation with invalid data."""
        # Test with missing required fields
        invalid_data = {'author_name': 'Test'}  # Missing content
        comment = await self.service.create_comment(invalid_data)
        # Service should still create comment (no validation in mock)
        self.assertIsNotNone(comment)

    async def _test_concurrent_operations(self):
        """Test concurrent operations on the same comment."""
        import asyncio

        async def approve_operation():
            return await self.service.approve_comment(1)

        async def reject_operation():
            await asyncio.sleep(0.01)  # Small delay
            return await self.service.reject_comment(1)

        # Run concurrent operations
        results = await asyncio.gather(approve_operation(), reject_operation())

        # First operation should succeed, second should fail
        self.assertTrue(results[0])
        self.assertFalse(results[1])

    def test_empty_thread_comments(self):
        """Run async test for empty thread comments."""
        asyncio.run(self._test_empty_thread_comments())

    def test_comment_validation(self):
        """Run async test for comment validation."""
        asyncio.run(self._test_comment_validation())

    def test_concurrent_operations(self):
        """Run async test for concurrent operations."""
        asyncio.run(self._test_concurrent_operations())


if __name__ == '__main__':
    unittest.main(verbosity=2)