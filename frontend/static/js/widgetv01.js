// Indie Comments Widget
// A lightweight, embeddable comment system

class IndieCommentsWidget extends HTMLElement {
    constructor() {
        super();
        console.log('IndieCommentsWidget constructor called');
        this.threadId = this.getAttribute('thread-id') || window.location.pathname;
        this.apiBaseUrl = this.getAttribute('api-base-url') || 'http://localhost:8000';
        this.containerId = 'indie-comments-container'; // Fixed ID for shadow DOM
        this.moderationEnabled = false;
        this.comments = [];

        // Theme related CSS strings
        this.themes = {
            'default': `
/* Default Theme - Widget styles */
#indie-comments-app {
    background: #fff !important;
    color: #333 !important;
    border: 1px solid #e0e0e0 !important;
}
#indie-comments-form-container {
    background: #f8f9fa !important;
    border: 1px solid #e9ecef !important;
}
.indie-comments-comment {
    background: #fff !important;
    border: 1px solid #eee !important;
    color: #444 !important;
}
.indie-comments-author {
    color: #333 !important;
}
.indie-comments-date {
    color: #888 !important;
}
.indie-comments-content {
    color: #444 !important;
}
#indie-comments-form button {
    background: #007cba !important;
    color: white !important;
}
#indie-comments-form button:hover {
    background: #005a87 !important;
}
.indie-comments-input-group input,
.indie-comments-input-group textarea {
    background: #fff !important;
    border-color: #ddd !important;
    color: #333 !important;
}
#indie-comments-theme-select {
    background: #fff !important;
    border-color: #ddd !important;
    color: #333 !important;
}
.indie-comments-empty {
    color: #666 !important;
}
            `,
            'dark': `
/* Dark Theme - Widget styles */
#indie-comments-app {
    background: #2d2d2d !important;
    color: #e0e0e0 !important;
    border: 1px solid #444 !important;
}
#indie-comments-form-container {
    background: #3a3a3a !important;
    border: 1px solid #555 !important;
}
.indie-comments-comment {
    background: #2d2d2d !important;
    border: 1px solid #444 !important;
    color: #e0e0e0 !important;
}
.indie-comments-author {
    color: #4fc3f7 !important;
}
.indie-comments-date {
    color: #b0b0b0 !important;
}
.indie-comments-content {
    color: #e0e0e0 !important;
}
#indie-comments-form button {
    background: #4fc3f7 !important;
    color: #000 !important;
}
#indie-comments-form button:hover {
    background: #29b6f6 !important;
}
.indie-comments-input-group input,
.indie-comments-input-group textarea {
    background: #3a3a3a !important;
    border-color: #555 !important;
    color: #e0e0e0 !important;
}
#indie-comments-theme-select {
    background: #3a3a3a !important;
    border-color: #555 !important;
    color: #e0e0e0 !important;
}
.indie-comments-empty {
    color: #b0b0b0 !important;
}
            `,
            'matrix': `
/* Matrix Theme - Widget styles */
#indie-comments-app {
    background: #000 !important;
    color: #0f0 !important;
    border: 1px solid #0a0 !important;
    font-family: 'Courier New', monospace !important;
}
#indie-comments-form-container {
    background: #010 !important;
    border: 1px solid #080 !important;
}
.indie-comments-comment {
    background: #000 !important;
    border: 1px solid #0a0 !important;
    color: #0f0 !important;
    font-family: 'Courier New', monospace !important;
}
.indie-comments-author {
    color: #0f0 !important;
}
.indie-comments-date {
    color: #6b7280 !important;
}
.indie-comments-content {
    color: #0f0 !important;
}
#indie-comments-form button {
    background: #0a0 !important;
    color: #000 !important;
    font-family: 'Courier New', monospace !important;
}
#indie-comments-form button:hover {
    background: #0f0 !important;
    box-shadow: 0 0 5px rgba(0, 255, 0, 0.5) !important;
}
.indie-comments-input-group input,
.indie-comments-input-group textarea {
    background: #010 !important;
    border-color: #080 !important;
    color: #0f0 !important;
    font-family: 'Courier New', monospace !important;
}
#indie-comments-theme-select {
    background: #010 !important;
    border-color: #080 !important;
    color: #0f0 !important;
    font-family: 'Courier New', monospace !important;
}
.indie-comments-empty {
    color: #6b7280 !important;
}
            `,
            'neocities': `
/* NeoCities Theme - Widget styles */
#indie-comments-app {
    background: #ccffff !important;
    color: #330033 !important;
    border: 2px dashed #996699 !important;
}
#indie-comments-form-container {
    background: #ffff99 !important;
    border: 2px dotted #669966 !important;
}
.indie-comments-comment {
    background: #ccffff !important;
    border: 2px dashed #996699 !important;
    color: #330033 !important;
}
.indie-comments-author {
    color: #663399 !important;
}
.indie-comments-date {
    color: #666699 !important;
}
.indie-comments-content {
    color: #330033 !important;
}
#indie-comments-form button {
    background: #ffccff !important;
    color: #330033 !important;
    border: 2px solid #996699 !important;
}
#indie-comments-form button:hover {
    background: #ff99ff !important;
}
.indie-comments-input-group input,
.indie-comments-input-group textarea {
    background: #ffff99 !important;
    border: 2px dotted #669966 !important;
    color: #330033 !important;
}
#indie-comments-theme-select {
    background: #ffff99 !important;
    border: 2px dotted #669966 !important;
    color: #330033 !important;
}
.indie-comments-empty {
    color: #666699 !important;
}
            `
        };

        this.currentTheme = 'default'; // Default theme
        this.shadow = this.attachShadow({ mode: 'open' });
        // Initialize synchronously first, then async
        this.render();
        this.init();
    }

    async init() {
        console.log('IndieCommentsWidget init called');
        try {
            await this.loadThreadStatus();
            await this.loadComments();
            // Re-render after API calls complete to update with any loaded data
            this.render();
        } catch (error) {
            console.error('Error initializing Indie Comments Widget:', error);
            // Re-render even if API calls fail to ensure UI is visible
            this.render();
        }
    }

    async loadThreadStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/v1/threads/${this.threadId}/status`);
            const status = await response.json();
            
            if (status.exists) {
                this.moderationEnabled = status.moderation_enabled;
            } else {
                // Thread doesn't exist, it will be created when first comment is submitted
                console.log('Thread does not exist yet, will be created on first comment');
            }
        } catch (error) {
            console.error('Error loading thread status:', error);
        }
    }

    async loadComments() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/v1/comments/${this.threadId}`);
            const data = await response.json();
            this.comments = data.comments || [];
        } catch (error) {
            console.error('Error loading comments:', error);
        }
    }

    async submitComment(commentData) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/v1/comments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    thread_id: this.threadId,
                    ...commentData
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.clearForm();
                this.showMessage('Comment submitted for moderation');
                await this.loadComments();
                this.render();
                return result;
            } else {
                throw new Error(result.detail || 'Failed to submit comment');
            }
        } catch (error) {
            console.error('Error submitting comment:', error);
            this.showError(error.message || 'Failed to submit comment');
            throw error;
        }
    }

    clearForm() {
        const form = this.shadow.querySelector('#indie-comments-form');
        if (form) {
            form.reset();
        }
    }

    showMessage(message) {
        const messageEl = this.shadow.querySelector('#indie-comments-message');
        if (messageEl) {
            messageEl.textContent = message;
            messageEl.className = 'indie-comments-message success';
            setTimeout(() => {
                messageEl.textContent = '';
                messageEl.className = 'indie-comments-message';
            }, 3000);
        }
    }

    showError(message) {
        const messageEl = this.shadow.querySelector('#indie-comments-message');
        if (messageEl) {
            messageEl.textContent = message;
            messageEl.className = 'indie-comments-message error';
            setTimeout(() => {
                messageEl.textContent = '';
                messageEl.className = 'indie-comments-message';
            }, 5000);
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    renderComment(comment, level = 0) {
        const commentEl = document.createElement('div');
        commentEl.className = `indie-comments-comment level-${level}`;
        commentEl.innerHTML = `
            <div class="indie-comments-comment-header">
                <strong class="indie-comments-author">${comment.author_name}</strong>
                <span class="indie-comments-date">${this.formatDate(comment.created_at)}</span>
            </div>
            <div class="indie-comments-content">${comment.content}</div>
            <div class="indie-comments-replies">
                ${(comment.replies && comment.replies.length > 0) 
                    ? comment.replies.map(reply => this.renderComment(reply, level + 1)).join('') 
                    : ''}
            </div>
        `;
        return commentEl;
    }

    render() {
        console.log('IndieCommentsWidget render called, current theme:', this.currentTheme);
        this.shadow.innerHTML = '';

        const style = document.createElement('style');
        style.textContent = `
/* Base widget styles - theme-specific styles will override these */
#indie-comments-app {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    max-width: 680px;
    margin: 2rem auto;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease;
}
#indie-comments-header {
    margin-bottom: 1.5rem;
}
#indie-comments-header h3 {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
    font-weight: 600;
}
.indie-comments-message {
    padding: 0.5rem 0;
    font-size: 0.9rem;
}
.indie-comments-message.success {
    color: #28a745;
}
.indie-comments-message.error {
    color: #dc3545;
}
#indie-comments-form-container {
    padding: 1.5rem;
    border-radius: 6px;
    margin-bottom: 2rem;
}
.indie-comments-input-group {
    margin-bottom: 1rem;
}
.indie-comments-input-group input,
.indie-comments-input-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
}
.indie-comments-input-group textarea {
    min-height: 100px;
    resize: vertical;
}
#indie-comments-form button {
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
}
#indie-comments-list {
    margin-top: 1.5rem;
}
.indie-comments-empty {
    text-align: center;
    font-style: italic;
    padding: 2rem;
}
.indie-comments-comment {
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.indie-comments-comment.level-0 {
    border-left: 3px solid #007cba;
}
.indie-comments-comment.level-1 {
    margin-left: 2rem;
    border-left: 2px solid #888;
}
.indie-comments-comment.level-2 {
    margin-left: 3rem;
    border-left: 1px solid #ccc;
}
.indie-comments-comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}
.indie-comments-author {
    font-weight: 600;
}
.indie-comments-date {
    color: #888;
}
.indie-comments-content {
    line-height: 1.6;
}
.indie-comments-replies {
    margin-top: 1rem;
}
#indie-comments-theme-select {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    font-size: 0.9rem;
    margin-left: 1rem;
}
/* Responsive design */
@media (max-width: 768px) {
    #indie-comments-app {
        margin: 1rem;
        padding: 1rem;
    }
    .indie-comments-comment.level-1,
    .indie-comments-comment.level-2 {
        margin-left: 1rem;
    }
    #indie-comments-theme-select {
        margin-left: 0;
        margin-top: 0.5rem;
        width: 100%;
    }
}
/* Theme styles injected dynamically */
${this.themes[this.currentTheme] || ''}
        `;
        this.shadow.appendChild(style);

        const app = document.createElement('div');
        app.id = 'indie-comments-app';
        app.innerHTML = `
            <div id="indie-comments-header">
                <h3>Comments</h3>
                <div id="indie-comments-message" class="indie-comments-message"></div>
                <select id="indie-comments-theme-select" aria-label="Select theme">
                    <option value="default">Default</option>
                    <option value="dark">Dark</option>
                    <option value="matrix">Matrix</option>
                    <option value="neocities">NeoCities</option>
                </select>
            </div>
            <div id="indie-comments-form-container">
                <form id="indie-comments-form">
                    <div class="indie-comments-input-group">
                        <input type="text" id="indie-comments-author" name="author_name" placeholder="Your name" required />
                    </div>
                    <div class="indie-comments-input-group">
                        <input type="email" id="indie-comments-email" name="author_email" placeholder="Your email" required />
                    </div>
                    <div class="indie-comments-input-group">
                        <textarea id="indie-comments-content" name="content" placeholder="Write your comment..." required></textarea>
                    </div>
                    <button type="submit">Post Comment</button>
                </form>
            </div>
            <div id="indie-comments-list">
                ${this.comments.length > 0
                    ? this.comments.map(comment => this.renderComment(comment)).join('')
                    : '<div class="indie-comments-empty">No comments yet. Be the first to comment!</div>'}
            </div>
        `;
        this.shadow.appendChild(app);

        // Set theme select to current theme
        const themeSelect = this.shadow.getElementById('indie-comments-theme-select');
        themeSelect.value = this.currentTheme;

        // Theme select event listener
        themeSelect.addEventListener('change', (event) => {
            this.currentTheme = event.target.value;
            this.render(); // Re-render to apply the selected theme

            // Dispatch custom event to notify theme change to host page
            this.dispatchEvent(new CustomEvent('themeChange', {
                detail: { theme: this.currentTheme },
                bubbles: true,
                composed: true
            }));
        });

        // Attach form event listeners
        const form = this.shadow.querySelector('#indie-comments-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const commentData = {
                    author_name: formData.get('author_name'),
                    author_email: formData.get('author_email'),
                    content: formData.get('content')
                };
                try {
                    await this.submitComment(commentData);
                } catch (error) {
                    console.error('Comment submission failed:', error);
                }
            });
        }
    }
}

// Define the custom element
customElements.define('indie-comments-widget', IndieCommentsWidget);

// Debug: Log when the script loads
console.log('IndieCommentsWidget script loaded');

// Auto-initialize when DOM is loaded (fallback)
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, checking for indie-comments-widget elements');
    const widgets = document.querySelectorAll('indie-comments-widget');
    console.log('Found', widgets.length, 'indie-comments-widget elements');
});

// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { IndieCommentsWidget };
}
