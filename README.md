# Indie Comments Widget

**Add privacy-focused comments to any website in under 60 seconds.** No server required, works on static sites like Neocities, GitHub Pages, and Hugo.

[![Demo](https://img.shields.io/badge/Demo-Live-brightgreen)](https://nocodebackend.vercel.app/demo.html)
[![Size](https://img.shields.io/badge/Size-15KB-blue)](https://cdn.jsdelivr.net/gh/your-repo/indie-comments-widget/dist/indie-comments-widget.min.js)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## ✨ Key Features

- **🚀 Ultra-Lightweight**: ~15KB minified, loads instantly
- **🔒 Privacy-First**: No tracking, no ads, user-controlled data
- **⚡ Fast**: Smart caching, instant loading
- **🎨 Themed**: Light/dark themes, fully customizable
- **📱 Responsive**: Works perfectly on mobile
- **🔧 No-Code**: Simple HTML embed, zero configuration
- **🌐 Static-Friendly**: Perfect for Neocities, GitHub Pages, Hugo

## 🚀 Quick Install

Add this to your HTML:

```html
<!-- Indie Comments Widget -->
<div id="indie-comments"></div>

<script src="https://cdn.jsdelivr.net/npm/dompurify@3.2.7/dist/purify.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/your-repo/indie-comments-widget@main/dist/indie-comments-widget.min.js"></script>

<script>
  new IndieCommentsWidget('#indie-comments', {
    siteId: 'your-site-id',
    pageId: 'current-page',
    limit: 10,
    theme: 'light'
  }).init();
</script>
```

That's it! Your privacy-focused comment system is now live.

## 🔧 Compatibility

Works everywhere:
- ✅ Neocities
- ✅ GitHub Pages
- ✅ Hugo, Jekyll, Pelican
- ✅ WordPress, Squarespace
- ✅ Any static HTML site
- ✅ Modern browsers (Chrome 90+, Firefox 88+, Safari 14+)

## 🛡️ Privacy Features

- **No Tracking**: Zero analytics or third-party tracking
- **User Control**: Comments are owned by your users
- **GDPR Compliant**: No personal data collection
- **Self-Hosted Option**: Host your own comment data

## � Documentation

- **[Interactive Demo](https://nocodebackend.vercel.app/demo.html)** - Try it live
- **[Widget Guide](docs/WIDGET_GUIDE.md)** - Configuration options
- **[API Docs](docs/api_docs.md)** - Backend endpoints
- **[Theme Guide](frontend/static/css/themes/README.md)** - Customization

## 💝 Support the Project

If this privacy-focused comment widget helps you build better communities, consider supporting ongoing development:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-donate-yellow)](https://www.buymeacoffee.com/yourusername)

Your support helps maintain the free API and keeps the widget ad-free and privacy-focused.

## 🛠 Development

```bash
# Clone and setup
git clone https://github.com/your-repo/indie-comments-widget.git
cd indie-comments-widget

# Backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn api.index:app --reload

# Frontend (Flask)
cd ../frontend
pip install -r requirements.txt
python app.py

# Widget build
cd ../widget
npm install
npm run build
```

## 📊 Performance

- **Bundle Size**: 15KB minified + gzipped
- **API Response**: <100ms (cached), <2s (fresh)
- **Privacy**: Zero tracking, user-controlled data
- **Security**: DOMPurify XSS protection

## 🤝 Contributing

Contributions welcome! Open issues for bugs/features, submit PRs for improvements.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

*Built for the indie web community - privacy-first, user-owned comments for everyone.*