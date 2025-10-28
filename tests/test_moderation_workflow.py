"""
Integration tests for comment moderation workflow.
Tests the complete moderation process from submission to approval/rejection.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.comment_service import CommentService


class TestModerationWorkflow(unittest.TestCase):
    """Test the complete comment moderation workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = CommentService()
        # Reset mock data
        self.service._mock_comments = self.service._initialize_mock_data()

    async def _test_full_moderation_workflow(self):
        """Test complete workflow: create -> pending -> approve."""
        # Step 1: Create a new comment
        comment_data = {
            'thread_id': 'workflow_test',
            'author_name': 'Workflow User',
            'content': 'This comment needs moderation',
            'parent_id': None
        }

        comment = await self.service.create_comment(comment_data)
        comment_id = comment['id']

        # Verify comment is created and pending
        self.assertEqual(comment['is_approved'], 0)
        self.assertEqual(comment['author_name'], 'Workflow User')

        # Step 2: Check that it appears in pending comments
        pending = await self.service.get_pending_comments()
        pending_ids = [c['id'] for c in pending]
        self.assertIn(comment_id, pending_ids)

        # Step 3: Approve the comment
        success = await self.service.approve_comment(comment_id)
        self.assertTrue(success)

        # Step 4: Verify comment is now approved
        updated_comment = await self.service.get_comment(comment_id)
        self.assertEqual(updated_comment['is_approved'], 1)

        # Step 5: Check that it no longer appears in pending
        pending_after = await self.service.get_pending_comments()
        pending_ids_after = [c['id'] for c in pending_after]
        self.assertNotIn(comment_id, pending_ids_after)

        # Step 6: Check that it appears in approved comments
        approved = await self.service.get_approved_comments()
        approved_ids = [c['id'] for c in approved]
        self.assertIn(comment_id, approved_ids)

    async def _test_rejection_workflow(self):
        """Test rejection workflow."""
        # Create comment
        comment_data = {
            'thread_id': 'rejection_test',
            'author_name': 'Bad User',
            'content': 'Inappropriate content',
            'parent_id': None
        }

        comment = await self.service.create_comment(comment_data)
        comment_id = comment['id']

        # Reject the comment
        success = await self.service.reject_comment(comment_id)
        self.assertTrue(success)

        # Verify rejection
        updated_comment = await self.service.get_comment(comment_id)
        self.assertEqual(updated_comment['is_approved'], 2)

        # Check rejected list
        rejected = await self.service.get_rejected_comments()
        rejected_ids = [c['id'] for c in rejected]
        self.assertIn(comment_id, rejected_ids)

    async def _test_bulk_moderation_workflow(self):
        """Test bulk moderation operations."""
        # Create multiple comments
        comment_ids = []
        for i in range(5):
            comment_data = {
                'thread_id': f'bulk_test_{i}',
                'author_name': f'User {i}',
                'content': f'Comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Bulk approve first 3
        approve_ids = comment_ids[:3]
        results = []
        for cid in approve_ids:
            success = await self.service.approve_comment(cid)
            results.append(success)

        self.assertTrue(all(results))

        # Bulk reject next 2
        reject_ids = comment_ids[3:]
        results = []
        for cid in reject_ids:
            success = await self.service.reject_comment(cid)
            results.append(success)

        self.assertTrue(all(results))

        # Verify final state
        for cid in approve_ids:
            comment = await self.service.get_comment(cid)
            self.assertEqual(comment['is_approved'], 1)

        for cid in reject_ids:
            comment = await self.service.get_comment(cid)
            self.assertEqual(comment['is_approved'], 2)

        # Check stats
        stats = await self.service.get_moderation_stats()
        self.assertGreaterEqual(stats['approved'], 3)
        self.assertGreaterEqual(stats['rejected'], 2)

    async def _test_threaded_comment_moderation(self):
        """Test moderation of threaded comments."""
        # Create parent comment
        parent_data = {
            'thread_id': 'thread_test',
            'author_name': 'Parent User',
            'content': 'Parent comment',
            'parent_id': None
        }
        parent = await self.service.create_comment(parent_data)

        # Create reply
        reply_data = {
            'thread_id': 'thread_test',
            'author_name': 'Reply User',
            'content': 'Reply to parent',
            'parent_id': parent['id']
        }
        reply = await self.service.create_comment(reply_data)

        # Approve parent
        await self.service.approve_comment(parent['id'])

        # Reject reply
        await self.service.reject_comment(reply['id'])

        # Get threaded comments
        threaded = await self.service.get_threaded_comments('thread_test')

        # Find parent in threaded structure
        parent_comment = None
        reply_comment = None

        for comment in threaded:
            if comment['id'] == parent['id']:
                parent_comment = comment
            if comment['id'] == reply['id']:
                reply_comment = comment

        self.assertIsNotNone(parent_comment)
        self.assertIsNotNone(reply_comment)

        # Verify moderation states
        self.assertEqual(parent_comment['is_approved'], 1)  # Approved
        self.assertEqual(reply_comment['is_approved'], 2)   # Rejected

    async def _test_moderation_stats_accuracy(self):
        """Test that moderation stats are accurate throughout workflow."""
        initial_stats = await self.service.get_moderation_stats()

        # Create several comments
        created_ids = []
        for i in range(10):
            comment_data = {
                'thread_id': f'stats_test_{i}',
                'author_name': f'Stats User {i}',
                'content': f'Stats comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            created_ids.append(comment['id'])

        # Check stats after creation
        after_create_stats = await self.service.get_moderation_stats()
        self.assertEqual(after_create_stats['pending'], initial_stats['pending'] + 10)
        self.assertEqual(after_create_stats['total'], initial_stats['total'] + 10)

        # Approve half
        approve_ids = created_ids[:5]
        for cid in approve_ids:
            await self.service.approve_comment(cid)

        # Reject quarter
        reject_ids = created_ids[5:7]
        for cid in reject_ids:
            await self.service.reject_comment(cid)

        # Final stats check
        final_stats = await self.service.get_moderation_stats()
        expected_pending = initial_stats['pending'] + 10 - 5 - 2  # Created - approved - rejected
        expected_approved = initial_stats['approved'] + 5
        expected_rejected = initial_stats['rejected'] + 2

        self.assertEqual(final_stats['pending'], expected_pending)
        self.assertEqual(final_stats['approved'], expected_approved)
        self.assertEqual(final_stats['rejected'], expected_rejected)
        self.assertEqual(final_stats['total'], initial_stats['total'] + 10)

    async def _test_moderation_state_transitions(self):
        """Test valid and invalid state transitions."""
        # Create comment
        comment_data = {
            'thread_id': 'transition_test',
            'author_name': 'Transition User',
            'content': 'Transition test comment',
            'parent_id': None
        }
        comment = await self.service.create_comment(comment_data)
        comment_id = comment['id']

        # Valid transitions
        # Pending -> Approved
        success = await self.service.approve_comment(comment_id)
        self.assertTrue(success)

        # Approved -> Can't approve again
        success = await self.service.approve_comment(comment_id)
        self.assertFalse(success)

        # Create another comment for rejection test
        comment2_data = {
            'thread_id': 'transition_test2',
            'author_name': 'Transition User2',
            'content': 'Transition test comment 2',
            'parent_id': None
        }
        comment2 = await self.service.create_comment(comment2_data)
        comment2_id = comment2['id']

        # Pending -> Rejected
        success = await self.service.reject_comment(comment2_id)
        self.assertTrue(success)

        # Rejected -> Can't reject again
        success = await self.service.reject_comment(comment2_id)
        self.assertFalse(success)

    # Synchronous test runners
    def test_full_moderation_workflow(self):
        """Run async test for full moderation workflow."""
        asyncio.run(self._test_full_moderation_workflow())

    def test_rejection_workflow(self):
        """Run async test for rejection workflow."""
        asyncio.run(self._test_rejection_workflow())

    def test_bulk_moderation_workflow(self):
        """Run async test for bulk moderation workflow."""
        asyncio.run(self._test_bulk_moderation_workflow())

    def test_threaded_comment_moderation(self):
        """Run async test for threaded comment moderation."""
        asyncio.run(self._test_threaded_comment_moderation())

    def test_moderation_stats_accuracy(self):
        """Run async test for moderation stats accuracy."""
        asyncio.run(self._test_moderation_stats_accuracy())

    def test_moderation_state_transitions(self):
        """Run async test for moderation state transitions."""
        asyncio.run(self._test_moderation_state_transitions())


class TestModerationEdgeCases(unittest.TestCase):
    """Test edge cases in moderation workflow."""

    def setUp(self):
        self.service = CommentService()

    async def _test_empty_moderation_queue(self):
        """Test behavior when moderation queue is empty."""
        # Clear all comments
        self.service._mock_comments.clear()

        pending = await self.service.get_pending_comments()
        approved = await self.service.get_approved_comments()
        rejected = await self.service.get_rejected_comments()

        self.assertEqual(len(pending), 0)
        self.assertEqual(len(approved), 0)
        self.assertEqual(len(rejected), 0)

        stats = await self.service.get_moderation_stats()
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['pending'], 0)
        self.assertEqual(stats['approved'], 0)
        self.assertEqual(stats['rejected'], 0)

    async def _test_moderation_with_high_volume(self):
        """Test moderation with high volume of comments."""
        # Create many comments
        comment_ids = []
        for i in range(100):
            comment_data = {
                'thread_id': f'high_volume_{i % 10}',  # 10 different threads
                'author_name': f'User {i}',
                'content': f'High volume comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Bulk approve first 50
        approve_ids = comment_ids[:50]
        for cid in approve_ids:
            await self.service.approve_comment(cid)

        # Bulk reject next 30
        reject_ids = comment_ids[50:80]
        for cid in reject_ids:
            await self.service.reject_comment(cid)

        # Leave last 20 pending

        # Verify counts
        stats = await self.service.get_moderation_stats()
        self.assertEqual(stats['total'], 100)
        self.assertGreaterEqual(stats['approved'], 50)
        self.assertGreaterEqual(stats['rejected'], 30)
        self.assertGreaterEqual(stats['pending'], 20)

        # Test pagination
        pending_page1 = await self.service.get_pending_comments(limit=10, offset=0)
        pending_page2 = await self.service.get_pending_comments(limit=10, offset=10)

        self.assertEqual(len(pending_page1), 10)
        self.assertEqual(len(pending_page2), 10)

    def test_empty_moderation_queue(self):
        """Run async test for empty moderation queue."""
        asyncio.run(self._test_empty_moderation_queue())

    def test_moderation_with_high_volume(self):
        """Run async test for high volume moderation."""
        asyncio.run(self._test_moderation_with_high_volume())


if __name__ == '__main__':
    unittest.main(verbosity=2)