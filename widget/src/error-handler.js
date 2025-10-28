/**
 * Error handling utilities for the Comment Widget
 */
export class ErrorHandler {
    static handle(error, context = {}) {
        console.error('Comment Widget Error:', error, context);

        // Categorize error types
        if (error.name === 'NetworkError' || error.message.includes('fetch')) {
            return this.handleNetworkError(error, context);
        }

        if (error.name === 'ValidationError') {
            return this.handleValidationError(error, context);
        }

        if (error.status >= 400 && error.status < 500) {
            return this.handleClientError(error, context);
        }

        if (error.status >= 500) {
            return this.handleServerError(error, context);
        }

        return this.handleGenericError(error, context);
    }

    static handleNetworkError(error, context) {
        const message = 'Network connection failed. Please check your internet connection.';
        this.showUserMessage(message, 'error');
        return { type: 'network', message, retryable: true };
    }

    static handleValidationError(error, context) {
        const message = error.message || 'Invalid input data.';
        this.showUserMessage(message, 'warning');
        return { type: 'validation', message, retryable: false };
    }

    static handleClientError(error, context) {
        let message = 'Request failed.';

        if (error.status === 401) {
            message = 'Authentication required.';
        } else if (error.status === 403) {
            message = 'Access denied.';
        } else if (error.status === 404) {
            message = 'Resource not found.';
        } else if (error.status === 429) {
            message = 'Too many requests. Please wait and try again.';
        }

        this.showUserMessage(message, 'error');
        return { type: 'client', message, retryable: error.status === 429 };
    }

    static handleServerError(error, context) {
        const message = 'Server error occurred. Please try again later.';
        this.showUserMessage(message, 'error');
        return { type: 'server', message, retryable: true };
    }

    static handleGenericError(error, context) {
        const message = 'An unexpected error occurred.';
        this.showUserMessage(message, 'error');
        return { type: 'generic', message, retryable: true };
    }

    static showUserMessage(message, type = 'info') {
        // Create a temporary notification element
        const notification = document.createElement('div');
        notification.className = `comment-widget-notification comment-widget-notification--${type}`;
        notification.textContent = message;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'assertive');

        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: type === 'error' ? '#ff4444' : type === 'warning' ? '#ffaa00' : '#44aa44',
            color: 'white',
            padding: '12px 16px',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            zIndex: '10000',
            maxWidth: '300px',
            fontFamily: 'Arial, sans-serif',
            fontSize: '14px'
        });

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    static async withRetry(operation, maxRetries = 3, delay = 1000) {
        let lastError;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error;

                if (!this.isRetryable(error) || attempt === maxRetries) {
                    throw error;
                }

                // Exponential backoff
                const waitTime = delay * Math.pow(2, attempt - 1);
                await this.delay(waitTime);
            }
        }

        throw lastError;
    }

    static isRetryable(error) {
        // Network errors are usually retryable
        if (error.name === 'NetworkError' || error.message.includes('fetch')) {
            return true;
        }

        // Server errors (5xx) are retryable
        if (error.status >= 500) {
            return true;
        }

        // Rate limiting is retryable
        if (error.status === 429) {
            return true;
        }

        return false;
    }

    static delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}