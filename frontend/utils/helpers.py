"""
Utility functions for the frontend application.
"""
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json


def hash_password(password: str) -> str:
    """Simple password hash for demo purposes"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_session_id(email: str) -> str:
    """Generate session ID from email and timestamp"""
    return hashlib.md5(f"{email}{datetime.now()}".encode()).hexdigest()


def generate_site_id(url: str) -> str:
    """Generate site ID from URL"""
    return hashlib.md5(url.encode()).hexdigest()[:16]


def format_datetime(dt_str: str) -> str:
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return dt_str


def validate_email(email: str) -> bool:
    """Basic email validation"""
    return '@' in email and '.' in email and len(email) > 5


def validate_password(password: str) -> bool:
    """Basic password validation"""
    return len(password) >= 6


def safe_json_loads(data: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON data"""
    try:
        return json.loads(data)
    except:
        return None


def calculate_stats(comments: list) -> Dict[str, int]:
    """Calculate comment statistics"""
    total = len(comments)
    approved = len([c for c in comments if c.get('is_approved') == 1])
    pending = len([c for c in comments if c.get('is_approved') == 0])
    rejected = len([c for c in comments if c.get('is_approved') == 2])

    return {
        'total': total,
        'approved': approved,
        'pending': pending,
        'rejected': rejected
    }


def group_threads_by_site(threads: list) -> Dict[str, Dict[str, Any]]:
    """Group threads by site (external_page_id)"""
    sites = {}
    for thread in threads:
        site_id = thread.get('external_page_id')
        if site_id not in sites:
            sites[site_id] = {
                'site_id': site_id,
                'site_name': thread.get('title', '').replace(' - Main Thread', ''),
                'site_url': thread.get('url'),
                'threads': [],
                'total_comments': 0
            }
        sites[site_id]['threads'].append(thread)
    return sites


def is_session_expired(created_at: datetime, max_age: timedelta = timedelta(hours=24)) -> bool:
    """Check if session is expired"""
    return datetime.now() - created_at > max_age


def build_api_url(endpoint: str, base_url: str = "http://localhost:8000") -> str:
    """Build full API URL"""
    return f"{base_url}{endpoint}"


def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return url