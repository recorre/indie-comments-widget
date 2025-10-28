"""
Tests for bulk operations in comment moderation.
Tests bulk approve, reject, and delete operations.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.comment_service import CommentService


class TestBulkOperations(unittest.TestCase):
    """Test bulk comment operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = CommentService()
        # Reset mock data
        self.service._mock_comments = self.service._initialize_mock_data()

    async def _test_bulk_approve(self):
        """Test bulk approve operation."""
        # Create test comments
        comment_ids = []
        for i in range(5):
            comment_data = {
                'thread_id': f'bulk_approve_{i}',
                'author_name': f'User {i}',
                'content': f'Comment {i} to approve',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Perform bulk approve
        results = []
        for comment_id in comment_ids:
            success = await self.service.approve_comment(comment_id)
            results.append(success)

        # Verify all succeeded
        self.assertTrue(all(results))

        # Verify all comments are approved
        for comment_id in comment_ids:
            comment = await self.service.get_comment(comment_id)
            self.assertEqual(comment['is_approved'], 1)

        # Verify they appear in approved list
        approved = await self.service.get_approved_comments()
        approved_ids = [c['id'] for c in approved]
        for cid in comment_ids:
            self.assertIn(cid, approved_ids)

        # Verify they don't appear in pending
        pending = await self.service.get_pending_comments()
        pending_ids = [c['id'] for c in pending]
        for cid in comment_ids:
            self.assertNotIn(cid, pending_ids)

    async def _test_bulk_reject(self):
        """Test bulk reject operation."""
        # Create test comments
        comment_ids = []
        for i in range(4):
            comment_data = {
                'thread_id': f'bulk_reject_{i}',
                'author_name': f'User {i}',
                'content': f'Comment {i} to reject',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Perform bulk reject
        results = []
        for comment_id in comment_ids:
            success = await self.service.reject_comment(comment_id)
            results.append(success)

        # Verify all succeeded
        self.assertTrue(all(results))

        # Verify all comments are rejected
        for comment_id in comment_ids:
            comment = await self.service.get_comment(comment_id)
            self.assertEqual(comment['is_approved'], 2)

        # Verify they appear in rejected list
        rejected = await self.service.get_rejected_comments()
        rejected_ids = [c['id'] for c in rejected]
        for cid in comment_ids:
            self.assertIn(cid, rejected_ids)

    async def _test_bulk_delete(self):
        """Test bulk delete operation."""
        # Create test comments
        comment_ids = []
        for i in range(3):
            comment_data = {
                'thread_id': f'bulk_delete_{i}',
                'author_name': f'User {i}',
                'content': f'Comment {i} to delete',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        initial_count = len(self.service._mock_comments)

        # Perform bulk delete
        results = []
        for comment_id in comment_ids:
            success = await self.service.delete_comment(comment_id)
            results.append(success)

        # Verify all succeeded
        self.assertTrue(all(results))

        # Verify comments are deleted
        final_count = len(self.service._mock_comments)
        self.assertEqual(final_count, initial_count - 3)

        # Verify comments don't exist anymore
        for comment_id in comment_ids:
            comment = await self.service.get_comment(comment_id)
            self.assertIsNone(comment)

    async def _test_mixed_bulk_operations(self):
        """Test mixed bulk operations (approve some, reject some, delete some)."""
        # Create 9 test comments
        comment_ids = []
        for i in range(9):
            comment_data = {
                'thread_id': f'mixed_bulk_{i}',
                'author_name': f'User {i}',
                'content': f'Mixed comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Approve first 3
        approve_ids = comment_ids[:3]
        for cid in approve_ids:
            await self.service.approve_comment(cid)

        # Reject next 3
        reject_ids = comment_ids[3:6]
        for cid in reject_ids:
            await self.service.reject_comment(cid)

        # Delete last 3
        delete_ids = comment_ids[6:]
        for cid in delete_ids:
            await self.service.delete_comment(cid)

        # Verify approved comments
        for cid in approve_ids:
            comment = await self.service.get_comment(cid)
            self.assertEqual(comment['is_approved'], 1)

        # Verify rejected comments
        for cid in reject_ids:
            comment = await self.service.get_comment(cid)
            self.assertEqual(comment['is_approved'], 2)

        # Verify deleted comments
        for cid in delete_ids:
            comment = await self.service.get_comment(cid)
            self.assertIsNone(comment)

        # Check stats
        stats = await self.service.get_moderation_stats()
        self.assertGreaterEqual(stats['approved'], 3)
        self.assertGreaterEqual(stats['rejected'], 3)
        # Total should be original + 9 - 3 (deleted) = original + 6

    async def _test_bulk_with_invalid_ids(self):
        """Test bulk operations with mix of valid and invalid IDs."""
        # Create 2 valid comments
        valid_ids = []
        for i in range(2):
            comment_data = {
                'thread_id': f'valid_bulk_{i}',
                'author_name': f'Valid User {i}',
                'content': f'Valid comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            valid_ids.append(comment['id'])

        # Mix with invalid IDs
        all_ids = valid_ids + [999, 888, 777]  # Invalid IDs

        # Try bulk approve
        results = []
        for comment_id in all_ids:
            success = await self.service.approve_comment(comment_id)
            results.append(success)

        # Valid operations should succeed, invalid should fail
        self.assertTrue(results[0])  # First valid
        self.assertTrue(results[1])  # Second valid
        self.assertFalse(results[2]) # First invalid
        self.assertFalse(results[3]) # Second invalid
        self.assertFalse(results[4]) # Third invalid

        # Verify valid comments are approved
        for cid in valid_ids:
            comment = await self.service.get_comment(cid)
            self.assertEqual(comment['is_approved'], 1)

    async def _test_bulk_performance(self):
        """Test performance of bulk operations."""
        import time

        # Create many comments for bulk test
        comment_ids = []
        for i in range(50):
            comment_data = {
                'thread_id': f'perf_bulk_{i}',
                'author_name': f'Perf User {i}',
                'content': f'Performance comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Time bulk approve operation
        start_time = time.time()
        for comment_id in comment_ids:
            await self.service.approve_comment(comment_id)
        end_time = time.time()

        duration = end_time - start_time
        # Should complete in reasonable time (less than 1 second for 50 operations)
        self.assertLess(duration, 1.0, f"Bulk approve took too long: {duration}s")

        # Verify all are approved
        for comment_id in comment_ids:
            comment = await self.service.get_comment(comment_id)
            self.assertEqual(comment['is_approved'], 1)

    async def _test_bulk_thread_safety(self):
        """Test that bulk operations are thread-safe (basic concurrent test)."""
        # Create comments
        comment_ids = []
        for i in range(10):
            comment_data = {
                'thread_id': f'concurrent_bulk_{i}',
                'author_name': f'Concurrent User {i}',
                'content': f'Concurrent comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Simulate concurrent operations using asyncio.gather
        async def approve_operation(cid):
            return await self.service.approve_comment(cid)

        # Run concurrent approvals
        results = await asyncio.gather(*[approve_operation(cid) for cid in comment_ids])

        # All should succeed
        self.assertTrue(all(results))

        # All comments should be approved
        for comment_id in comment_ids:
            comment = await self.service.get_comment(comment_id)
            self.assertEqual(comment['is_approved'], 1)

    # Synchronous test runners
    def test_bulk_approve(self):
        """Run async test for bulk approve."""
        asyncio.run(self._test_bulk_approve())

    def test_bulk_reject(self):
        """Run async test for bulk reject."""
        asyncio.run(self._test_bulk_reject())

    def test_bulk_delete(self):
        """Run async test for bulk delete."""
        asyncio.run(self._test_bulk_delete())

    def test_mixed_bulk_operations(self):
        """Run async test for mixed bulk operations."""
        asyncio.run(self._test_mixed_bulk_operations())

    def test_bulk_with_invalid_ids(self):
        """Run async test for bulk operations with invalid IDs."""
        asyncio.run(self._test_bulk_with_invalid_ids())

    def test_bulk_performance(self):
        """Run async test for bulk performance."""
        asyncio.run(self._test_bulk_performance())

    def test_bulk_thread_safety(self):
        """Run async test for bulk thread safety."""
        asyncio.run(self._test_bulk_thread_safety())


class TestBulkOperationsEdgeCases(unittest.TestCase):
    """Test edge cases for bulk operations."""

    def setUp(self):
        self.service = CommentService()

    async def _test_bulk_empty_list(self):
        """Test bulk operations with empty list."""
        # Empty list should not cause errors
        results = []
        for comment_id in []:
            success = await self.service.approve_comment(comment_id)
            results.append(success)

        self.assertEqual(len(results), 0)

    async def _test_bulk_single_item(self):
        """Test bulk operations with single item."""
        # Create one comment
        comment_data = {
            'thread_id': 'single_bulk',
            'author_name': 'Single User',
            'content': 'Single comment for bulk test',
            'parent_id': None
        }
        comment = await self.service.create_comment(comment_data)

        # Bulk approve single item
        results = []
        for comment_id in [comment['id']]:
            success = await self.service.approve_comment(comment_id)
            results.append(success)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0])

        # Verify approved
        updated_comment = await self.service.get_comment(comment['id'])
        self.assertEqual(updated_comment['is_approved'], 1)

    async def _test_bulk_duplicate_ids(self):
        """Test bulk operations with duplicate IDs."""
        # Create one comment
        comment_data = {
            'thread_id': 'duplicate_bulk',
            'author_name': 'Duplicate User',
            'content': 'Comment for duplicate ID test',
            'parent_id': None
        }
        comment = await self.service.create_comment(comment_data)
        comment_id = comment['id']

        # Try to approve the same ID multiple times
        duplicate_ids = [comment_id, comment_id, comment_id]

        results = []
        for cid in duplicate_ids:
            success = await self.service.approve_comment(cid)
            results.append(success)

        # First should succeed, others should fail
        self.assertTrue(results[0])
        self.assertFalse(results[1])
        self.assertFalse(results[2])

        # Comment should still be approved
        updated_comment = await self.service.get_comment(comment_id)
        self.assertEqual(updated_comment['is_approved'], 1)

    def test_bulk_empty_list(self):
        """Run async test for bulk empty list."""
        asyncio.run(self._test_bulk_empty_list())

    def test_bulk_single_item(self):
        """Run async test for bulk single item."""
        asyncio.run(self._test_bulk_single_item())

    def test_bulk_duplicate_ids(self):
        """Run async test for bulk duplicate IDs."""
        asyncio.run(self._test_bulk_duplicate_ids())


if __name__ == '__main__':
    unittest.main(verbosity=2)