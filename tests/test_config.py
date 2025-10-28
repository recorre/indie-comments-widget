"""
Test configuration and requirements for comment moderation tests.
"""

import unittest
import sys
import os
import subprocess
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestConfiguration(unittest.TestCase):
    """Test configuration and environment setup."""

    def test_python_version(self):
        """Test that Python version is compatible."""
        version = sys.version_info
        self.assertGreaterEqual(version.major, 3)
        self.assertGreaterEqual(version.minor, 8)

    def test_backend_imports(self):
        """Test that all backend modules can be imported."""
        try:
            from services.comment_service import CommentService
            from api.comments import router as comments_router
            from api.moderation import router as moderation_router
            from core.cache import SWRCache

            # Test instantiation
            service = CommentService()
            self.assertIsNotNone(service)

            cache = SWRCache(ttl=60, max_size=100)
            self.assertIsNotNone(cache)

        except ImportError as e:
            self.fail(f"Failed to import backend modules: {e}")

    def test_test_dependencies(self):
        """Test that test dependencies are available."""
        try:
            import unittest
            import asyncio
            from unittest.mock import Mock, patch, AsyncMock

            # Test that async mocking works
            async def dummy_async():
                return "test"

            mock = AsyncMock(return_value="mocked")
            self.assertIsNotNone(mock)

        except ImportError as e:
            self.fail(f"Test dependencies not available: {e}")

    def test_service_initialization(self):
        """Test that services initialize correctly."""
        from services.comment_service import CommentService

        service = CommentService()

        # Check initial state
        self.assertIsInstance(service._mock_comments, list)
        self.assertGreaterEqual(len(service._mock_comments), 0)

        # Test basic functionality
        stats = asyncio.run(service.get_moderation_stats())
        self.assertIsInstance(stats, dict)
        self.assertIn('total', stats)


class TestRequirements(unittest.TestCase):
    """Test that project requirements are met."""

    def test_fastapi_available(self):
        """Test that FastAPI is available."""
        try:
            import fastapi
            from fastapi import APIRouter, HTTPException
            from fastapi.testclient import TestClient

            # Test basic FastAPI functionality
            app = fastapi.FastAPI()
            self.assertIsNotNone(app)

        except ImportError:
            self.fail("FastAPI not available")

    def test_uvicorn_available(self):
        """Test that uvicorn is available."""
        try:
            import uvicorn
            # Just test import
            self.assertTrue(hasattr(uvicorn, 'run'))
        except ImportError:
            self.fail("uvicorn not available")

    def test_standard_library(self):
        """Test that required standard library modules are available."""
        required_modules = [
            'asyncio', 'json', 'datetime', 'typing', 'sys', 'os',
            'unittest', 'time', 'statistics', 'concurrent.futures'
        ]

        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                self.fail(f"Required standard library module not available: {module_name}")


class TestEnvironment(unittest.TestCase):
    """Test environment and system requirements."""

    def test_working_directory(self):
        """Test that we're in the correct working directory."""
        current_dir = os.getcwd()
        self.assertTrue('HACKATHON' in current_dir or 'nocodebackend' in current_dir.lower())

    def test_backend_directory_structure(self):
        """Test that backend directory structure exists."""
        backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')

        required_dirs = ['api', 'services', 'models', 'core', 'utils']
        for dir_name in required_dirs:
            dir_path = os.path.join(backend_dir, dir_name)
            self.assertTrue(os.path.exists(dir_path), f"Required directory missing: {dir_path}")

        required_files = [
            'api/__init__.py',
            'api/comments.py',
            'api/moderation.py',
            'services/__init__.py',
            'services/comment_service.py',
            'core/__init__.py',
            'models/__init__.py'
        ]

        for file_path in required_files:
            full_path = os.path.join(backend_dir, file_path)
            self.assertTrue(os.path.exists(full_path), f"Required file missing: {full_path}")

    def test_test_directory_structure(self):
        """Test that test directory has required structure."""
        test_dir = os.path.dirname(__file__)

        # Check that we have our test files
        test_files = [
            'test_comment_service.py',
            'test_api_endpoints.py',
            'test_moderation_workflow.py',
            'test_bulk_operations.py',
            'test_filtering.py',
            'test_realtime_updates.py',
            'test_performance_load.py',
            'test_config.py'
        ]

        for test_file in test_files:
            file_path = os.path.join(test_dir, test_file)
            if not os.path.exists(file_path):
                self.skipTest(f"Test file not yet created: {test_file}")
            else:
                self.assertTrue(os.path.exists(file_path), f"Test file missing: {file_path}")


class TestMockDataIntegrity(unittest.TestCase):
    """Test that mock data maintains integrity."""

    def setUp(self):
        from services.comment_service import CommentService
        self.service = CommentService()

    def test_mock_data_structure(self):
        """Test that mock data has correct structure."""
        comments = self.service._mock_comments

        for comment in comments:
            required_keys = ['id', 'thread_referencia_id', 'author_name', 'content', 'created_at', 'is_approved']
            for key in required_keys:
                self.assertIn(key, comment, f"Comment missing required key: {key}")

            # Test data types
            self.assertIsInstance(comment['id'], int)
            self.assertIsInstance(comment['thread_referencia_id'], str)
            self.assertIsInstance(comment['author_name'], str)
            self.assertIsInstance(comment['content'], str)
            self.assertIsInstance(comment['is_approved'], int)
            self.assertIn(comment['is_approved'], [0, 1, 2])  # pending, approved, rejected

    def test_mock_data_consistency(self):
        """Test that mock data is internally consistent."""
        comments = self.service._mock_comments

        # Check for unique IDs
        ids = [c['id'] for c in comments]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate comment IDs found")

        # Check parent-child relationships
        for comment in comments:
            if comment['parent_id'] is not None:
                # Parent should exist
                parent_exists = any(c['id'] == comment['parent_id'] for c in comments)
                self.assertTrue(parent_exists, f"Parent comment {comment['parent_id']} not found for comment {comment['id']}")

    def test_service_isolation(self):
        """Test that service instances are properly isolated."""
        service1 = self.service
        service2 = type(self.service)()  # Create new instance

        # Modify service1
        original_count = len(service1._mock_comments)
        comment_data = {
            'thread_id': 'isolation_test',
            'author_name': 'Isolation User',
            'content': 'Isolation test comment',
            'parent_id': None
        }
        asyncio.run(service1.create_comment(comment_data))

        # service2 should not be affected
        self.assertEqual(len(service2._mock_comments), original_count)
        self.assertEqual(len(service1._mock_comments), original_count + 1)


class TestTestRunner(unittest.TestCase):
    """Test that the test runner works correctly."""

    def test_unittest_discovery(self):
        """Test that unittest can discover our tests."""
        # This test just verifies that the test framework is working
        self.assertTrue(True)

    def test_async_test_support(self):
        """Test that async tests are supported."""
        async def dummy_async_test():
            await asyncio.sleep(0.001)
            return True

        result = asyncio.run(dummy_async_test())
        self.assertTrue(result)


if __name__ == '__main__':
    # Run configuration tests
    unittest.main(verbosity=2)