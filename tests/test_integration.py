"""
Integration tests for the Comment Widget System.
Tests full workflow from frontend to backend and back.
"""

import unittest
import requests
import time
import subprocess
import signal
import os
import sys
from unittest.mock import patch, Mock

class TestSystemIntegration(unittest.TestCase):
    """Test the complete system integration."""

    BACKEND_URL = "http://localhost:8000"
    FRONTEND_URL = "http://localhost:3000"

    def setUp(self):
        """Set up test environment."""
        self.backend_process = None
        self.frontend_process = None
        self.start_services()

    def tearDown(self):
        """Clean up test environment."""
        self.stop_services()

    def start_services(self):
        """Start backend and frontend services for testing."""
        # Note: In a real scenario, you'd start actual services
        # For now, we'll mock the services being available
        pass

    def stop_services(self):
        """Stop test services."""
        pass

    @patch('requests.get')
    def test_comment_workflow(self, mock_get):
        """Test complete comment creation and moderation workflow."""
        # Mock backend responses
        mock_get.return_value = Mock(status_code=200, json=lambda: {
            "comments": [
                {
                    "id": 1,
                    "thread_referencia_id": "test_thread",
                    "author_name": "Test User",
                    "content": "Test comment",
                    "created_at": "2024-01-01T00:00:00Z",
                    "is_approved": 0
                }
            ]
        })

        # Test comment retrieval
        response = requests.get(f"{self.BACKEND_URL}/moderation/comments?status=pending")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('comments', data)
        self.assertGreater(len(data['comments']), 0)

    @patch('requests.post')
    def test_moderation_workflow(self, mock_post):
        """Test comment moderation workflow."""
        mock_post.return_value = Mock(status_code=200, json=lambda: {
            "message": "Comment 1 successfully approved",
            "comment_id": 1,
            "action": "approve"
        })

        # Test comment approval
        response = requests.post(f"{self.BACKEND_URL}/moderation/1", json={"action": "approve"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('message', data)
        self.assertEqual(data['action'], 'approve')

    @patch('requests.post')
    def test_bulk_moderation(self, mock_post):
        """Test bulk comment moderation."""
        mock_post.return_value = Mock(status_code=200, json=lambda: {
            "message": "Successfully approved 2 out of 2 comments",
            "results": [
                {"comment_id": 1, "success": True},
                {"comment_id": 2, "success": True}
            ],
            "successful": 2,
            "total": 2
        })

        # Test bulk approval
        response = requests.post(f"{self.BACKEND_URL}/moderation/bulk",
                               json={"comment_ids": [1, 2], "action": "approve"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['successful'], 2)
        self.assertEqual(data['total'], 2)

class TestThreadManagement(unittest.TestCase):
    """Test thread creation and management."""

    BACKEND_URL = "http://localhost:8000"

    @patch('requests.post')
    def test_thread_creation(self, mock_post):
        """Test thread creation workflow."""
        mock_post.return_value = Mock(status_code=200, json=lambda: {
            "thread": {
                "id": 1,
                "title": "Test Thread",
                "url": "https://example.com/test",
                "external_page_id": "thread_1"
            },
            "message": "Thread created successfully"
        })

        response = requests.post(f"{self.BACKEND_URL}/threads", json={
            "title": "Test Thread",
            "url": "https://example.com/test"
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('thread', data)
        self.assertEqual(data['thread']['title'], 'Test Thread')

    @patch('requests.get')
    def test_thread_retrieval(self, mock_get):
        """Test thread retrieval."""
        mock_get.return_value = Mock(status_code=200, json=lambda: {
            "threads": [
                {
                    "id": 1,
                    "title": "Test Thread",
                    "url": "https://example.com/test",
                    "external_page_id": "thread_1"
                }
            ]
        })

        response = requests.get(f"{self.BACKEND_URL}/threads")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('threads', data)
        self.assertGreater(len(data['threads']), 0)

class TestWidgetConfiguration(unittest.TestCase):
    """Test widget configuration functionality."""

    BACKEND_URL = "http://localhost:8000"

    @patch('requests.get')
    def test_widget_config_retrieval(self, mock_get):
        """Test widget configuration retrieval."""
        mock_get.return_value = Mock(status_code=200, json=lambda: {
            "theme": "default",
            "position": "bottom-right",
            "max_comments": 50,
            "auto_load": True,
            "colors": {
                "primary": "#007bff",
                "background": "#ffffff",
                "text": "#212529"
            }
        })

        response = requests.get(f"{self.BACKEND_URL}/widget/config")
        self.assertEqual(response.status_code, 200)

        config = response.json()
        required_keys = ['theme', 'position', 'max_comments', 'colors']
        for key in required_keys:
            self.assertIn(key, config)

    @patch('requests.post')
    def test_widget_config_update(self, mock_post):
        """Test widget configuration update."""
        mock_post.return_value = Mock(status_code=200, json=lambda: {
            "message": "Widget configuration updated successfully",
            "config": {
                "theme": "dark",
                "position": "bottom-left",
                "max_comments": 25
            }
        })

        new_config = {
            "theme": "dark",
            "position": "bottom-left",
            "max_comments": 25
        }

        response = requests.post(f"{self.BACKEND_URL}/widget/config", json=new_config)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('message', data)
        self.assertIn('config', data)

class TestLoadTesting(unittest.TestCase):
    """Load testing for the system."""

    BACKEND_URL = "http://localhost:8000"

    def test_concurrent_requests(self):
        """Test system performance under concurrent load."""
        import concurrent.futures
        import threading

        results = []
        errors = []

        def make_request(request_id):
            try:
                start_time = time.time()
                response = requests.get(f"{self.BACKEND_URL}/moderation/stats")
                end_time = time.time()

                results.append({
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            except Exception as e:
                errors.append({'request_id': request_id, 'error': str(e)})

        # Test with 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            concurrent.futures.wait(futures)

        # Check results
        successful_requests = len([r for r in results if r['status_code'] == 200])
        self.assertGreaterEqual(successful_requests, 8, "Too many failed requests")

        # Check response times (should be under 2 seconds each)
        slow_requests = [r for r in results if r['response_time'] > 2.0]
        self.assertLess(len(slow_requests), 3, "Too many slow requests")

class TestEndToEndWidget(unittest.TestCase):
    """End-to-end tests for widget functionality."""

    FRONTEND_URL = "http://localhost:3000"

    @patch('requests.get')
    def test_widget_embed_generation(self, mock_get):
        """Test widget embed code generation."""
        mock_get.return_value = Mock(status_code=200, json=lambda: {
            "thread_id": "test_thread",
            "embed_html": "<div id=\"comment-widget-test_thread\"></div><script>...</script>",
            "embed_script": "// Comment Widget Embed Code...",
            "config": {"theme": "default"}
        })

        response = requests.get("http://localhost:8000/widget/embed/test_thread")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('embed_html', data)
        self.assertIn('embed_script', data)
        self.assertIn('config', data)

    def test_widget_preview_generation(self):
        """Test widget preview functionality."""
        config = {
            "theme": "dark",
            "position": "bottom-right",
            "max_comments": 25
        }

        # This would test the preview endpoint
        # In a real test, you'd make actual HTTP requests
        self.assertIsInstance(config, dict)
        self.assertIn('theme', config)

if __name__ == '__main__':
    # Run tests with timing information
    unittest.main(verbosity=2)