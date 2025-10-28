from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import hashlib

# In-memory storage for demo
comments = []
threads = []

class Comment:
    def __init__(self, id, content, author, thread_id, parent_id=None):
        self.id = id
        self.content = content
        self.author = author
        self.thread_id = thread_id
        self.parent_id = parent_id
        self.created_at = datetime.now().isoformat()
        self.is_approved = 0

def generate_thread_id(url=None):
    if not url or "localhost" in url or "127.0.0.1" in url:
        return "demo_site"
    return hashlib.md5(url.encode()).hexdigest()[:16]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_cors_headers()

        if self.path == "/api/health":
            self.handle_health()
        elif self.path.startswith("/api/comments"):
            self.handle_comments()
        elif self.path.startswith("/api/threads"):
            self.handle_threads()
        else:
            self.send_error(404)

    def do_POST(self):
        self.send_cors_headers()

        if self.path == "/api/comments":
            self.handle_create_comment()
        elif self.path == "/api/auth/login":
            self.handle_login()
        else:
            self.send_error(404)

    def do_PUT(self):
        self.send_cors_headers()

        if "moderate" in self.path:
            self.handle_moderate()
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-type', 'application/json')

    def handle_health(self):
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_comments(self):
        # Parse query parameters
        query = self.path.split('?')[1] if '?' in self.path else ''
        params = {}
        if query:
            for pair in query.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    params[key] = value

        thread_id = params.get('thread_id')
        status_filter = params.get('status')
        search = params.get('search')
        limit = int(params.get('limit', '50'))

        filtered = []
        for comment in comments:
            if thread_id and comment.thread_id != thread_id:
                continue
            if status_filter and str(comment.is_approved) != status_filter:
                continue
            if search and search.lower() not in comment.content.lower() and search.lower() not in comment.author.lower():
                continue
            filtered.append({
                'id': comment.id,
                'content': comment.content,
                'author': comment.author,
                'thread_id': comment.thread_id,
                'parent_id': comment.parent_id,
                'created_at': comment.created_at,
                'is_approved': comment.is_approved
            })

        filtered = filtered[:limit]
        self.end_headers()
        self.wfile.write(json.dumps({'data': filtered}).encode())

    def handle_create_comment(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            thread_id = generate_thread_id(data.get('url'))
            comment_id = len(comments) + 1

            comment = Comment(
                id=comment_id,
                content=data['content'],
                author=data['author'],
                thread_id=thread_id,
                parent_id=data.get('parent_id')
            )

            comments.append(comment)

            response = {
                'id': comment.id,
                'content': comment.content,
                'author': comment.author,
                'thread_id': comment.thread_id,
                'parent_id': comment.parent_id,
                'created_at': comment.created_at,
                'is_approved': comment.is_approved
            }

            self.send_response(201)
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, str(e))

    def handle_moderate(self):
        try:
            path_parts = self.path.split('/')
            comment_id = int(path_parts[3])

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            for comment in comments:
                if comment.id == comment_id:
                    comment.is_approved = data['is_approved']
                    break

            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())

        except Exception as e:
            self.send_error(500, str(e))

    def handle_threads(self):
        mock_threads = [{
            'id': 1,
            'external_page_id': 'demo_site',
            'title': 'Demo Thread',
            'url': 'https://indie-comments-widget.vercel.app',
            'created_at': datetime.now().isoformat()
        }]

        self.end_headers()
        self.wfile.write(json.dumps({'data': mock_threads}).encode())

    def handle_login(self):
        response = {
            'user_id': 1,
            'name': 'Demo User',
            'email': 'demo@example.com'
        }
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        # Suppress default logging for Vercel
        pass