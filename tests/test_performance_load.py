"""
Performance and load tests for comment moderation system.
Tests system performance under various loads and conditions.
"""

import unittest
import asyncio
import time
import statistics
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import concurrent.futures

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.comment_service import CommentService


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics and benchmarks."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = CommentService()
        # Reset mock data for clean tests
        self.service._mock_comments = self.service._initialize_mock_data()

    async def _test_operation_timings(self):
        """Test timing of basic operations."""
        timings = {
            'create': [],
            'read': [],
            'update': [],
            'delete': []
        }

        # Test create performance
        for i in range(10):
            start_time = time.time()
            comment_data = {
                'thread_id': f'perf_test_{i}',
                'author_name': f'Perf User {i}',
                'content': f'Performance test comment {i}',
                'parent_id': None
            }
            await self.service.create_comment(comment_data)
            end_time = time.time()
            timings['create'].append(end_time - start_time)

        # Test read performance
        comment_ids = []
        for i in range(10):
            pending = await self.service.get_pending_comments()
            if pending:
                comment_ids.append(pending[i]['id'])

        for comment_id in comment_ids:
            start_time = time.time()
            await self.service.get_comment(comment_id)
            end_time = time.time()
            timings['read'].append(end_time - start_time)

        # Test update performance
        for comment_id in comment_ids[:5]:
            start_time = time.time()
            await self.service.update_comment(comment_id, {'content': 'Updated content'})
            end_time = time.time()
            timings['update'].append(end_time - start_time)

        # Test delete performance
        for comment_id in comment_ids[5:]:
            start_time = time.time()
            await self.service.delete_comment(comment_id)
            end_time = time.time()
            timings['delete'].append(end_time - start_time)

        # Analyze timings
        for operation, times in timings.items():
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                min_time = min(times)

                # Operations should complete within reasonable time
                self.assertLess(avg_time, 0.1, f"Average {operation} time too slow: {avg_time}s")
                self.assertLess(max_time, 0.5, f"Max {operation} time too slow: {max_time}s")

                print(f"{operation.capitalize()}: avg={avg_time:.4f}s, min={min_time:.4f}s, max={max_time:.4f}s")

    async def _test_bulk_operation_performance(self):
        """Test performance of bulk operations."""
        # Create many comments for bulk testing
        comment_ids = []
        for i in range(50):
            comment_data = {
                'thread_id': f'bulk_perf_{i % 5}',  # 5 threads
                'author_name': f'Bulk User {i}',
                'content': f'Bulk performance comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Test bulk approve performance
        start_time = time.time()
        for comment_id in comment_ids:
            await self.service.approve_comment(comment_id)
        end_time = time.time()

        bulk_approve_time = end_time - start_time
        avg_approve_time = bulk_approve_time / len(comment_ids)

        # Bulk operations should be efficient
        self.assertLess(bulk_approve_time, 2.0, f"Bulk approve took too long: {bulk_approve_time}s")
        self.assertLess(avg_approve_time, 0.02, f"Average approve time too slow: {avg_approve_time}s")

        print(f"Bulk approve: total={bulk_approve_time:.4f}s, avg={avg_approve_time:.4f}s per comment")

    async def _test_concurrent_operations(self):
        """Test performance under concurrent operations."""
        async def concurrent_create(i):
            comment_data = {
                'thread_id': f'concurrent_perf_{i % 3}',
                'author_name': f'Concurrent User {i}',
                'content': f'Concurrent comment {i}',
                'parent_id': None
            }
            start_time = time.time()
            comment = await self.service.create_comment(comment_data)
            end_time = time.time()
            return end_time - start_time, comment

        # Run 20 concurrent creations
        start_total = time.time()
        results = await asyncio.gather(*[concurrent_create(i) for i in range(20)])
        end_total = time.time()

        total_time = end_total - start_total
        individual_times = [r[0] for r in results]

        avg_time = statistics.mean(individual_times)
        max_time = max(individual_times)

        # Concurrent operations should complete efficiently
        self.assertLess(total_time, 1.0, f"Concurrent operations took too long: {total_time}s")
        self.assertLess(avg_time, 0.05, f"Average concurrent time too slow: {avg_time}s")
        self.assertLess(max_time, 0.2, f"Max concurrent time too slow: {max_time}s")

        print(f"Concurrent creates: total={total_time:.4f}s, avg={avg_time:.4f}s, max={max_time:.4f}s")

    async def _test_memory_usage_simulation(self):
        """Test memory usage with large datasets (simulated)."""
        # Create a large number of comments
        large_dataset = []
        for i in range(200):
            comment_data = {
                'thread_id': f'memory_test_{i % 10}',
                'author_name': f'Memory User {i}',
                'content': f'Memory test comment {i} with some additional content to increase size',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            large_dataset.append(comment)

        # Test that operations still work with large dataset
        stats = await self.service.get_moderation_stats()
        self.assertGreaterEqual(stats['total'], 200)

        # Test filtering on large dataset
        pending = await self.service.get_pending_comments(limit=50)
        self.assertEqual(len(pending), 50)

        # Test threaded comments on large dataset
        for thread_id in [f'memory_test_{i}' for i in range(3)]:
            threaded = await self.service.get_threaded_comments(thread_id)
            self.assertGreaterEqual(len(threaded), 15)  # ~20 comments per thread

        print(f"Large dataset test: {len(large_dataset)} comments created successfully")

    async def _test_caching_performance(self):
        """Test performance with simulated caching."""
        # Create comments
        comment_ids = []
        for i in range(20):
            comment_data = {
                'thread_id': 'cache_perf',
                'author_name': f'Cache User {i}',
                'content': f'Cache performance comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            comment_ids.append(comment['id'])

        # Simulate repeated reads (cache hits would be faster)
        read_times = []
        for _ in range(5):
            for comment_id in comment_ids[:10]:  # Read first 10 repeatedly
                start_time = time.time()
                await self.service.get_comment(comment_id)
                end_time = time.time()
                read_times.append(end_time - start_time)

        avg_read_time = statistics.mean(read_times)

        # Reads should be fast
        self.assertLess(avg_read_time, 0.01, f"Average read time too slow: {avg_read_time}s")

        print(f"Repeated reads: avg={avg_read_time:.6f}s per read")

    # Synchronous test runners
    def test_operation_timings(self):
        """Run async test for operation timings."""
        asyncio.run(self._test_operation_timings())

    def test_bulk_operation_performance(self):
        """Run async test for bulk operation performance."""
        asyncio.run(self._test_bulk_operation_performance())

    def test_concurrent_operations(self):
        """Run async test for concurrent operations."""
        asyncio.run(self._test_concurrent_operations())

    def test_memory_usage_simulation(self):
        """Run async test for memory usage simulation."""
        asyncio.run(self._test_memory_usage_simulation())

    def test_caching_performance(self):
        """Run async test for caching performance."""
        asyncio.run(self._test_caching_performance())


class TestLoadTesting(unittest.TestCase):
    """Load testing for the comment system."""

    def setUp(self):
        self.service = CommentService()

    async def _test_high_load_creation(self):
        """Test creating comments under high load."""
        async def create_load(i):
            try:
                comment_data = {
                    'thread_id': f'load_test_{i % 20}',  # 20 threads
                    'author_name': f'Load User {i}',
                    'content': f'High load comment {i}',
                    'parent_id': None
                }
                return await self.service.create_comment(comment_data)
            except Exception as e:
                return f"Error: {e}"

        # Create 100 comments concurrently
        start_time = time.time()
        results = await asyncio.gather(*[create_load(i) for i in range(100)])
        end_time = time.time()

        total_time = end_time - start_time
        successful_creates = sum(1 for r in results if isinstance(r, dict) and 'id' in r)
        errors = sum(1 for r in results if isinstance(r, str) and r.startswith("Error"))

        # Should handle high load reasonably well
        self.assertLess(total_time, 5.0, f"High load creation took too long: {total_time}s")
        self.assertGreaterEqual(successful_creates, 95, f"Too many creation failures: {errors} errors")
        self.assertLess(errors, 5, f"Too many errors: {errors}")

        print(f"High load creation: {successful_creates} successes, {errors} errors, {total_time:.2f}s")

    async def _test_mixed_load_operations(self):
        """Test mixed read/write operations under load."""
        # First create a base set of comments
        base_ids = []
        for i in range(50):
            comment_data = {
                'thread_id': f'mixed_load_{i % 5}',
                'author_name': f'Base User {i}',
                'content': f'Base comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            base_ids.append(comment['id'])

        async def mixed_operation(i):
            try:
                if i % 4 == 0:
                    # Create
                    comment_data = {
                        'thread_id': 'mixed_load_dynamic',
                        'author_name': f'Mixed User {i}',
                        'content': f'Mixed comment {i}',
                        'parent_id': None
                    }
                    return 'create', await self.service.create_comment(comment_data)
                elif i % 4 == 1:
                    # Read
                    if base_ids:
                        comment = await self.service.get_comment(base_ids[i % len(base_ids)])
                        return 'read', comment
                elif i % 4 == 2:
                    # Update
                    if base_ids:
                        cid = base_ids[i % len(base_ids)]
                        success = await self.service.update_comment(cid, {'content': f'Updated {i}'})
                        return 'update', success
                else:
                    # Moderate
                    if base_ids:
                        cid = base_ids[i % len(base_ids)]
                        success = await self.service.approve_comment(cid)
                        return 'moderate', success
            except Exception as e:
                return 'error', str(e)

        # Run 80 mixed operations concurrently
        start_time = time.time()
        results = await asyncio.gather(*[mixed_operation(i) for i in range(80)])
        end_time = time.time()

        total_time = end_time - start_time

        operation_counts = {}
        for op_type, _ in results:
            operation_counts[op_type] = operation_counts.get(op_type, 0) + 1

        errors = operation_counts.get('error', 0)

        # Should handle mixed load
        self.assertLess(total_time, 3.0, f"Mixed load operations took too long: {total_time}s")
        self.assertLess(errors, 5, f"Too many errors in mixed load: {errors}")

        print(f"Mixed load: {total_time:.2f}s, operations: {operation_counts}")

    async def _test_sustained_load(self):
        """Test sustained load over time."""
        operation_times = []

        # Run operations for a short sustained period
        end_time = time.time() + 2  # 2 seconds of sustained load

        operation_count = 0
        while time.time() < end_time:
            start_op = time.time()

            # Alternate between create and read
            if operation_count % 2 == 0:
                comment_data = {
                    'thread_id': 'sustained_load',
                    'author_name': f'Sustained User {operation_count}',
                    'content': f'Sustained comment {operation_count}',
                    'parent_id': None
                }
                await self.service.create_comment(comment_data)
            else:
                stats = await self.service.get_moderation_stats()

            end_op = time.time()
            operation_times.append(end_op - start_op)
            operation_count += 1

        avg_operation_time = statistics.mean(operation_times)
        total_operations = len(operation_times)

        # Sustained load should maintain reasonable performance
        self.assertLess(avg_operation_time, 0.05, f"Average sustained operation time too slow: {avg_operation_time}s")
        self.assertGreater(total_operations, 50, f"Not enough operations in sustained test: {total_operations}")

        print(f"Sustained load: {total_operations} operations, avg={avg_operation_time:.4f}s per op")

    def test_high_load_creation(self):
        """Run async test for high load creation."""
        asyncio.run(self._test_high_load_creation())

    def test_mixed_load_operations(self):
        """Run async test for mixed load operations."""
        asyncio.run(self._test_mixed_load_operations())

    def test_sustained_load(self):
        """Run async test for sustained load."""
        asyncio.run(self._test_sustained_load())


class TestScalabilityMetrics(unittest.TestCase):
    """Test scalability metrics and thresholds."""

    def setUp(self):
        self.service = CommentService()

    async def _test_scaling_with_data_size(self):
        """Test how performance scales with data size."""
        sizes = [10, 50, 100, 200]
        performance_data = {}

        for size in sizes:
            # Clear and create specific number of comments
            self.service._mock_comments.clear()

            for i in range(size):
                comment_data = {
                    'thread_id': f'scale_test_{i % 5}',
                    'author_name': f'Scale User {i}',
                    'content': f'Scale comment {i}',
                    'parent_id': None
                }
                await self.service.create_comment(comment_data)

            # Measure operation times
            start_time = time.time()
            stats = await self.service.get_moderation_stats()
            pending = await self.service.get_pending_comments(limit=20)
            threaded = await self.service.get_threaded_comments('scale_test_0')
            end_time = time.time()

            operation_time = end_time - start_time
            performance_data[size] = {
                'time': operation_time,
                'stats': stats,
                'pending_count': len(pending),
                'threaded_count': len(threaded)
            }

            print(f"Size {size}: {operation_time:.4f}s")

        # Performance should degrade gracefully (not exponentially)
        times = [performance_data[size]['time'] for size in sizes]
        # Check that doubling size doesn't quadruple time (rough scalability test)
        if len(times) >= 2:
            ratio_10_to_50 = times[1] / times[0] if times[0] > 0 else float('inf')
            self.assertLess(ratio_10_to_50, 10, f"Poor scalability: 5x data, {ratio_10_to_50:.1f}x time")

    async def _test_thread_contention(self):
        """Test for thread contention issues (simulated)."""
        # Create shared resource scenario
        shared_comment_ids = []

        # Create initial comments
        for i in range(10):
            comment_data = {
                'thread_id': 'contention_test',
                'author_name': f'Contention User {i}',
                'content': f'Contention comment {i}',
                'parent_id': None
            }
            comment = await self.service.create_comment(comment_data)
            shared_comment_ids.append(comment['id'])

        async def contended_operation(task_id):
            """Simulate contended operations on shared data."""
            results = []
            for i in range(5):
                # Randomly select a comment to operate on
                target_id = shared_comment_ids[(task_id + i) % len(shared_comment_ids)]

                # Perform different operations
                if i % 3 == 0:
                    comment = await self.service.get_comment(target_id)
                    results.append(('read', comment is not None))
                elif i % 3 == 1:
                    success = await self.service.approve_comment(target_id)
                    results.append(('approve', success))
                else:
                    success = await self.service.update_comment(target_id, {'content': f'Updated by {task_id}'})
                    results.append(('update', success))

            return results

        # Run 5 concurrent tasks operating on shared data
        start_time = time.time()
        results = await asyncio.gather(*[contended_operation(i) for i in range(5)])
        end_time = time.time()

        total_time = end_time - start_time

        # Should handle contention reasonably
        self.assertLess(total_time, 1.0, f"Contended operations took too long: {total_time}s")

        # Count successful operations
        total_operations = sum(len(task_results) for task_results in results)
        successful_ops = sum(1 for task_results in results for _, success in task_results if success)

        success_rate = successful_ops / total_operations if total_operations > 0 else 0
        self.assertGreater(success_rate, 0.8, f"Low success rate under contention: {success_rate:.2%}")

        print(f"Contention test: {successful_ops}/{total_operations} successful, {total_time:.4f}s")

    def test_scaling_with_data_size(self):
        """Run async test for scaling with data size."""
        asyncio.run(self._test_scaling_with_data_size())

    def test_thread_contention(self):
        """Run async test for thread contention."""
        asyncio.run(self._test_thread_contention())


if __name__ == '__main__':
    unittest.main(verbosity=2)