# Comment Widget v2.0

A modern, embeddable comment system built as a Web Component. Easy to integrate, highly customizable, and production-ready.

## ✨ Features

- 🚀 **Easy Integration** - Just add a script tag and custom element
- 🎨 **Multiple Themes** - Default, Dark, Matrix, and NeoCities themes
- 📱 **Responsive Design** - Works perfectly on all devices
- 🔄 **Real-time Updates** - Live comment loading and submission
- 🧵 **Nested Replies** - Configurable reply depth
- 🛡️ **Security** - Input validation and XSS protection
- 🎯 **Web Component** - Shadow DOM for style isolation
- 🔧 **Customizable** - Extensive configuration options

## 🚀 Quick Start

### 1. Include the Widget

```html
<!-- Development -->
<script type="module" src="/widget/src/widget.js"></script>

<!-- Production -->
<script src="/widget/dist/comment-widget.min.js"></script>
```

### 2. Add to Your Page

```html
<!-- Basic usage -->
<comment-widget thread-id="my-page"></comment-widget>

<!-- With configuration -->
<comment-widget
    thread-id="blog-post-1"
    api-base-url="https://my-api.com"
    theme="dark"
    max-depth="5">
</comment-widget>
```

## ⚙️ Configuration

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `thread-id` | string | auto-generated | Unique identifier for the comment thread |
| `api-base-url` | string | production backend | API endpoint URL |
| `theme` | string | 'default' | Theme: default, dark, matrix, neocities |
| `max-depth` | number | 3 | Maximum nesting level for replies |

## 🎨 Themes

### Default
Clean and modern design with excellent readability.

### Dark
Perfect for dark websites with high contrast.

### Matrix
Retro terminal-style theme with green-on-black aesthetics.

### NeoCities
Playful, colorful theme inspired by old web aesthetics.

## 🔧 JavaScript API

```javascript
// Get widget instance
const widget = document.querySelector('comment-widget');

// Refresh comments
widget.refresh();

// Get current comments
const comments = widget.getComments();

// Change theme
widget.setTheme('dark');

// Listen for events
document.addEventListener('commentWidgetThemeChange', (event) => {
    console.log('Theme changed to:', event.detail.theme);
});
```

## 🏗️ Development

### Setup

```bash
cd widget/
npm install
```

### Development Server

```bash
npm run dev
```

Visit `http://localhost:3000` to see the embed example.

### Building

```bash
npm run build
```

This creates optimized bundles in the `dist/` directory:

- `comment-widget.js` - ES modules (development)
- `comment-widget.min.js` - ES modules (production)
- `comment-widget.umd.js` - UMD format
- `comment-widget.umd.min.js` - UMD format (minified)

## 📁 Project Structure

```
widget/
├── src/                    # Source code
│   ├── widget.js          # Main widget component
│   ├── api.js             # API client
│   ├── renderer.js        # HTML rendering
│   ├── theme-manager.js   # Theme handling
│   └── utils.js           # Utility functions
├── dist/                  # Built files
├── embed.html             # Development example
├── package.json           # Dependencies and scripts
├── rollup.config.js       # Build configuration
└── README.md              # This file
```

## 🌐 API Integration

The widget integrates with the FastAPI backend via REST endpoints:

- `GET /widget/comments/{thread_id}` - Load comments
- `POST /comments` - Submit new comment
- `PUT /comments/{id}/moderate` - Moderate comments (admin)

## 🔒 Security

- Input validation and sanitization
- XSS protection via DOMPurify (recommended)
- Email validation
- Rate limiting ready (implement on backend)

## 🎯 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🐛 Issues

Report bugs and feature requests on the GitHub issues page.

## 📞 Support

For support, email support@commentwidget.com or join our Discord community.