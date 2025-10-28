/**
 * State management for the Comment Widget
 */
export class StateManager {
    constructor() {
        this.state = {
            comments: [],
            loading: false,
            error: null,
            theme: 'default',
            replyingTo: null,
            user: null,
            pagination: {
                page: 1,
                limit: 50,
                total: 0
            }
        };

        this.listeners = new Map();
        this.history = [];
        this.maxHistorySize = 10;
    }

    // Get current state
    getState() {
        return { ...this.state };
    }

    // Update state partially
    setState(updates) {
        const previousState = { ...this.state };
        this.state = { ...this.state, ...updates };

        // Save to history for undo functionality
        this.history.push(previousState);
        if (this.history.length > this.maxHistorySize) {
            this.history.shift();
        }

        // Notify listeners
        this.notifyListeners(updates);
    }

    // Subscribe to state changes
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
        }
        this.listeners.get(key).push(callback);

        // Return unsubscribe function
        return () => {
            const listeners = this.listeners.get(key);
            if (listeners) {
                const index = listeners.indexOf(callback);
                if (index > -1) {
                    listeners.splice(index, 1);
                }
            }
        };
    }

    // Notify listeners of changes
    notifyListeners(changes) {
        for (const [key, listeners] of this.listeners) {
            if (key in changes) {
                listeners.forEach(callback => callback(this.state[key], changes[key]));
            }
        }
    }

    // Undo last state change
    undo() {
        if (this.history.length > 0) {
            const previousState = this.history.pop();
            const changes = {};

            // Calculate what changed
            for (const key in previousState) {
                if (JSON.stringify(previousState[key]) !== JSON.stringify(this.state[key])) {
                    changes[key] = previousState[key];
                }
            }

            this.state = previousState;
            this.notifyListeners(changes);
            return true;
        }
        return false;
    }

    // Reset state to initial values
    reset() {
        const initialState = {
            comments: [],
            loading: false,
            error: null,
            theme: 'default',
            replyingTo: null,
            user: null,
            pagination: {
                page: 1,
                limit: 50,
                total: 0
            }
        };

        const changes = {};
        for (const key in this.state) {
            if (JSON.stringify(initialState[key]) !== JSON.stringify(this.state[key])) {
                changes[key] = initialState[key];
            }
        }

        this.state = initialState;
        this.history = [];
        this.notifyListeners(changes);
    }

    // Get specific state value
    get(key) {
        return this.state[key];
    }

    // Set specific state value
    set(key, value) {
        this.setState({ [key]: value });
    }

    // Batch updates
    batch(updates) {
        this.setState(updates);
    }

    // Computed properties
    get isLoading() {
        return this.state.loading;
    }

    get hasError() {
        return this.state.error !== null;
    }

    get commentCount() {
        return this.state.comments.length;
    }

    get approvedComments() {
        return this.state.comments.filter(comment => comment.is_approved === 1);
    }

    get pendingComments() {
        return this.state.comments.filter(comment => comment.is_approved === 0);
    }

    get rejectedComments() {
        return this.state.comments.filter(comment => comment.is_approved === 2);
    }

    // Actions
    setLoading(loading) {
        this.setState({ loading });
    }

    setError(error) {
        this.setState({ error });
    }

    clearError() {
        this.setState({ error: null });
    }

    setComments(comments) {
        this.setState({ comments });
    }

    addComment(comment) {
        const newComments = [...this.state.comments, comment];
        this.setState({ comments: newComments });
    }

    updateComment(commentId, updates) {
        const newComments = this.state.comments.map(comment =>
            comment.id === commentId ? { ...comment, ...updates } : comment
        );
        this.setState({ comments: newComments });
    }

    removeComment(commentId) {
        const newComments = this.state.comments.filter(comment => comment.id !== commentId);
        this.setState({ comments: newComments });
    }

    setTheme(theme) {
        this.setState({ theme });
    }

    setReplyingTo(commentId) {
        this.setState({ replyingTo: commentId });
    }

    clearReplyingTo() {
        this.setState({ replyingTo: null });
    }

    setUser(user) {
        this.setState({ user });
    }

    updatePagination(pagination) {
        this.setState({ pagination: { ...this.state.pagination, ...pagination } });
    }

    // Persistence
    saveToStorage() {
        try {
            const dataToSave = {
                theme: this.state.theme,
                user: this.state.user
            };
            localStorage.setItem('commentWidgetState', JSON.stringify(dataToSave));
        } catch (error) {
            console.warn('Failed to save state to localStorage:', error);
        }
    }

    loadFromStorage() {
        try {
            const saved = localStorage.getItem('commentWidgetState');
            if (saved) {
                const data = JSON.parse(saved);
                this.setState(data);
            }
        } catch (error) {
            console.warn('Failed to load state from localStorage:', error);
        }
    }

    // Middleware for side effects
    use(middleware) {
        const originalSetState = this.setState.bind(this);
        this.setState = (updates) => {
            middleware(updates, this.state, originalSetState);
        };
    }
}