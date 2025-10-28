/**
 * Comment Renderer for Widget
 * Handles HTML rendering of comments with nesting
 */

import { sanitizeComment } from './utils/sanitize.js';

export class CommentRenderer {
    constructor() {
        this.templates = {
            widget: (data) => `
                <div class="comment-widget" data-theme="${data.theme}" role="region" aria-label="Comment widget">
                    <div class="comment-header">
                        <h3>💬 Comments</h3>
                        ${data.showThemeSelector ? this.renderThemeSelector(data.theme, data.onThemeChange) : ''}
                    </div>

                    ${data.error ? this.renderError(data.error) : ''}

                    ${data.loading ? this.renderLoading() : ''}

                    ${!data.loading && !data.error ? this.renderCommentForm(data.onSubmit, data.replyingTo, data.onCancelReply) : ''}

                    <div class="comment-list" role="region" aria-label="Comments list">
                        ${data.comments.length > 0
                            ? data.comments.map(comment => this.renderComment(comment, 0, data.maxDepth, data.onReply)).join('')
                            : this.renderEmptyState()
                        }
                    </div>
                </div>
            `,

            comment: (comment, level, maxDepth, onReply) => `
                <article class="comment-item level-${level}" data-id="${comment.id}" style="margin-left: ${level * 20}px;" role="article" aria-labelledby="comment-author-${comment.id}" aria-describedby="comment-content-${comment.id}">
                    <div class="comment-avatar">
                        <div class="avatar-placeholder" aria-hidden="true">
                            ${comment.author_name.charAt(0).toUpperCase()}
                        </div>
                    </div>
                    <div class="comment-content">
                        <div class="comment-meta">
                            <span class="comment-author" id="comment-author-${comment.id}">${this.escapeHtml(comment.author_name)}</span>
                            <time class="comment-date" datetime="${comment.created_at}" aria-label="Posted ${this.formatDate(comment.created_at)}">${this.formatDate(comment.created_at)}</time>
                        </div>
                        <div class="comment-text" id="comment-content-${comment.id}">${this.formatContent(comment.content)}</div>
                        <div class="comment-actions">
                            ${level < maxDepth ? `<button class="reply-btn" data-parent-id="${comment.id}" aria-label="Reply to ${this.escapeHtml(comment.author_name)}'s comment">Reply</button>` : ''}
                        </div>
                        ${comment.replies && comment.replies.length > 0
                            ? `<div class="comment-replies" role="region" aria-label="Replies to this comment">${comment.replies.map(reply => this.renderComment(reply, level + 1, maxDepth, onReply)).join('')}</div>`
                            : ''
                        }
                    </div>
                </article>
            `,

            form: (onSubmit, replyingTo, onCancelReply) => `
                <form class="comment-form" id="comment-form" role="form" aria-label="${replyingTo ? 'Reply to comment' : 'Add new comment'}">
                    ${replyingTo ? `<div class="reply-indicator" role="status" aria-live="polite">Replying to comment #${replyingTo}</div>` : ''}
                    <div class="form-group">
                        <input type="text" id="author-name" name="author-name" placeholder="Your name" required aria-label="Your name" aria-required="true">
                    </div>
                    <div class="form-group">
                        <input type="email" id="author-email" name="author-email" placeholder="Your email" required aria-label="Your email address" aria-required="true" aria-describedby="email-help">
                        <div id="email-help" class="sr-only">Your email will not be published</div>
                    </div>
                    <div class="form-group">
                        <textarea id="comment-content" name="comment-content" placeholder="${replyingTo ? 'Write your reply...' : 'Write your comment...'}" required rows="4" aria-label="${replyingTo ? 'Write your reply' : 'Write your comment'}" aria-required="true"></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="submit-btn" aria-describedby="submit-help">${replyingTo ? 'Post Reply' : 'Post Comment'}</button>
                        ${replyingTo ? `<button type="button" class="cancel-reply-btn" id="cancel-reply-btn" aria-label="Cancel reply">Cancel Reply</button>` : ''}
                        <div id="submit-help" class="sr-only">Submit your ${replyingTo ? 'reply' : 'comment'}</div>
                    </div>
                </form>
            `,

            themeSelector: (currentTheme, onChange) => `
                <label for="theme-selector" class="sr-only">Choose theme</label>
                <select class="theme-selector" id="theme-selector" aria-label="Select comment widget theme">
                    <option value="default" ${currentTheme === 'default' ? 'selected' : ''}>Default</option>
                    <option value="dark" ${currentTheme === 'dark' ? 'selected' : ''}>Dark</option>
                    <option value="matrix" ${currentTheme === 'matrix' ? 'selected' : ''}>Matrix</option>
                    <option value="neocities" ${currentTheme === 'neocities' ? 'selected' : ''}>NeoCities</option>
                    <option value="serene-mist" ${currentTheme === 'serene-mist' ? 'selected' : ''}>Serene Mist</option>
                    <option value="neon-pulse" ${currentTheme === 'neon-pulse' ? 'selected' : ''}>Neon Pulse</option>
                    <option value="geometric-prime" ${currentTheme === 'geometric-prime' ? 'selected' : ''}>Geometric Prime</option>
                    <option value="forest-flow" ${currentTheme === 'forest-flow' ? 'selected' : ''}>Forest Flow</option>
                    <option value="digital-chaos" ${currentTheme === 'digital-chaos' ? 'selected' : ''}>Digital Chaos</option>
                </select>
            `,

            loading: () => `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Loading comments...</p>
                </div>
            `,

            error: (message) => `
                <div class="error-state">
                    <p>❌ ${this.escapeHtml(message)}</p>
                </div>
            `,

            empty: () => `
                <div class="empty-state">
                    <p>💭 No comments yet. Be the first to comment!</p>
                </div>
            `
        };
    }

    render(data) {
        return this.templates.widget(data);
    }

    renderComment(comment, level, maxDepth) {
        return this.templates.comment(comment, level, maxDepth);
    }

    renderCommentForm(onSubmit, replyingTo, onCancelReply) {
        return this.templates.form(onSubmit, replyingTo, onCancelReply);
    }

    // Add ARIA attributes to form elements
    enhanceFormAccessibility(formElement) {
        if (!formElement) return;

        // Add ARIA labels and descriptions
        const nameInput = formElement.querySelector('input[name="author-name"]');
        if (nameInput) {
            nameInput.setAttribute('aria-label', 'Your name');
            nameInput.setAttribute('aria-required', 'true');
        }

        const emailInput = formElement.querySelector('input[name="author-email"]');
        if (emailInput) {
            emailInput.setAttribute('aria-label', 'Your email address');
            emailInput.setAttribute('aria-required', 'true');
            emailInput.setAttribute('aria-describedby', 'email-help');
        }

        const contentTextarea = formElement.querySelector('textarea[name="comment-content"]');
        if (contentTextarea) {
            contentTextarea.setAttribute('aria-label', replyingTo ? 'Write your reply' : 'Write your comment');
            contentTextarea.setAttribute('aria-required', 'true');
        }

        // Add hidden help text for email
        const emailHelp = document.createElement('div');
        emailHelp.id = 'email-help';
        emailHelp.className = 'sr-only';
        emailHelp.textContent = 'Your email will not be published';
        formElement.appendChild(emailHelp);
    }

    renderThemeSelector(currentTheme, onChange) {
        return this.templates.themeSelector(currentTheme, onChange);
    }

    renderLoading() {
        return this.templates.loading();
    }

    renderError(message) {
        return this.templates.error(message);
    }

    renderEmptyState() {
        return this.templates.empty();
    }

    // Utility methods
    formatDate(dateString) {
        if (!dateString) return '';

        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));

        if (diffInHours < 1) return 'Just now';
        if (diffInHours < 24) return `${diffInHours}h ago`;

        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatContent(content) {
        // Use DOMPurify sanitization instead of basic escaping
        // This provides better security and handles XSS prevention
        return sanitizeComment(content, {
            allowHTML: false,  // Plain text only for MVP
            convertNewlines: true  // Convert \n to <br>
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}