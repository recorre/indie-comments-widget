from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_homepage()
        elif self.path.startswith("/dashboard"):
            self.serve_dashboard()
        else:
            self.send_error(404)

    def serve_homepage(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indie Comments Widget - Privacy-Focused Comments</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; }
        .hero-section { background: linear-gradient(135deg, #007cba, #005a87); color: white; padding: 4rem 0; text-align: center; }
        .demo-section { padding: 4rem 0; background: #f8f9fa; }
        .widget-demo-container { border: 2px dashed #007cba; padding: 2rem; border-radius: 12px; background: white; margin: 2rem 0; }
    </style>
</head>
<body>
    <section class="hero-section">
        <div class="container">
            <h1 class="display-4 fw-bold mb-3">
                <i class="fas fa-comments me-3"></i>
                Indie Comments Widget
            </h1>
            <p class="lead mb-4">
                Add privacy-focused comments to any website in under 60 seconds. No server required.
            </p>
            <div class="d-flex justify-content-center gap-3 mb-4">
                <a href="#demo" class="btn btn-light btn-lg">
                    <i class="fas fa-play me-2"></i>Try Live Demo
                </a>
                <a href="#install" class="btn btn-outline-light btn-lg">
                    <i class="fas fa-code me-2"></i>Get Started
                </a>
            </div>
        </div>
    </section>

    <section id="demo" class="demo-section">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="widget-demo-container">
                        <h4 class="mb-4 text-center">
                            <i class="fas fa-comments me-2"></i>
                            Live Comments Widget
                        </h4>
                        <div id="comments-widget-container">
                            <comment-widget thread-id="demo_site" theme="default" show-theme-selector></comment-widget>
                        </div>
                        <div class="mt-3 text-center">
                            <small class="text-muted">
                                🔒 Privacy-first comments - no tracking, user-controlled data
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script type="module">
        import '/widget/src/widget.js';
    </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_dashboard(self):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Comment Widget</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">
                <i class="fas fa-comments"></i> Comment Widget
            </a>
        </div>
    </nav>

    <div class="container-fluid py-4">
        <div class="row">
            <div class="col-12">
                <h1 class="h3 mb-4">Dashboard</h1>
                <p class="text-muted">Welcome to your comment moderation dashboard</p>

                <div class="alert alert-info">
                    <h5>Demo Dashboard</h5>
                    <p>This is a simplified demo version. For full functionality, deploy with a proper backend.</p>
                    <a href="/" class="btn btn-primary">Back to Homepage</a>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        # Suppress default logging
        pass