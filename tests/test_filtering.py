"""
Tests for filtering functionality in comment moderation.
Tests status filtering, pagination, and search capabilities.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.comment_service import CommentService


class TestFilteringFunctionality(unittest.TestCase):
    """Test filtering and search functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = CommentService()
        # Reset mock data
        self.service._mock_comments = self.service._initialize_mock_data()

    async def _test_status_filtering(self):
        """Test filtering comments by status."""
        # Get all pending comments
        pending = await self.service.get_pending_comments()
        pending_count = len(pending)

        # Get all approved comments
        approved = await self.service.get_approved_comments()
        approved_count = len(approved)

        # Get all rejected comments
        rejected = await self.service.get_rejected_comments()
        rejected_count = len(rejected)

        # Verify counts add up to total
        total = pending_count + approved_count + rejected_count
        stats = await self.service.get_moderation_stats()
        self.assertEqual(total, stats['total'])

        # Verify each list contains only correct status
        for comment in pending:
            self.assertEqual(comment['is_approved'], 0)

        for comment in approved:
            self.assertEqual(comment['is_approved'], 1)

        for comment in rejected:
            self.assertEqual(comment['is_approved'], 2)

    async def _test_pagination(self):
        """Test pagination functionality."""
        # Create many comments for pagination testing
        for i in range(20):
            comment_data = {
                'thread_id': f'pagination_test_{i}',
                'author_name': f'Pagination User {i}',
                'content': f'Pagination comment {i}',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)

        # Test pagination on pending comments
        page1 = await self.service.get_pending_comments(limit=5, offset=0)
        page2 = await self.service.get_pending_comments(limit=5, offset=5)
        page3 = await self.service.get_pending_comments(limit=5, offset=10)

        # Each page should have 5 items
        self.assertEqual(len(page1), 5)
        self.assertEqual(len(page2), 5)
        self.assertEqual(len(page3), 5)

        # Pages should be different
        page1_ids = [c['id'] for c in page1]
        page2_ids = [c['id'] for c in page2]
        page3_ids = [c['id'] for c in page3]

        self.assertTrue(set(page1_ids).isdisjoint(set(page2_ids)))
        self.assertTrue(set(page1_ids).isdisjoint(set(page3_ids)))
        self.assertTrue(set(page2_ids).isdisjoint(set(page3_ids)))

        # Test edge case: offset beyond available data
        empty_page = await self.service.get_pending_comments(limit=5, offset=100)
        self.assertEqual(len(empty_page), 0)

    async def _test_thread_filtering(self):
        """Test filtering comments by thread."""
        # Create comments in different threads
        threads = ['thread_a', 'thread_b', 'thread_c']
        comments_per_thread = 3

        created_comments = {}
        for thread_id in threads:
            created_comments[thread_id] = []
            for i in range(comments_per_thread):
                comment_data = {
                    'thread_id': thread_id,
                    'author_name': f'Thread User {thread_id}_{i}',
                    'content': f'Comment in {thread_id}',
                    'parent_id': None
                }
                comment = await self.service.create_comment(comment_data)
                created_comments[thread_id].append(comment['id'])

        # Test threaded comment retrieval
        for thread_id in threads:
            threaded_comments = await self.service.get_threaded_comments(thread_id)
            # Should have exactly comments_per_thread comments
            self.assertEqual(len(threaded_comments), comments_per_thread)

            # All comments should be in the correct thread
            for comment in threaded_comments:
                self.assertEqual(comment['thread_referencia_id'], thread_id)

        # Test empty thread
        empty_thread = await self.service.get_threaded_comments('nonexistent_thread')
        self.assertEqual(len(empty_thread), 0)

    async def _test_date_based_filtering(self):
        """Test filtering by date ranges (simulated)."""
        from datetime import datetime, timedelta

        # Create comments at different times (simulate by setting created_at)
        base_time = datetime.now()

        # Comment 1: 2 hours ago
        comment1_data = {
            'thread_id': 'date_test',
            'author_name': 'Old User',
            'content': 'Old comment',
            'parent_id': None
        }
        comment1 = await self.service.create_comment(comment1_data)
        # Manually set older timestamp
        comment1['created_at'] = (base_time - timedelta(hours=2)).isoformat()
        await self.service.update_comment(comment1['id'], {'created_at': comment1['created_at']})

        # Comment 2: 1 hour ago
        comment2_data = {
            'thread_id': 'date_test',
            'author_name': 'Recent User',
            'content': 'Recent comment',
            'parent_id': None
        }
        comment2 = await self.service.create_comment(comment2_data)
        comment2['created_at'] = (base_time - timedelta(hours=1)).isoformat()
        await self.service.update_comment(comment2['id'], {'created_at': comment2['created_at']})

        # Comment 3: just now
        comment3_data = {
            'thread_id': 'date_test',
            'author_name': 'New User',
            'content': 'New comment',
            'parent_id': None
        }
        comment3 = await self.service.create_comment(comment3_data)

        # Get all comments for thread
        all_comments = await self.service.get_threaded_comments('date_test')

        # Sort by creation time (most recent first)
        sorted_comments = sorted(all_comments, key=lambda x: x['created_at'], reverse=True)

        # Verify order: comment3 (newest), comment2, comment1 (oldest)
        self.assertEqual(sorted_comments[0]['author_name'], 'New User')
        self.assertEqual(sorted_comments[1]['author_name'], 'Recent User')
        self.assertEqual(sorted_comments[2]['author_name'], 'Old User')

    async def _test_author_filtering(self):
        """Test filtering by author (simulated search)."""
        # Create comments from different authors
        authors = ['Alice', 'Bob', 'Charlie', 'Alice']  # Alice has 2 comments

        for i, author in enumerate(authors):
            comment_data = {
                'thread_id': 'author_test',
                'author_name': author,
                'content': f'Comment by {author} {i}',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)

        # Get all comments for thread
        all_comments = await self.service.get_threaded_comments('author_test')

        # Filter by author manually (since service doesn't have built-in author filtering)
        alice_comments = [c for c in all_comments if c['author_name'] == 'Alice']
        bob_comments = [c for c in all_comments if c['author_name'] == 'Bob']
        charlie_comments = [c for c in all_comments if c['author_name'] == 'Charlie']

        self.assertEqual(len(alice_comments), 2)
        self.assertEqual(len(bob_comments), 1)
        self.assertEqual(len(charlie_comments), 1)

        # Verify content
        for comment in alice_comments:
            self.assertIn('Comment by Alice', comment['content'])

    async def _test_content_filtering(self):
        """Test content-based filtering (simulated search)."""
        # Create comments with specific keywords
        keywords = ['urgent', 'question', 'feedback', 'bug', 'urgent']

        for keyword in keywords:
            comment_data = {
                'thread_id': 'content_test',
                'author_name': f'User with {keyword}',
                'content': f'This is a {keyword} comment that needs attention',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)

        # Get all comments
        all_comments = await self.service.get_threaded_comments('content_test')

        # Filter by keyword manually
        urgent_comments = [c for c in all_comments if 'urgent' in c['content'].lower()]
        question_comments = [c for c in all_comments if 'question' in c['content'].lower()]
        feedback_comments = [c for c in all_comments if 'feedback' in c['content'].lower()]

        self.assertEqual(len(urgent_comments), 2)  # Two urgent comments
        self.assertEqual(len(question_comments), 1)
        self.assertEqual(len(feedback_comments), 1)

    async def _test_combined_filters(self):
        """Test combining multiple filters."""
        # Create diverse comments
        test_comments = [
            {'thread': 'combined_test', 'author': 'Alice', 'content': 'Approved feedback', 'status': 1},
            {'thread': 'combined_test', 'author': 'Bob', 'content': 'Pending question', 'status': 0},
            {'thread': 'combined_test', 'author': 'Alice', 'content': 'Rejected bug report', 'status': 2},
            {'thread': 'combined_test', 'author': 'Charlie', 'content': 'Pending feedback', 'status': 0},
            {'thread': 'other_thread', 'author': 'Alice', 'content': 'Other thread comment', 'status': 0},
        ]

        for test_comment in test_comments:
            comment_data = {
                'thread_id': test_comment['thread'],
                'author_name': test_comment['author'],
                'content': test_comment['content'],
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)

            # Set status
            if test_comment['status'] == 1:
                await self.service.approve_comment(comment['id'])
            elif test_comment['status'] == 2:
                await self.service.reject_comment(comment['id'])

        # Test combined filtering: pending comments by Alice in combined_test thread
        all_pending = await self.service.get_pending_comments()
        combined_test_pending = [c for c in all_pending if c['thread_referencia_id'] == 'combined_test']
        alice_pending_combined = [c for c in combined_test_pending if c['author_name'] == 'Alice']

        # Should find Charlie's pending feedback (Alice's is approved)
        self.assertEqual(len(alice_pending_combined), 0)  # Alice has no pending in this thread

        # Charlie's pending feedback should be found
        charlie_pending_combined = [c for c in combined_test_pending if c['author_name'] == 'Charlie']
        self.assertEqual(len(charlie_pending_combined), 1)
        self.assertIn('feedback', charlie_pending_combined[0]['content'])

    # Synchronous test runners
    def test_status_filtering(self):
        """Run async test for status filtering."""
        asyncio.run(self._test_status_filtering())

    def test_pagination(self):
        """Run async test for pagination."""
        asyncio.run(self._test_pagination())

    def test_thread_filtering(self):
        """Run async test for thread filtering."""
        asyncio.run(self._test_thread_filtering())

    def test_date_based_filtering(self):
        """Run async test for date-based filtering."""
        asyncio.run(self._test_date_based_filtering())

    def test_author_filtering(self):
        """Run async test for author filtering."""
        asyncio.run(self._test_author_filtering())

    def test_content_filtering(self):
        """Run async test for content filtering."""
        asyncio.run(self._test_content_filtering())

    def test_combined_filters(self):
        """Run async test for combined filters."""
        asyncio.run(self._test_combined_filters())


class TestFilteringEdgeCases(unittest.TestCase):
    """Test edge cases for filtering functionality."""

    def setUp(self):
        self.service = CommentService()

    async def _test_empty_results_filtering(self):
        """Test filtering when no results match."""
        # Clear all comments
        self.service._mock_comments.clear()

        # Test all filter types return empty
        pending = await self.service.get_pending_comments()
        approved = await self.service.get_approved_comments()
        rejected = await self.service.get_rejected_comments()
        threaded = await self.service.get_threaded_comments('any_thread')

        self.assertEqual(len(pending), 0)
        self.assertEqual(len(approved), 0)
        self.assertEqual(len(rejected), 0)
        self.assertEqual(len(threaded), 0)

    async def _test_pagination_edge_cases(self):
        """Test pagination edge cases."""
        # Create exactly 7 comments
        for i in range(7):
            comment_data = {
                'thread_id': 'pagination_edge',
                'author_name': f'Edge User {i}',
                'content': f'Edge comment {i}',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)

        # Test limit larger than available
        large_limit = await self.service.get_pending_comments(limit=100, offset=0)
        self.assertEqual(len(large_limit), 7)

        # Test offset at boundary
        boundary_page = await self.service.get_pending_comments(limit=5, offset=5)
        self.assertEqual(len(boundary_page), 2)  # Should get remaining 2

        # Test offset beyond total
        beyond_total = await self.service.get_pending_comments(limit=5, offset=10)
        self.assertEqual(len(beyond_total), 0)

    async def _test_filter_consistency(self):
        """Test that filters remain consistent across operations."""
        # Create comments with known states
        initial_pending = await self.service.get_pending_comments()
        initial_count = len(initial_pending)

        # Add more comments
        for i in range(3):
            comment_data = {
                'thread_id': 'consistency_test',
                'author_name': f'Consistency User {i}',
                'content': f'Consistency comment {i}',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)

        # Check counts again
        after_pending = await self.service.get_pending_comments()
        self.assertEqual(len(after_pending), initial_count + 3)

        # Approve one
        if after_pending:
            await self.service.approve_comment(after_pending[0]['id'])

            # Check counts after approval
            final_pending = await self.service.get_pending_comments()
            final_approved = await self.service.get_approved_comments()

            self.assertEqual(len(final_pending), len(after_pending) - 1)
            self.assertGreaterEqual(len(final_approved), 1)

    def test_empty_results_filtering(self):
        """Run async test for empty results filtering."""
        asyncio.run(self._test_empty_results_filtering())

    def test_pagination_edge_cases(self):
        """Run async test for pagination edge cases."""
        asyncio.run(self._test_pagination_edge_cases())

    def test_filter_consistency(self):
        """Run async test for filter consistency."""
        asyncio.run(self._test_filter_consistency())


if __name__ == '__main__':
    unittest.main(verbosity=2)