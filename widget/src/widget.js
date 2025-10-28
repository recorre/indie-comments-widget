/**
 * Comment Widget v2.0 - Improved Architecture
 * Modular, themeable, and API-integrated comment system
 */

import { APIClient } from './api.js';
import { CommentRenderer } from './renderer.js';
import { ThemeManager } from './theme-manager.js';
import { Utils } from './utils.js';
import { ErrorHandler } from './error-handler.js';
import { StateManager } from './state-manager.js';
import widgetCSS from './widget.css';

class CommentWidget extends HTMLElement {
    constructor() {
        super();

        // Configuration from attributes
        this.threadId = this.getAttribute('thread-id') || Utils.generateThreadId();
        this.apiBaseUrl = this.getAttribute('api-base-url') || 'https://comment-widget-backend.vercel.app';
        this.theme = this.getAttribute('theme') || 'default';
        this.maxDepth = parseInt(this.getAttribute('max-depth')) || 3;
        this.showThemeSelector = this.hasAttribute('show-theme-selector') || true; // Default to true

        // Initialize components
        this.api = new APIClient(this.apiBaseUrl);
        this.renderer = new CommentRenderer();
        this.themeManager = new ThemeManager(this.theme);
        this.stateManager = new StateManager();

        // Initialize state
        this.stateManager.setTheme(this.theme);
        this.stateManager.loadFromStorage();

        // Subscribe to state changes
        this.stateManager.subscribe('comments', (newComments) => this.render());
        this.stateManager.subscribe('loading', (loading) => this.render());
        this.stateManager.subscribe('error', (error) => this.render());
        this.stateManager.subscribe('theme', (theme) => {
            this.theme = theme;
            this.themeManager.setTheme(theme);
            this.render();
        });

        // Create shadow DOM
        this.shadow = this.attachShadow({ mode: 'open' });

        // Initialize
        this.init();
    }

    async init() {
        try {
            this.stateManager.setLoading(true);

            // Load comments from API
            await this.loadComments();

            this.stateManager.setLoading(false);

        } catch (error) {
            console.error('Widget initialization error:', error);
            ErrorHandler.handle(error, { context: 'widget_init' });
            this.stateManager.setError(error.message);
            this.stateManager.setLoading(false);
        }
    }

    async loadComments() {
        try {
            const response = await ErrorHandler.withRetry(
                () => this.api.getComments(this.threadId)
            );
            this.stateManager.setComments(response.comments || []);
        } catch (error) {
            console.error('Error loading comments:', error);
            ErrorHandler.handle(error, { context: 'load_comments', threadId: this.threadId });
            this.stateManager.setError('Failed to load comments');
        }
    }

    async submitComment(commentData) {
        try {
            this.stateManager.setLoading(true);

            const result = await ErrorHandler.withRetry(
                () => this.api.createComment({
                    thread_id: parseInt(this.threadId),
                    author_name: commentData.author_name,
                    author_email: commentData.author_email,
                    content: commentData.content,
                    parent_id: commentData.parent_id || null
                })
            );

            // Reload comments after successful submission
            await this.loadComments();

            this.stateManager.setLoading(false);

            // Announce successful submission to screen readers
            const announcement = commentData.parent_id
                ? 'Your reply has been posted successfully'
                : 'Your comment has been posted successfully';
            this.announceToScreenReader(announcement);

            return result;

        } catch (error) {
            console.error('Error submitting comment:', error);
            ErrorHandler.handle(error, { context: 'submit_comment', commentData });
            this.stateManager.setError(error.message);
            this.stateManager.setLoading(false);

            // Announce error to screen readers
            this.announceToScreenReader('Error posting comment: ' + error.message);

            throw error;
        }
    }

    setTheme(theme) {
        this.stateManager.setTheme(theme);
        this.stateManager.saveToStorage();
    }

    connectedCallback() {
        // Listen for theme changes from page
        document.addEventListener('themeChange', (e) => {
            if (e.detail && e.detail.theme) {
                this.setAttribute('theme', e.detail.theme);
                this.setTheme(e.detail.theme);
            }
        });
    }

    render() {
        const state = this.stateManager.getState();
        const styles = this.themeManager.getStyles();
        const html = this.renderer.render({
            comments: state.comments,
            loading: state.loading,
            error: state.error,
            theme: state.theme,
            maxDepth: this.maxDepth,
            showThemeSelector: this.showThemeSelector,
            replyingTo: state.replyingTo,
            onSubmit: (data) => this.submitComment(data),
            onReply: (parentId) => this.startReply(parentId),
            onCancelReply: () => this.cancelReply(),
            onThemeChange: (theme) => this.setTheme(theme)
        });

        this.shadow.innerHTML = `
            <style>${widgetCSS}${styles}</style>
            ${html}
        `;

        // Attach event listeners after rendering
        this.attachEventListeners();
    }


    // Public API methods
    refresh() {
        this.loadComments();
    }

    getComments() {
        return this.stateManager.get('comments');
    }

    getTheme() {
        return this.stateManager.get('theme');
    }

    getState() {
        return this.stateManager.getState();
    }

    reset() {
        this.stateManager.reset();
    }

    undo() {
        return this.stateManager.undo();
    }

    startReply(parentId) {
        this.stateManager.setReplyingTo(parentId);

        // Focus management: move focus to the comment form when replying
        setTimeout(() => {
            const nameInput = this.shadow.getElementById('author-name');
            if (nameInput) {
                nameInput.focus();
                this.announceToScreenReader('Reply form opened. Enter your name to continue.');
            }
        }, 100);
    }

    cancelReply() {
        this.stateManager.clearReplyingTo();
        this.announceToScreenReader('Reply cancelled.');
    }

    attachEventListeners() {
        // Handle reply button clicks
        const replyButtons = this.shadow.querySelectorAll('.reply-btn');
        replyButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const parentId = parseInt(e.target.getAttribute('data-parent-id'));
                this.startReply(parentId);
            });
        });

        // Handle cancel reply button
        const cancelReplyBtn = this.shadow.getElementById('cancel-reply-btn');
        if (cancelReplyBtn) {
            cancelReplyBtn.addEventListener('click', () => {
                this.cancelReply();
            });
        }

        // Handle theme selector changes
        const themeSelector = this.shadow.getElementById('theme-selector');
        if (themeSelector) {
            themeSelector.addEventListener('change', (e) => {
                this.setTheme(e.target.value);
                this.announceThemeChange(e.target.value);
            });
        }

        // Handle form submission
        const form = this.shadow.getElementById('comment-form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const commentData = {
                    author_name: formData.get('author-name'),
                    author_email: formData.get('author-email'),
                    content: formData.get('comment-content'),
                    parent_id: this.replyingTo
                };
                await this.submitComment(commentData);
                form.reset();
                this.cancelReply();
            });
        }

        // Add keyboard navigation
        this.setupKeyboardNavigation();
    }

    setupKeyboardNavigation() {
        const widget = this.shadow.querySelector('.comment-widget');

        // Handle keyboard navigation within the widget
        widget.addEventListener('keydown', (e) => {
            const focusableElements = widget.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const focusableArray = Array.from(focusableElements);
            const currentIndex = focusableArray.indexOf(document.activeElement);

            switch (e.key) {
                case 'ArrowDown':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        const nextIndex = (currentIndex + 1) % focusableArray.length;
                        focusableArray[nextIndex].focus();
                    }
                    break;
                case 'ArrowUp':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        const prevIndex = currentIndex - 1 < 0 ? focusableArray.length - 1 : currentIndex - 1;
                        focusableArray[prevIndex].focus();
                    }
                    break;
                case 'Home':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        focusableArray[0].focus();
                    }
                    break;
                case 'End':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        focusableArray[focusableArray.length - 1].focus();
                    }
                    break;
            }
        });
    }

    announceThemeChange(theme) {
        const announcement = `Theme changed to ${theme}`;
        this.announceToScreenReader(announcement);
    }

    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;

        this.shadow.appendChild(announcement);

        // Remove after announcement
        setTimeout(() => {
            if (announcement.parentNode) {
                announcement.parentNode.removeChild(announcement);
            }
        }, 1000);
    }
}

// Register the custom element
customElements.define('comment-widget', CommentWidget);

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('Comment Widget v2.0 loaded');
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CommentWidget };
}