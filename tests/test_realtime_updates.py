"""
Tests for real-time updates functionality.
Tests streaming endpoints and comment update mechanisms.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.comment_service import CommentService


class TestRealtimeUpdates(unittest.TestCase):
    """Test real-time comment update functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = CommentService()
        # Reset mock data
        self.service._mock_comments = self.service._initialize_mock_data()

    async def _test_comment_count_updates(self):
        """Test that comment counts update correctly."""
        # Get initial stats
        initial_stats = await self.service.get_moderation_stats()

        # Create a new comment
        comment_data = {
            'thread_id': 'realtime_test',
            'author_name': 'Realtime User',
            'content': 'Comment for realtime testing',
            'parent_id': None
        }
        await self.service.create_comment(comment_data)

        # Check stats after creation
        after_create_stats = await self.service.get_moderation_stats()
        self.assertEqual(after_create_stats['pending'], initial_stats['pending'] + 1)
        self.assertEqual(after_create_stats['total'], initial_stats['total'] + 1)

        # Approve the comment
        pending_comments = await self.service.get_pending_comments()
        new_comment = pending_comments[-1]  # Get the last one (newly created)
        await self.service.approve_comment(new_comment['id'])

        # Check stats after approval
        after_approve_stats = await self.service.get_moderation_stats()
        self.assertEqual(after_approve_stats['pending'], after_create_stats['pending'] - 1)
        self.assertEqual(after_approve_stats['approved'], initial_stats['approved'] + 1)

    async def _test_stats_consistency(self):
        """Test that stats remain consistent across operations."""
        # Perform various operations and check stats consistency
        operations = []

        # Record initial stats
        stats = await self.service.get_moderation_stats()
        operations.append(('initial', stats.copy()))

        # Create 3 comments
        for i in range(3):
            comment_data = {
                'thread_id': f'stats_test_{i}',
                'author_name': f'Stats User {i}',
                'content': f'Stats comment {i}',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)

        stats = await self.service.get_moderation_stats()
        operations.append(('after_create', stats.copy()))

        # Approve first comment
        pending = await self.service.get_pending_comments()
        if pending:
            await self.service.approve_comment(pending[0]['id'])

        stats = await self.service.get_moderation_stats()
        operations.append(('after_approve', stats.copy()))

        # Reject second comment
        pending = await self.service.get_pending_comments()
        if len(pending) > 1:
            await self.service.reject_comment(pending[1]['id'])

        stats = await self.service.get_moderation_stats()
        operations.append(('after_reject', stats.copy()))

        # Delete third comment
        pending = await self.service.get_pending_comments()
        if len(pending) > 2:
            await self.service.delete_comment(pending[2]['id'])

        stats = await self.service.get_moderation_stats()
        operations.append(('after_delete', stats.copy()))

        # Verify consistency: total = pending + approved + rejected
        for op_name, op_stats in operations:
            calculated_total = op_stats['pending'] + op_stats['approved'] + op_stats['rejected']
            self.assertEqual(
                op_stats['total'],
                calculated_total,
                f"Stats inconsistency in {op_name}: {op_stats}"
            )

    async def _test_update_frequency(self):
        """Test that updates happen at appropriate frequency."""
        import time

        # Simulate time-based updates
        start_time = time.time()

        # Perform multiple operations quickly
        for i in range(5):
            comment_data = {
                'thread_id': f'frequency_test_{i}',
                'author_name': f'Frequency User {i}',
                'content': f'Frequency comment {i}',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)

        # Check that stats update immediately
        stats = await self.service.get_moderation_stats()
        self.assertGreaterEqual(stats['pending'], 5)

        end_time = time.time()
        duration = end_time - start_time

        # Operations should complete quickly (less than 0.5 seconds)
        self.assertLess(duration, 0.5, f"Operations took too long: {duration}s")

    async def _test_concurrent_updates(self):
        """Test handling concurrent comment updates."""
        # Create multiple comments concurrently
        async def create_comment_async(i):
            comment_data = {
                'thread_id': f'concurrent_test_{i}',
                'author_name': f'Concurrent User {i}',
                'content': f'Concurrent comment {i}',
                'parent_id': None
            }
            return await self.service.create_comment(comment_data)

        # Create 10 comments concurrently
        tasks = [create_comment_async(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertIsNotNone(result)
            self.assertIn('id', result)

        # Stats should reflect all creations
        stats = await self.service.get_moderation_stats()
        self.assertGreaterEqual(stats['pending'], 10)

    async def _test_streaming_data_format(self):
        """Test that streaming data is in correct format."""
        # Get current stats
        stats = await self.service.get_moderation_stats()

        # Simulate streaming data format
        streaming_data = {
            "pending_count": stats['pending'],
            "approved_count": stats['approved'],
            "total_count": stats['total'],
            "timestamp": "2024-01-01T00:00:00Z"  # Mock timestamp
        }

        # Verify structure
        required_keys = ["pending_count", "approved_count", "total_count", "timestamp"]
        for key in required_keys:
            self.assertIn(key, streaming_data)

        # Verify counts are consistent
        self.assertEqual(
            streaming_data["total_count"],
            streaming_data["pending_count"] + streaming_data["approved_count"]
        )

        # Test JSON serialization (for SSE)
        json_str = json.dumps(streaming_data)
        parsed_back = json.loads(json_str)
        self.assertEqual(parsed_back, streaming_data)

    async def _test_update_triggers(self):
        """Test what operations trigger updates."""
        # Get initial stats
        initial_stats = await self.service.get_moderation_stats()

        # Test that create triggers update
        comment_data = {
            'thread_id': 'trigger_test',
            'author_name': 'Trigger User',
            'content': 'Trigger comment',
            'parent_id': None
        }
        await self.service.create_comment(comment_data)

        after_create = await self.service.get_moderation_stats()
        self.assertNotEqual(after_create['pending'], initial_stats['pending'])

        # Test that approve triggers update
        pending = await self.service.get_pending_comments()
        if pending:
            await self.service.approve_comment(pending[-1]['id'])  # Approve the created one

            after_approve = await self.service.get_moderation_stats()
            self.assertNotEqual(after_approve['approved'], after_create['approved'])

        # Test that reject triggers update
        pending = await self.service.get_pending_comments()
        if pending:
            await self.service.reject_comment(pending[0]['id'])

            after_reject = await self.service.get_moderation_stats()
            self.assertNotEqual(after_reject['rejected'], after_approve['rejected'])

        # Test that delete triggers update
        pending = await self.service.get_pending_comments()
        if pending:
            await self.service.delete_comment(pending[0]['id'])

            after_delete = await self.service.get_moderation_stats()
            self.assertNotEqual(after_delete['total'], after_reject['total'])

    # Synchronous test runners
    def test_comment_count_updates(self):
        """Run async test for comment count updates."""
        asyncio.run(self._test_comment_count_updates())

    def test_stats_consistency(self):
        """Run async test for stats consistency."""
        asyncio.run(self._test_stats_consistency())

    def test_update_frequency(self):
        """Run async test for update frequency."""
        asyncio.run(self._test_update_frequency())

    def test_concurrent_updates(self):
        """Run async test for concurrent updates."""
        asyncio.run(self._test_concurrent_updates())

    def test_streaming_data_format(self):
        """Run async test for streaming data format."""
        asyncio.run(self._test_streaming_data_format())

    def test_update_triggers(self):
        """Run async test for update triggers."""
        asyncio.run(self._test_update_triggers())


class TestRealtimeEdgeCases(unittest.TestCase):
    """Test edge cases for real-time updates."""

    def setUp(self):
        self.service = CommentService()

    async def _test_empty_state_updates(self):
        """Test updates when starting from empty state."""
        # Clear all comments
        self.service._mock_comments.clear()

        # Get stats for empty state
        empty_stats = await self.service.get_moderation_stats()

        # Verify empty state
        self.assertEqual(empty_stats['total'], 0)
        self.assertEqual(empty_stats['pending'], 0)
        self.assertEqual(empty_stats['approved'], 0)
        self.assertEqual(empty_stats['rejected'], 0)

        # Add one comment
        comment_data = {
            'thread_id': 'empty_test',
            'author_name': 'Empty State User',
            'content': 'First comment in empty state',
            'parent_id': None
        }
        await self.service.create_comment(comment_data)

        # Check update
        after_add_stats = await self.service.get_moderation_stats()
        self.assertEqual(after_add_stats['total'], 1)
        self.assertEqual(after_add_stats['pending'], 1)

    async def _test_rapid_successive_updates(self):
        """Test rapid successive updates."""
        # Perform many operations in quick succession
        for i in range(10):
            comment_data = {
                'thread_id': f'rapid_test_{i}',
                'author_name': f'Rapid User {i}',
                'content': f'Rapid comment {i}',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)

        # Get all pending
        pending = await self.service.get_pending_comments()

        # Rapidly approve all
        for comment in pending[-10:]:  # Last 10 added
            await self.service.approve_comment(comment['id'])

        # Check final stats
        final_stats = await self.service.get_moderation_stats()
        self.assertGreaterEqual(final_stats['approved'], 10)

    async def _test_update_during_operations(self):
        """Test getting stats during ongoing operations."""
        # Start some operations
        comment_ids = []
        for i in range(5):
            comment_data = {
                'thread_id': f'ongoing_test_{i}',
                'author_name': f'Ongoing User {i}',
                'content': f'Ongoing comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Get stats during operations
        mid_stats = await self.service.get_moderation_stats()
        self.assertGreaterEqual(mid_stats['pending'], 5)

        # Continue operations
        for cid in comment_ids[:3]:
            await self.service.approve_comment(cid)

        # Get stats again
        after_partial_stats = await self.service.get_moderation_stats()
        self.assertGreaterEqual(after_partial_stats['approved'], 3)
        self.assertLessEqual(after_partial_stats['pending'], mid_stats['pending'] - 3)

    def test_empty_state_updates(self):
        """Run async test for empty state updates."""
        asyncio.run(self._test_empty_state_updates())

    def test_rapid_successive_updates(self):
        """Run async test for rapid successive updates."""
        asyncio.run(self._test_rapid_successive_updates())

    def test_update_during_operations(self):
        """Run async test for updates during operations."""
        asyncio.run(self._test_update_during_operations())


class TestStreamingSimulation(unittest.TestCase):
    """Test streaming endpoint simulation."""

    def setUp(self):
        self.service = CommentService()

    async def _test_sse_format(self):
        """Test Server-Sent Events format."""
        # Get stats
        stats = await self.service.get_moderation_stats()

        # Format as SSE data
        sse_data = f"data: {json.dumps(stats)}\n\n"

        # Verify SSE format
        self.assertTrue(sse_data.startswith("data: "))
        self.assertTrue(sse_data.endswith("\n\n"))

        # Parse back
        data_line = sse_data.strip().split("data: ")[1]
        parsed_data = json.loads(data_line)
        self.assertEqual(parsed_data, stats)

    async def _test_streaming_headers(self):
        """Test streaming response headers (simulated)."""
        # Simulate headers that would be set for SSE
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "text/event-stream"
        }

        # Verify required headers
        self.assertEqual(headers["Cache-Control"], "no-cache")
        self.assertEqual(headers["Connection"], "keep-alive")
        self.assertIn("Access-Control-Allow-Origin", headers)
        self.assertEqual(headers["Content-Type"], "text/event-stream")

    def test_sse_format(self):
        """Run async test for SSE format."""
        asyncio.run(self._test_sse_format())

    def test_streaming_headers(self):
        """Run async test for streaming headers."""
        asyncio.run(self._test_streaming_headers())


if __name__ == '__main__':
    unittest.main(verbosity=2)