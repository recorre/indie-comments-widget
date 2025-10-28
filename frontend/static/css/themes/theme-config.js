/**
 * Theme Configuration System
 * Advanced theme management with smooth transitions
 */

class ThemeConfig {
    constructor() {
        this.themes = {
            'default': {
                name: 'Default',
                description: 'Clean and modern design',
                colors: {
                    primary: '#007cba',
                    secondary: '#6c757d',
                    success: '#28a745',
                    danger: '#dc3545',
                    warning: '#ffc107',
                    info: '#17a2b8',
                    light: '#f8f9fa',
                    dark: '#343a40',
                    background: '#ffffff',
                    surface: '#f8f9fa',
                    text: '#333333',
                    textMuted: '#6c757d',
                    border: '#e0e0e0',
                    shadow: 'rgba(0,0,0,0.1)'
                },
                fonts: {
                    family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    size: '16px',
                    weight: '400'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '8px',
                transitions: {
                    duration: '0.3s',
                    easing: 'ease-in-out'
                }
            },
            'dark': {
                name: 'Dark',
                description: 'High contrast dark theme',
                colors: {
                    primary: '#4fc3f7',
                    secondary: '#b0b0b0',
                    success: '#4caf50',
                    danger: '#f44336',
                    warning: '#ff9800',
                    info: '#2196f3',
                    light: '#2d2d2d',
                    dark: '#1a1a1a',
                    background: '#2d2d2d',
                    surface: '#3a3a3a',
                    text: '#e0e0e0',
                    textMuted: '#b0b0b0',
                    border: '#444444',
                    shadow: 'rgba(0,0,0,0.3)'
                },
                fonts: {
                    family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                    size: '16px',
                    weight: '400'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '8px',
                transitions: {
                    duration: '0.3s',
                    easing: 'ease-in-out'
                }
            },
            'matrix': {
                name: 'Matrix',
                description: 'Retro terminal aesthetic',
                colors: {
                    primary: '#0f0',
                    secondary: '#6b7280',
                    success: '#00ff00',
                    danger: '#ff4444',
                    warning: '#ffff00',
                    info: '#00ffff',
                    light: '#000000',
                    dark: '#000000',
                    background: '#000000',
                    surface: '#010101',
                    text: '#0f0',
                    textMuted: '#6b7280',
                    border: '#0a0',
                    shadow: 'rgba(0,255,0,0.1)'
                },
                fonts: {
                    family: '"Courier New", monospace',
                    size: '16px',
                    weight: '400'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '0px',
                transitions: {
                    duration: '0.2s',
                    easing: 'linear'
                }
            },
            'neocities': {
                name: 'NeoCities',
                description: 'Playful retro web aesthetic',
                colors: {
                    primary: '#996699',
                    secondary: '#666699',
                    success: '#669966',
                    danger: '#cc6666',
                    warning: '#ffccff',
                    info: '#ccffff',
                    light: '#ccffff',
                    dark: '#330033',
                    background: '#ccffff',
                    surface: '#ffff99',
                    text: '#330033',
                    textMuted: '#666699',
                    border: '#996699',
                    shadow: 'rgba(153,102,153,0.2)'
                },
                fonts: {
                    family: '"Comic Sans MS", cursive, sans-serif',
                    size: '16px',
                    weight: '400'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '15px',
                transitions: {
                    duration: '0.4s',
                    easing: 'ease-out'
                }
            },
            'serene-mist': {
                name: 'Serene Mist',
                description: 'Organic minimalism inspired by zen aesthetics',
                colors: {
                    primary: '#8b7e74',
                    secondary: '#5a524c',
                    success: '#7fb069',
                    danger: '#d4a373',
                    warning: '#c9b8a8',
                    info: '#3d3935',
                    light: '#f4f1ea',
                    dark: '#3d3935',
                    background: '#f4f1ea',
                    surface: '#f4f1ea',
                    text: '#3d3935',
                    textMuted: '#8b7e74',
                    border: '#c9b8a8',
                    shadow: 'rgba(61,57,53,0.1)'
                },
                fonts: {
                    family: '"Noto Serif", serif',
                    size: '16px',
                    weight: '400'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '12px',
                transitions: {
                    duration: '0.8s',
                    easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
                }
            },
            'neon-pulse': {
                name: 'Neon Pulse',
                description: 'Vibrant cyberpunk with pulsing energy',
                colors: {
                    primary: '#ffd700',
                    secondary: '#ff6b35',
                    success: '#00d9ff',
                    danger: '#ff0080',
                    warning: '#ffff00',
                    info: '#8b2e8f',
                    light: '#1a0a2e',
                    dark: '#1a0a2e',
                    background: '#1a0a2e',
                    surface: '#1a0a2e',
                    text: '#ffd700',
                    textMuted: '#8b2e8f',
                    border: '#ffd700',
                    shadow: 'rgba(255,215,0,0.3)'
                },
                fonts: {
                    family: '"Montserrat", sans-serif',
                    size: '16px',
                    weight: '700'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '4px',
                transitions: {
                    duration: '0.3s',
                    easing: 'ease-in-out'
                }
            },
            'geometric-prime': {
                name: 'Geometric Prime',
                description: 'Retro functionalism with primary shapes',
                colors: {
                    primary: '#ff4444',
                    secondary: '#2b5caa',
                    success: '#f0e68c',
                    danger: '#ff4444',
                    warning: '#ffff00',
                    info: '#2b5caa',
                    light: '#e8e8e8',
                    dark: '#1a1a1a',
                    background: '#f0e68c',
                    surface: '#e8e8e8',
                    text: '#1a1a1a',
                    textMuted: '#666666',
                    border: '#1a1a1a',
                    shadow: 'rgba(0,0,0,0.2)'
                },
                fonts: {
                    family: '"Futura", sans-serif',
                    size: '16px',
                    weight: '500'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '0px',
                transitions: {
                    duration: '0.4s',
                    easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
                }
            },
            'forest-flow': {
                name: 'Forest Flow',
                description: 'Natural organic design with flowing movement',
                colors: {
                    primary: '#7fb069',
                    secondary: '#2d6a4f',
                    success: '#7fb069',
                    danger: '#d4a373',
                    warning: '#e8ddb5',
                    info: '#0d3b2e',
                    light: '#e8ddb5',
                    dark: '#0d3b2e',
                    background: '#0d3b2e',
                    surface: '#2d6a4f',
                    text: '#e8ddb5',
                    textMuted: '#7fb069',
                    border: '#7fb069',
                    shadow: 'rgba(127,176,105,0.2)'
                },
                fonts: {
                    family: '"Merriweather", serif',
                    size: '16px',
                    weight: '400'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '12px',
                transitions: {
                    duration: '0.6s',
                    easing: 'ease-in-out'
                }
            },
            'digital-chaos': {
                name: 'Digital Chaos',
                description: 'Futuristic glitch effects with cyberpunk aesthetics',
                colors: {
                    primary: '#00ff41',
                    secondary: '#ff0080',
                    success: '#00d4ff',
                    danger: '#ff0080',
                    warning: '#ffff00',
                    info: '#00d4ff',
                    light: '#0a0e27',
                    dark: '#0a0e27',
                    background: '#0a0e27',
                    surface: '#0a0e27',
                    text: '#00ff41',
                    textMuted: '#6b7280',
                    border: '#00ff41',
                    shadow: 'rgba(0,255,65,0.1)'
                },
                fonts: {
                    family: '"Source Code Pro", monospace',
                    size: '16px',
                    weight: '400'
                },
                spacing: {
                    xs: '0.25rem',
                    sm: '0.5rem',
                    md: '1rem',
                    lg: '1.5rem',
                    xl: '2rem'
                },
                borderRadius: '2px',
                transitions: {
                    duration: '0.2s',
                    easing: 'steps(4, end)'
                }
            }
        };

        this.currentTheme = 'default';
        this.transitionDuration = 300;
        this.init();
    }

    init() {
        // Load saved theme
        const savedTheme = localStorage.getItem('comment-widget-theme') || 'default';
        this.setTheme(savedTheme, false);

        // Listen for system theme changes
        this.watchSystemTheme();
    }

    setTheme(themeName, animate = true) {
        if (!this.themes[themeName]) {
            console.warn(`Theme "${themeName}" not found, falling back to default`);
            themeName = 'default';
        }

        const previousTheme = this.currentTheme;
        this.currentTheme = themeName;
        const theme = this.themes[themeName];

        // Apply theme with optional animation
        this.applyTheme(theme, animate);

        // Save preference
        localStorage.setItem('comment-widget-theme', themeName);

        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('themeChange', {
            detail: {
                theme: themeName,
                previousTheme: previousTheme,
                config: theme
            }
        }));
    }

    applyTheme(theme, animate = true) {
        const root = document.documentElement;

        // Set transition duration
        if (animate) {
            root.style.setProperty('--theme-transition-duration', theme.transitions.duration);
            root.style.setProperty('--theme-transition-easing', theme.transitions.easing);
        } else {
            root.style.setProperty('--theme-transition-duration', '0s');
            root.style.setProperty('--theme-transition-easing', 'linear');
        }

        // Apply colors
        Object.entries(theme.colors).forEach(([key, value]) => {
            root.style.setProperty(`--theme-${key}`, value);
        });

        // Apply fonts
        root.style.setProperty('--theme-font-family', theme.fonts.family);
        root.style.setProperty('--theme-font-size', theme.fonts.size);
        root.style.setProperty('--theme-font-weight', theme.fonts.weight);

        // Apply spacing
        Object.entries(theme.spacing).forEach(([key, value]) => {
            root.style.setProperty(`--theme-spacing-${key}`, value);
        });

        // Apply design tokens
        root.style.setProperty('--theme-border-radius', theme.borderRadius);

        // Add theme class to body
        document.body.className = document.body.className.replace(/theme-\w+/g, '');
        document.body.classList.add(`theme-${this.currentTheme}`);

        // Update meta theme-color
        this.updateMetaThemeColor(theme.colors.primary);
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

    watchSystemTheme() {
        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

            mediaQuery.addEventListener('change', (e) => {
                if (localStorage.getItem('comment-widget-theme') === 'auto') {
                    this.setTheme(e.matches ? 'dark' : 'default');
                }
            });
        }
    }

    getThemeConfig(themeName = null) {
        return this.themes[themeName || this.currentTheme];
    }

    getAllThemes() {
        return Object.keys(this.themes).map(key => ({
            id: key,
            ...this.themes[key]
        }));
    }

    createCustomTheme(baseTheme, customizations) {
        const base = this.themes[baseTheme] || this.themes.default;
        return {
            ...base,
            ...customizations,
            name: customizations.name || `${base.name} Custom`,
            description: customizations.description || `Customized ${base.description.toLowerCase()}`
        };
    }

    exportTheme(themeName) {
        const theme = this.getThemeConfig(themeName);
        return {
            name: theme.name,
            description: theme.description,
            colors: theme.colors,
            fonts: theme.fonts,
            spacing: theme.spacing,
            borderRadius: theme.borderRadius,
            transitions: theme.transitions
        };
    }

    importTheme(themeData) {
        const themeName = themeData.name.toLowerCase().replace(/\s+/g, '-');
        this.themes[themeName] = themeData;
        return themeName;
    }

    // Animation utilities
    fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';

        requestAnimationFrame(() => {
            element.style.transition = `opacity ${duration}ms ease-in`;
            element.style.opacity = '1';
        });
    }

    fadeOut(element, duration = 300) {
        element.style.transition = `opacity ${duration}ms ease-out`;
        element.style.opacity = '0';

        setTimeout(() => {
            element.style.display = 'none';
        }, duration);
    }

    slideIn(element, direction = 'left', duration = 300) {
        const translations = {
            left: 'translateX(-100%)',
            right: 'translateX(100%)',
            up: 'translateY(-100%)',
            down: 'translateY(100%)'
        };

        element.style.transform = translations[direction];
        element.style.display = 'block';

        requestAnimationFrame(() => {
            element.style.transition = `transform ${duration}ms ease-out`;
            element.style.transform = 'translate(0, 0)';
        });
    }

    // Color utilities
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }

    lightenColor(color, percent) {
        const rgb = this.hexToRgb(color);
        if (!rgb) return color;

        const { r, g, b } = rgb;
        const factor = percent / 100;

        return this.rgbToHex(
            Math.min(255, Math.round(r + (255 - r) * factor)),
            Math.min(255, Math.round(g + (255 - g) * factor)),
            Math.min(255, Math.round(b + (255 - b) * factor))
        );
    }

    darkenColor(color, percent) {
        const rgb = this.hexToRgb(color);
        if (!rgb) return color;

        const { r, g, b } = rgb;
        const factor = percent / 100;

        return this.rgbToHex(
            Math.max(0, Math.round(r - r * factor)),
            Math.max(0, Math.round(g - g * factor)),
            Math.max(0, Math.round(b - b * factor))
        );
    }
}

// Global theme instance
window.themeConfig = new ThemeConfig();

// Auto-initialize theme system
document.addEventListener('DOMContentLoaded', () => {
    console.log('Theme system initialized with', window.themeConfig.getAllThemes().length, 'themes');
});