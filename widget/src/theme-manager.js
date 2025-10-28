/**
 * Enhanced Theme Manager for Comment Widget
 * Integrates with the dashboard theme system
 */

export class ThemeManager {
    constructor(currentTheme = 'default') {
        this.currentTheme = currentTheme;
        this.themes = {
            'default': this.getDefaultTheme(),
            'dark': this.getDarkTheme(),
            'matrix': this.getMatrixTheme(),
            'neocities': this.getNeocitiesTheme(),
            'serene-mist': this.getSereneMistTheme(),
            'neon-pulse': this.getNeonPulseTheme(),
            'geometric-prime': this.getGeometricPrimeTheme(),
            'forest-flow': this.getForestFlowTheme(),
            'digital-chaos': this.getDigitalChaosTheme()
        };
        this.themeCSS = new Map();
        this.transitionDuration = 300;
        this.init();
    }

    init() {
        // Listen for dashboard theme changes
        document.addEventListener('themeChange', (e) => {
            this.syncWithDashboard(e.detail.theme);
        });

        // Load external theme CSS
        this.loadThemeCSS();
    }

    setTheme(theme, animate = true) {
        if (!this.themes[theme]) {
            console.warn(`Theme "${theme}" not found, falling back to default`);
            theme = 'default';
        }

        const previousTheme = this.currentTheme;
        this.currentTheme = theme;

        // Apply theme with animation
        this.applyTheme(animate);

        // Dispatch custom event
        this.dispatchThemeChange(previousTheme, theme);
    }

    syncWithDashboard(dashboardTheme) {
        // Map dashboard themes to widget themes
        const themeMapping = {
            'default': 'default',
            'dark': 'dark',
            'matrix': 'matrix',
            'neocities': 'neocities'
        };

        const widgetTheme = themeMapping[dashboardTheme] || 'default';
        if (widgetTheme !== this.currentTheme) {
            this.setTheme(widgetTheme, true);
        }
    }

    applyTheme(animate = true) {
        const theme = this.themes[this.currentTheme] || this.themes.default;

        // Apply CSS variables
        this.applyCSSVariables(theme, animate);

        // Apply theme-specific effects
        this.applyThemeEffects(theme);

        // Update meta theme-color
        this.updateMetaThemeColor(theme.colors.primary);
    }

    applyCSSVariables(theme, animate = true) {
        const root = document.documentElement;

        // Set transition properties
        if (animate) {
            root.style.setProperty('--widget-transition-duration', theme.transitions.duration);
            root.style.setProperty('--widget-transition-easing', theme.transitions.easing);
        } else {
            root.style.setProperty('--widget-transition-duration', '0s');
        }

        // Apply colors
        Object.entries(theme.colors).forEach(([key, value]) => {
            root.style.setProperty(`--widget-${key}`, value);
        });

        // Apply typography
        Object.entries(theme.fonts).forEach(([key, value]) => {
            root.style.setProperty(`--widget-font-${key}`, value);
        });

        // Apply spacing
        Object.entries(theme.spacing).forEach(([key, value]) => {
            root.style.setProperty(`--widget-spacing-${key}`, value);
        });

        // Apply design tokens
        root.style.setProperty('--widget-border-radius', theme.borderRadius);
    }

    applyThemeEffects(theme) {
        // Remove existing theme classes
        const widget = document.querySelector('comment-widget');
        if (widget && widget.shadowRoot) {
            const app = widget.shadowRoot.querySelector('#indie-comments-app');
            if (app) {
                app.className = app.className.replace(/theme-\w+/g, '');
                app.classList.add(`theme-${this.currentTheme}`);
            }
        }

        // Apply theme-specific effects
        switch (this.currentTheme) {
            case 'matrix':
                this.applyMatrixEffects();
                break;
            case 'neocities':
                this.applyNeocitiesEffects();
                break;
            case 'dark':
                this.applyDarkEffects();
                break;
            case 'serene-mist':
                this.applySereneMistEffects();
                break;
            case 'neon-pulse':
                this.applyNeonPulseEffects();
                break;
            case 'geometric-prime':
                this.applyGeometricPrimeEffects();
                break;
            case 'forest-flow':
                this.applyForestFlowEffects();
                break;
            case 'digital-chaos':
                this.applyDigitalChaosEffects();
                break;
            default:
                this.applyDefaultEffects();
        }
    }

    applyMatrixEffects() {
        // Matrix-specific effects can be added here
        console.log('Matrix theme effects applied');
    }

    applyNeocitiesEffects() {
        // NeoCities-specific effects can be added here
        console.log('NeoCities theme effects applied');
    }

    applyDarkEffects() {
        // Dark theme-specific effects can be added here
        console.log('Dark theme effects applied');
    }

    applyDefaultEffects() {
        // Default theme-specific effects can be added here
        console.log('Default theme effects applied');
    }

    applySereneMistEffects() {
        // Organic breathing animation
        this.widgetElement.style.animation = 'serene-breath 4s ease-in-out infinite';
    }

    applyNeonPulseEffects() {
        // Pulsing neon glow
        this.widgetElement.style.animation = 'neon-pulse 2s ease-in-out infinite';
    }

    applyGeometricPrimeEffects() {
        // 3D geometric transforms
        this.widgetElement.style.animation = 'geometric-rotate 8s linear infinite';
    }

    applyForestFlowEffects() {
        // Flowing wave animation
        this.widgetElement.style.animation = 'forest-wave 6s ease-in-out infinite';
    }

    applyDigitalChaosEffects() {
        // Glitch and scan line effects
        this.widgetElement.style.animation = 'digital-glitch 0.3s ease-in-out infinite, scan-line 2s linear infinite';
    }

    updateMetaThemeColor(color) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = color;
    }

    dispatchThemeChange(previousTheme, newTheme) {
        document.dispatchEvent(new CustomEvent('commentWidgetThemeChange', {
            detail: {
                theme: newTheme,
                previousTheme: previousTheme,
                config: this.themes[newTheme]
            }
        }));
    }

    async loadThemeCSS() {
        // Load external theme CSS files
        const themeFiles = {
            'dark': '/frontend/static/css/themes/dark.css',
            'matrix': '/frontend/static/css/themes/matrix.css',
            'neocities': '/frontend/static/css/themes/neocities.css'
        };

        for (const [theme, file] of Object.entries(themeFiles)) {
            try {
                const response = await fetch(file);
                if (response.ok) {
                    const css = await response.text();
                    this.themeCSS.set(theme, css);
                }
            } catch (error) {
                console.warn(`Failed to load theme CSS for ${theme}:`, error);
            }
        }
    }

    getThemeCSS(theme) {
        return this.themeCSS.get(theme) || '';
    }

    // Theme definitions using CSS variables
    getDefaultTheme() {
        return `
            /* Default theme with CSS variables */
            .comment-widget {
                font-family: var(--widget-font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
                max-width: 680px;
                margin: 2rem auto;
                padding: 1.5rem;
                background: var(--widget-background, #fff);
                border: 1px solid var(--widget-border, #e0e0e0);
                border-radius: var(--widget-border-radius, 8px);
                box-shadow: 0 2px 10px var(--widget-shadow, rgba(0,0,0,0.1));
                color: var(--widget-text, #333);
                transition: var(--widget-transition, all 0.3s ease);
            }

            .comment-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid var(--widget-border, #e0e0e0);
            }

            .comment-header h3 {
                margin: 0;
                color: var(--widget-text, #333);
                font-size: 1.5rem;
                font-weight: 600;
            }

            .theme-selector {
                padding: 0.5rem;
                border: 1px solid var(--widget-border, #ddd);
                border-radius: var(--widget-border-radius, 4px);
                background: var(--widget-surface, #fff);
                color: var(--widget-text, #333);
                font-size: 0.9rem;
            }

            .comment-form {
                background: var(--widget-surface, #f8f9fa);
                padding: 1.5rem;
                border-radius: var(--widget-border-radius, 6px);
                margin-bottom: 2rem;
                border: 1px solid var(--widget-border, #e9ecef);
            }

            .form-group {
                margin-bottom: 1rem;
            }

            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid var(--widget-border, #ddd);
                border-radius: var(--widget-border-radius, 4px);
                font-size: 1rem;
                box-sizing: border-box;
                font-family: inherit;
                background: var(--widget-surface, #fff);
                color: var(--widget-text, #333);
                transition: var(--widget-transition, border-color 0.2s);
            }

            .form-group input:focus,
            .form-group textarea:focus {
                border-color: var(--widget-primary, #007cba);
                box-shadow: 0 0 0 0.2rem rgba(0, 124, 186, 0.25);
            }

            .form-group textarea {
                min-height: 100px;
                resize: vertical;
            }

            .form-actions {
                text-align: right;
            }

            .submit-btn {
                background: var(--widget-primary, #007cba);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: var(--widget-border-radius, 4px);
                font-size: 1rem;
                cursor: pointer;
                transition: var(--widget-transition, background 0.2s);
            }

            .submit-btn:hover {
                background: var(--widget-primary, #007cba);
                opacity: 0.9;
                transform: translateY(-1px);
            }

            .comment-list {
                margin-top: 1.5rem;
            }

            .comment-item {
                display: flex;
                padding: 1rem;
                margin-bottom: 1rem;
                background: var(--widget-surface, #fff);
                border: 1px solid var(--widget-border, #eee);
                border-radius: var(--widget-border-radius, 6px);
                border-left: 3px solid var(--widget-primary, #007cba);
                transition: var(--widget-transition, all 0.2s);
            }

            .comment-item:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px var(--widget-shadow, rgba(0,0,0,0.1));
            }

            .comment-item.level-1 {
                margin-left: 2rem;
                border-left-width: 2px;
                border-left-color: var(--widget-secondary, #888);
            }

            .comment-item.level-2 {
                margin-left: 3rem;
                border-left-width: 1px;
                border-left-color: var(--widget-border, #ccc);
            }

            .comment-avatar {
                margin-right: 1rem;
                flex-shrink: 0;
            }

            .avatar-placeholder {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: var(--widget-primary, #007cba);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 1.1rem;
            }

            .comment-content {
                flex: 1;
            }

            .comment-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
            }

            .comment-author {
                font-weight: 600;
                color: var(--widget-primary, #007cba);
            }

            .comment-date {
                color: var(--widget-text-muted, #888);
            }

            .comment-text {
                line-height: 1.6;
                color: var(--widget-text, #444);
                margin-bottom: 0.5rem;
            }

            .comment-actions {
                font-size: 0.8rem;
            }

            .reply-btn {
                background: none;
                border: none;
                color: var(--widget-primary, #007cba);
                cursor: pointer;
                text-decoration: underline;
                font-size: 0.8rem;
                transition: var(--widget-transition, color 0.2s);
            }

            .reply-btn:hover {
                color: var(--widget-primary, #007cba);
                opacity: 0.8;
            }

            .comment-replies {
                margin-top: 1rem;
                margin-left: 1rem;
            }

            .loading-state,
            .error-state,
            .empty-state {
                text-align: center;
                padding: 2rem;
                font-style: italic;
            }

            .loading-state {
                color: var(--widget-text-muted, #666);
            }

            .error-state {
                color: var(--widget-danger, #dc3545);
                background: rgba(220, 53, 69, 0.1);
                border: 1px solid var(--widget-danger, #dc3545);
                border-radius: var(--widget-border-radius, 4px);
            }

            .empty-state {
                color: var(--widget-text-muted, #666);
            }

            .spinner {
                border: 3px solid var(--widget-light, #f3f3f3);
                border-top: 3px solid var(--widget-primary, #007cba);
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            @media (max-width: 768px) {
                .comment-widget {
                    margin: 1rem;
                    padding: 1rem;
                }

                .comment-item.level-1,
                .comment-item.level-2 {
                    margin-left: 1rem;
                }

                .theme-selector {
                    margin-top: 0.5rem;
                    width: 100%;
                }

                .comment-header {
                    flex-direction: column;
                    align-items: stretch;
                }
            }
        `;
    }

    getDarkTheme() {
        return `
            .comment-widget {
                background: #2d2d2d;
                border-color: #444;
                color: #e0e0e0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            }

            .comment-header h3 {
                color: #e0e0e0;
            }

            .theme-selector {
                background: #3a3a3a;
                border-color: #555;
                color: #e0e0e0;
            }

            .comment-form {
                background: #3a3a3a;
                border-color: #555;
            }

            .form-group input,
            .form-group textarea {
                background: #3a3a3a;
                border-color: #555;
                color: #e0e0e0;
            }

            .submit-btn {
                background: #4fc3f7;
                color: #000;
            }

            .submit-btn:hover {
                background: #29b6f6;
            }

            .comment-item {
                background: #2d2d2d;
                border-color: #444;
                color: #e0e0e0;
                border-left-color: #4fc3f7;
            }

            .comment-item.level-1 {
                border-left-color: #888;
            }

            .comment-item.level-2 {
                border-left-color: #ccc;
            }

            .avatar-placeholder {
                background: #4fc3f7;
                color: #000;
            }

            .comment-author {
                color: #4fc3f7;
            }

            .comment-date {
                color: #b0b0b0;
            }

            .comment-text {
                color: #e0e0e0;
            }

            .reply-btn {
                color: #4fc3f7;
            }

            .reply-btn:hover {
                color: #29b6f6;
            }

            .loading-state,
            .empty-state {
                color: #b0b0b0;
            }

            .error-state {
                color: #ff6b6b;
                background: rgba(255, 107, 107, 0.1);
                border-color: rgba(255, 107, 107, 0.3);
            }
        `;
    }

    getMatrixTheme() {
        return `
            .comment-widget {
                background: #000;
                border-color: #0a0;
                color: #0f0;
                font-family: 'Courier New', monospace;
                box-shadow: 0 2px 10px rgba(0,255,0,0.1);
            }

            .comment-header h3 {
                color: #0f0;
            }

            .theme-selector {
                background: #010;
                border-color: #080;
                color: #0f0;
                font-family: 'Courier New', monospace;
            }

            .comment-form {
                background: #010;
                border-color: #080;
            }

            .form-group input,
            .form-group textarea {
                background: #010;
                border-color: #080;
                color: #0f0;
                font-family: 'Courier New', monospace;
            }

            .submit-btn {
                background: #0a0;
                color: #000;
                font-family: 'Courier New', monospace;
            }

            .submit-btn:hover {
                background: #0f0;
                box-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
            }

            .comment-item {
                background: #000;
                border-color: #0a0;
                color: #0f0;
                border-left-color: #0f0;
                font-family: 'Courier New', monospace;
            }

            .comment-item.level-1 {
                border-left-color: #080;
            }

            .comment-item.level-2 {
                border-left-color: #040;
            }

            .avatar-placeholder {
                background: #0f0;
                color: #000;
            }

            .comment-author {
                color: #0f0;
            }

            .comment-date {
                color: #6b7280;
            }

            .comment-text {
                color: #0f0;
            }

            .reply-btn {
                color: #0f0;
            }

            .reply-btn:hover {
                color: #0a0;
                text-shadow: 0 0 3px rgba(0, 255, 0, 0.5);
            }

            .loading-state,
            .empty-state {
                color: #6b7280;
            }

            .error-state {
                color: #ff4444;
                background: rgba(255, 68, 68, 0.1);
                border-color: rgba(255, 68, 68, 0.3);
            }
        `;
    }

    getNeocitiesTheme() {
        return `
            .comment-widget {
                background: #ccffff;
                border: 2px dashed #996699;
                color: #330033;
                box-shadow: 0 4px 15px rgba(153, 102, 153, 0.2);
            }

            .comment-header h3 {
                color: #330033;
            }

            .theme-selector {
                background: #ffff99;
                border: 2px dotted #669966;
                color: #330033;
            }

            .comment-form {
                background: #ffff99;
                border: 2px dotted #669966;
            }

            .form-group input,
            .form-group textarea {
                background: #ffff99;
                border: 2px dotted #669966;
                color: #330033;
            }

            .submit-btn {
                background: #ffccff;
                color: #330033;
                border: 2px solid #996699;
            }

            .submit-btn:hover {
                background: #ff99ff;
            }

            .comment-item {
                background: #ccffff;
                border: 2px dashed #996699;
                color: #330033;
                border-left: 4px solid #996699;
            }

            .comment-item.level-1 {
                border-left-color: #669966;
                border-left-style: dotted;
            }

            .comment-item.level-2 {
                border-left-color: #cc99ff;
                border-left-style: dashed;
            }

            .avatar-placeholder {
                background: #ffccff;
                color: #330033;
                border: 2px solid #996699;
            }

            .comment-author {
                color: #663399;
                font-weight: bold;
            }

            .comment-date {
                color: #666699;
            }

            .comment-text {
                color: #330033;
            }

            .reply-btn {
                color: #663399;
                background: #ffccff;
                border: 1px solid #996699;
                padding: 0.2rem 0.5rem;
                border-radius: 3px;
            }

            .reply-btn:hover {
                background: #ff99ff;
            }

            .loading-state,
            .empty-state {
                color: #666699;
            }

            .error-state {
                color: #cc0000;
                background: rgba(255, 204, 204, 0.7);
                border: 2px dashed #cc6666;
            }
        `;
    }

    getSereneMistTheme() {
        return {
            colors: {
                primary: '#8B9D77',
                secondary: '#A8B5A0',
                background: '#F8F9F7',
                surface: '#FFFFFF',
                text: '#4A5D3A',
                'text-muted': '#7A8F69',
                border: '#D4E2D0',
                light: '#F0F2EF',
                danger: '#C17D5F'
            },
            fonts: {
                family: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size: '14px',
                weight: '400'
            },
            spacing: {
                small: '8px',
                medium: '16px',
                large: '24px'
            },
            borderRadius: '12px',
            transitions: {
                duration: '0.4s',
                easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
            }
        };
    }

    getNeonPulseTheme() {
        return {
            colors: {
                primary: '#00FF88',
                secondary: '#FF0080',
                background: '#0A0A0A',
                surface: '#1A1A1A',
                text: '#FFFFFF',
                'text-muted': '#888888',
                border: '#333333',
                light: '#2A2A2A',
                danger: '#FF4444'
            },
            fonts: {
                family: "'JetBrains Mono', 'Courier New', monospace",
                size: '14px',
                weight: '400'
            },
            spacing: {
                small: '8px',
                medium: '16px',
                large: '24px'
            },
            borderRadius: '4px',
            transitions: {
                duration: '0.2s',
                easing: 'ease-out'
            }
        };
    }

    getGeometricPrimeTheme() {
        return {
            colors: {
                primary: '#FF6B35',
                secondary: '#F7931E',
                background: '#2C2C2C',
                surface: '#3A3A3A',
                text: '#FFFFFF',
                'text-muted': '#CCCCCC',
                border: '#555555',
                light: '#4A4A4A',
                danger: '#FF4444'
            },
            fonts: {
                family: "'IBM Plex Sans', sans-serif",
                size: '14px',
                weight: '500'
            },
            spacing: {
                small: '12px',
                medium: '20px',
                large: '32px'
            },
            borderRadius: '0px',
            transitions: {
                duration: '0.3s',
                easing: 'ease-in-out'
            }
        };
    }

    getForestFlowTheme() {
        return {
            colors: {
                primary: '#2D5A3D',
                secondary: '#4A7C59',
                background: '#F5F8F5',
                surface: '#FFFFFF',
                text: '#1A3D2A',
                'text-muted': '#5A8F6B',
                border: '#B8D4BB',
                light: '#E8F5E8',
                danger: '#8B4513'
            },
            fonts: {
                family: "'Crimson Text', serif",
                size: '15px',
                weight: '400'
            },
            spacing: {
                small: '10px',
                medium: '18px',
                large: '28px'
            },
            borderRadius: '16px',
            transitions: {
                duration: '0.5s',
                easing: 'ease-in-out'
            }
        };
    }

    getDigitalChaosTheme() {
        return {
            colors: {
                primary: '#FF00FF',
                secondary: '#00FFFF',
                background: '#000000',
                surface: '#0F0F0F',
                text: '#FFFFFF',
                'text-muted': '#AAAAAA',
                border: '#333333',
                light: '#1A1A1A',
                danger: '#FF0000'
            },
            fonts: {
                family: "'Share Tech Mono', monospace",
                size: '13px',
                weight: '400'
            },
            spacing: {
                small: '6px',
                medium: '12px',
                large: '18px'
            },
            borderRadius: '2px',
            transitions: {
                duration: '0.1s',
                easing: 'step-end'
            }
        };
    }
}