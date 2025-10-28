/**
 * API Client for Comment Widget
 * Handles communication with FastAPI proxy
 */

export class APIClient {
    constructor(baseUrl = 'http://localhost:8000') {
        // Use localhost:8000 for local development, but allow override
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Network error: Unable to connect to API');
            }
            throw error;
        }
    }

    // Comments API
    async getComments(threadId, options = {}) {
        const params = new URLSearchParams({
            thread_id: threadId,
            ...options
        });

        return this.request(`/widget/comments/${threadId}?${params}`);
    }

    async createComment(commentData) {
        return this.request('/comments', {
            method: 'POST',
            body: JSON.stringify(commentData)
        });
    }

    async updateComment(commentId, commentData) {
        return this.request(`/comments/${commentId}`, {
            method: 'PUT',
            body: JSON.stringify(commentData)
        });
    }

    async deleteComment(commentId) {
        return this.request(`/comments/${commentId}`, {
            method: 'DELETE'
        });
    }

    async moderateComment(commentId, moderationData) {
        return this.request(`/comments/${commentId}/moderate`, {
            method: 'PUT',
            body: JSON.stringify(moderationData)
        });
    }

    // Threads API
    async getThread(threadId) {
        return this.request(`/threads/${threadId}`);
    }

    async createThread(threadData) {
        return this.request('/threads', {
            method: 'POST',
            body: JSON.stringify(threadData)
        });
    }

    // Demo API
    async getDemoThread() {
        return this.request('/demo/thread');
    }

    // Health check
    async healthCheck() {
        return this.request('/health');
    }
}