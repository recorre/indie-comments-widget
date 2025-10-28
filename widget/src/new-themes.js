/**
 * New Creative Themes for Comment Widget
 * 5 Additional themes with maximum diversity
 */

export const newThemes = {
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

// Theme CSS generators
export function getSereneMistTheme() {
    return `
        .comment-widget {
            background: var(--widget-background, #f4f1ea);
            border: 1px solid var(--widget-border, #c9b8a8);
            color: var(--widget-text, #3d3935);
            font-family: var(--widget-font-family, 'Noto Serif', serif);
            box-shadow: 0 2px 10px var(--widget-shadow, rgba(61,57,53,0.1));
            animation: breath 4s ease-in-out infinite;
        }

        @keyframes breath {
            0%, 100% { transform: translateY(0); opacity: 0.95; }
            50% { transform: translateY(-3px); opacity: 1; }
        }

        .comment-header h3 {
            color: var(--widget-text, #3d3935);
        }

        .theme-selector {
            background: var(--widget-surface, #f4f1ea);
            border: 1px solid var(--widget-border, #c9b8a8);
            color: var(--widget-text, #3d3935);
        }

        .comment-form {
            background: var(--widget-surface, #f4f1ea);
            border: 1px solid var(--widget-border, #c9b8a8);
        }

        .form-group input,
        .form-group textarea {
            background: var(--widget-surface, #f4f1ea);
            border: 1px solid var(--widget-border, #c9b8a8);
            color: var(--widget-text, #3d3935);
        }

        .submit-btn {
            background: var(--widget-primary, #8b7e74);
            color: var(--widget-background, #f4f1ea);
        }

        .submit-btn:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        .comment-item {
            background: var(--widget-surface, #f4f1ea);
            border: 1px solid var(--widget-border, #c9b8a8);
            color: var(--widget-text, #3d3935);
            border-left: 3px solid var(--widget-primary, #8b7e74);
        }

        .avatar-placeholder {
            background: var(--widget-primary, #8b7e74);
            color: var(--widget-background, #f4f1ea);
        }

        .comment-author {
            color: var(--widget-primary, #8b7e74);
        }

        .comment-date {
            color: var(--widget-text-muted, #8b7e74);
        }

        .comment-text {
            color: var(--widget-text, #3d3935);
        }

        .reply-btn {
            color: var(--widget-primary, #8b7e74);
        }

        .reply-btn:hover {
            opacity: 0.8;
        }
    `;
}

export function getNeonPulseTheme() {
    return `
        .comment-widget {
            background: var(--widget-background, #1a0a2e);
            border: 1px solid var(--widget-border, #ffd700);
            color: var(--widget-text, #ffd700);
            font-family: var(--widget-font-family, 'Montserrat', sans-serif);
            box-shadow: 0 0 20px var(--widget-shadow, rgba(255,215,0,0.3));
            animation: pulse-glow 2s ease-in-out infinite;
        }

        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 5px rgba(255, 215, 0, 0.3); }
            50% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.8); }
        }

        .comment-header h3 {
            color: var(--widget-text, #ffd700);
            text-shadow: 0 0 10px var(--widget-primary, #ffd700);
        }

        .theme-selector {
            background: var(--widget-surface, #1a0a2e);
            border: 1px solid var(--widget-border, #ffd700);
            color: var(--widget-text, #ffd700);
        }

        .comment-form {
            background: var(--widget-surface, #1a0a2e);
            border: 1px solid var(--widget-border, #ffd700);
        }

        .form-group input,
        .form-group textarea {
            background: var(--widget-surface, #1a0a2e);
            border: 1px solid var(--widget-border, #ffd700);
            color: var(--widget-text, #ffd700);
        }

        .submit-btn {
            background: var(--widget-primary, #ffd700);
            color: var(--widget-background, #1a0a2e);
            animation: glitch 0.3s steps(2, end);
        }

        .submit-btn:hover {
            animation: glitch 0.3s steps(2, end);
            background: linear-gradient(90deg, var(--widget-secondary, #ff6b35), var(--widget-success, #00d9ff));
        }

        @keyframes glitch {
            0% { transform: translate(0); }
            33% { transform: translate(-2px, 2px); }
            66% { transform: translate(2px, -2px); }
        }

        .comment-item {
            background: var(--widget-surface, #1a0a2e);
            border: 1px solid var(--widget-border, #ffd700);
            color: var(--widget-text, #ffd700);
            border-left: 3px solid var(--widget-primary, #ffd700);
        }

        .avatar-placeholder {
            background: var(--widget-primary, #ffd700);
            color: var(--widget-background, #1a0a2e);
        }

        .comment-author {
            color: var(--widget-primary, #ffd700);
        }

        .comment-date {
            color: var(--widget-text-muted, #8b2e8f);
        }

        .comment-text {
            color: var(--widget-text, #ffd700);
        }

        .reply-btn {
            color: var(--widget-primary, #ffd700);
        }

        .reply-btn:hover {
            text-shadow: 0 0 5px var(--widget-primary, #ffd700);
        }
    `;
}

export function getGeometricPrimeTheme() {
    return `
        .comment-widget {
            background: var(--widget-background, #f0e68c);
            border: 1px solid var(--widget-border, #1a1a1a);
            color: var(--widget-text, #1a1a1a);
            font-family: var(--widget-font-family, 'Futura', sans-serif);
            transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        .comment-widget:hover {
            transform: perspective(500px) rotateY(5deg) rotateX(2deg);
            box-shadow: -8px 8px 0 var(--widget-primary, #ff4444);
        }

        .comment-header h3 {
            color: var(--widget-text, #1a1a1a);
        }

        .theme-selector {
            background: var(--widget-surface, #e8e8e8);
            border: 1px solid var(--widget-border, #1a1a1a);
            color: var(--widget-text, #1a1a1a);
            clip-path: polygon(10% 0, 100% 0, 90% 100%, 0 100%);
        }

        .comment-form {
            background: var(--widget-surface, #e8e8e8);
            border: 1px solid var(--widget-border, #1a1a1a);
        }

        .form-group input,
        .form-group textarea {
            background: var(--widget-surface, #e8e8e8);
            border: 1px solid var(--widget-border, #1a1a1a);
            color: var(--widget-text, #1a1a1a);
        }

        .submit-btn {
            background: var(--widget-primary, #ff4444);
            color: var(--widget-background, #f0e68c);
            clip-path: polygon(10% 0, 100% 0, 90% 100%, 0 100%);
        }

        .submit-btn:hover {
            transform: perspective(500px) rotateY(-5deg) rotateX(-2deg);
        }

        .comment-item {
            background: var(--widget-surface, #e8e8e8);
            border: 1px solid var(--widget-border, #1a1a1a);
            color: var(--widget-text, #1a1a1a);
            border-left: 3px solid var(--widget-primary, #ff4444);
        }

        .comment-item:hover {
            transform: perspective(500px) rotateY(5deg) rotateX(2deg);
            box-shadow: -8px 8px 0 var(--widget-primary, #ff4444);
        }

        .avatar-placeholder {
            background: var(--widget-primary, #ff4444);
            color: var(--widget-background, #f0e68c);
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
        }

        .comment-author {
            color: var(--widget-primary, #ff4444);
        }

        .comment-date {
            color: var(--widget-text-muted, #666666);
        }

        .comment-text {
            color: var(--widget-text, #1a1a1a);
        }

        .reply-btn {
            color: var(--widget-primary, #ff4444);
            clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%);
        }
    `;
}

export function getForestFlowTheme() {
    return `
        .comment-widget {
            background: var(--widget-background, #0d3b2e);
            border: 1px solid var(--widget-border, #7fb069);
            color: var(--widget-text, #e8ddb5);
            font-family: var(--widget-font-family, 'Merriweather', serif);
            animation: wave 3s ease-in-out infinite;
        }

        @keyframes wave {
            0%, 100% { transform: translateX(0) skewX(0deg); }
            50% { transform: translateX(5px) skewX(1deg); }
        }

        .comment-header h3 {
            color: var(--widget-text, #e8ddb5);
        }

        .theme-selector {
            background: var(--widget-surface, #2d6a4f);
            border: 1px solid var(--widget-border, #7fb069);
            color: var(--widget-text, #e8ddb5);
        }

        .comment-form {
            background: var(--widget-surface, #2d6a4f);
            border: 1px solid var(--widget-border, #7fb069);
        }

        .form-group input,
        .form-group textarea {
            background: var(--widget-surface, #2d6a4f);
            border: 1px solid var(--widget-border, #7fb069);
            color: var(--widget-text, #e8ddb5);
        }

        .submit-btn {
            background: var(--widget-primary, #7fb069);
            color: var(--widget-background, #0d3b2e);
        }

        .submit-btn:hover {
            transform: translateX(5px) skewX(1deg);
        }

        .comment-item {
            background: var(--widget-surface, #2d6a4f);
            border: 1px solid var(--widget-border, #7fb069);
            color: var(--widget-text, #e8ddb5);
            border-left: 3px solid var(--widget-primary, #7fb069);
            border-radius: 12px 2px 12px 2px;
            background: linear-gradient(135deg, rgba(127, 176, 105, 0.2), transparent);
        }

        .comment-item:hover {
            transform: translateX(5px) skewX(1deg);
        }

        .avatar-placeholder {
            background: var(--widget-primary, #7fb069);
            color: var(--widget-background, #0d3b2e);
            border-radius: 12px 2px 12px 2px;
        }

        .comment-author {
            color: var(--widget-primary, #7fb069);
        }

        .comment-date {
            color: var(--widget-text-muted, #7fb069);
        }

        .comment-text {
            color: var(--widget-text, #e8ddb5);
        }

        .reply-btn {
            color: var(--widget-primary, #7fb069);
        }

        .reply-btn:hover {
            transform: translateX(3px);
        }
    `;
}

export function getDigitalChaosTheme() {
    return `
        .comment-widget {
            background: var(--widget-background, #0a0e27);
            border: 1px solid var(--widget-border, #00ff41);
            color: var(--widget-text, #00ff41);
            font-family: var(--widget-font-family, 'Source Code Pro', monospace);
            background: repeating-linear-gradient(
                0deg, transparent, transparent 2px, rgba(0, 255, 65, 0.03) 3px
            );
            animation: scan 4s linear infinite;
        }

        @keyframes scan {
            0%, 100% { background-position: 0 0; }
            50% { background-position: 0 100%; }
        }

        .comment-header h3 {
            color: var(--widget-text, #00ff41);
            text-shadow: 0 0 5px var(--widget-primary, #00ff41);
        }

        .theme-selector {
            background: var(--widget-surface, #0a0e27);
            border: 1px solid var(--widget-border, #00ff41);
            color: var(--widget-text, #00ff41);
        }

        .comment-form {
            background: var(--widget-surface, #0a0e27);
            border: 1px solid var(--widget-border, #00ff41);
        }

        .form-group input,
        .form-group textarea {
            background: var(--widget-surface, #0a0e27);
            border: 1px solid var(--widget-border, #00ff41);
            color: var(--widget-text, #00ff41);
        }

        .submit-btn {
            background: var(--widget-primary, #00ff41);
            color: var(--widget-background, #0a0e27);
            text-shadow: 2px 0 var(--widget-secondary, #ff0080), -2px 0 var(--widget-success, #00d4ff);
            animation: scan 4s linear infinite;
        }

        .submit-btn:hover {
            animation: magnetic-glitch 0.5s steps(4);
        }

        @keyframes magnetic-glitch {
            0% { transform: translate(0); filter: hue-rotate(0deg); }
            25% { transform: translate(-3px, 2px); filter: hue-rotate(90deg); }
            50% { transform: translate(3px, -2px); filter: hue-rotate(180deg); }
            75% { transform: translate(-2px, -3px); filter: hue-rotate(270deg); }
        }

        .comment-item {
            background: var(--widget-surface, #0a0e27);
            border: 1px solid var(--widget-border, #00ff41);
            color: var(--widget-text, #00ff41);
            border-left: 3px solid var(--widget-primary, #00ff41);
        }

        .comment-item:hover {
            animation: magnetic-glitch 0.5s steps(4);
        }

        .avatar-placeholder {
            background: var(--widget-primary, #00ff41);
            color: var(--widget-background, #0a0e27);
        }

        .comment-author {
            color: var(--widget-primary, #00ff41);
        }

        .comment-date {
            color: var(--widget-text-muted, #6b7280);
        }

        .comment-text {
            color: var(--widget-text, #00ff41);
        }

        .reply-btn {
            color: var(--widget-primary, #00ff41);
        }

        .reply-btn:hover {
            text-shadow: 0 0 5px var(--widget-primary, #00ff41);
        }
    `;
}