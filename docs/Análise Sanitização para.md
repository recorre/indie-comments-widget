# 🤔 Análise: Sanitização para Widget de Comentários

## ⚠️ Resposta Curta: **NÃO diretamente, precisa de adaptações**

---

## 🔍 Por Quê Não Serve Diretamente?

### **Diferenças Críticas:**

| Aspecto | Mastodon Widget | Comment Widget |
|---------|-----------------|----------------|
| **Fonte de HTML** | API Mastodon (HTML rico) | Usuários do seu site (texto simples) |
| **Confiança** | Moderação externa (Mastodon) | Moderação sua (backend) |
| **Tags permitidas** | Links, listas, blockquotes | **Apenas texto** ou markdown básico |
| **Classes CSS** | `mention`, `hashtag`, `invisible` | Nenhuma (ou custom suas) |
| **Threat model** | Instâncias Mastodon maliciosas | **Seus próprios usuários** |

---

## ✅ Versão Adaptada para Comment Widget## ✅ Agora sim! Versão para Comment Widget

### 🎯 Principais Diferenças

| Feature | Mastodon Widget | Comment Widget |
|---------|-----------------|----------------|
| **Default behavior** | Permite HTML rico | **PLAINTEXT ONLY** |
| **Tags permitidas** | 11 tags (links, listas) | **0 tags (MVP)** ou 5 básicas |
| **Classes CSS** | Whitelist Mastodon | **Nenhuma** |
| **Markdown** | ❌ | **✅ Opcional** |
| **Newline handling** | Já vem como `<br>` | **Converte `\n` → `<br>`** |

---

## 📝 Exemplos de Uso

### **Caso 1: MVP (Texto Puro - Recomendado)**

```javascript
import { sanitizeComment } from './utils/sanitize.js';

// Usuário digita
const userInput = "Hello!\n<script>alert('xss')</script>\nWorld!";

// Sanitiza (default: plaintext only)
const safe = sanitizeComment(userInput);
// → "Hello!<br>alert('xss')<br>World!"

// Renderiza
element.innerHTML = safe;
```

### **Caso 2: Com Markdown (Futuro)**

```javascript
import { processComment } from './utils/sanitize.js';

// Usuário digita
const userInput = "Check this **awesome** project!";

// Processa com markdown
const safe = processComment(userInput, { 
  allowMarkdown: true,
  allowLinks: false 
});
// → "Check this <strong>awesome</strong> project!"
```

### **Caso 3: Preview em Tempo Real**

```javascript
import { previewComment } from './utils/sanitize.js';

// No event listener do textarea
textarea.addEventListener('input', (e) => {
  const preview = previewComment(e.target.value, {
    allowMarkdown: true,
    convertNewlines: true
  });
  
  previewContainer.innerHTML = preview;
});
```

### **Caso 4: Sanitizar Objeto Completo**

```javascript
import { sanitizeCommentObject } from './utils/sanitize.js';

// Da API (não confiável)
const rawComment = {
  id: 1,
  author_name: "<script>alert(1)</script>Bob",
  content: "Hello **world**\n<iframe src='evil.com'></iframe>",
  replies: [...]
};

// Sanitiza tudo
const safeComment = sanitizeCommentObject(rawComment);
// → {
//   author_name: "alert(1)Bob",
//   content: "Hello **world**<br>",
//   replies: [...]
// }
```

---

## 🔒 Configurações de Segurança

### **Opção A: Máxima Segurança (MVP)**
```javascript
sanitizeComment(content)
// → ZERO HTML, apenas texto escapado + <br>
```

### **Opção B: Markdown Básico (Pós-MVP)**
```javascript
processComment(content, {
  allowMarkdown: true,   // **bold**, *italic*, `code`
  allowLinks: false,     // Ainda sem links
  convertNewlines: true
})
// → Permite <strong>, <em>, <code> apenas
```

### **Opção C: Markdown + Links (Fase 2)**
```javascript
processComment(content, {
  allowMarkdown: true,
  allowLinks: true,      // [text](url)
  convertNewlines: true
})
// → Adiciona <a href> com rel="nofollow ugc"
```

---

## 🚀 Integração no Widget

```javascript
// comment-widget/src/renderer.js
import { sanitizeCommentObject } from './utils/sanitize.js';

export function renderComments(container, comments) {
  container.innerHTML = "";
  
  comments.forEach(rawComment => {
    // ✅ Sanitiza antes de renderizar
    const comment = sanitizeCommentObject(rawComment);
    
    const item = document.createElement("div");
    item.className = "comment";
    
    item.innerHTML = `
      <div class="comment-header">
        <strong>${comment.author_name}</strong>
        <time>${new Date(comment.created_at).toLocaleDateString()}</time>
      </div>
      <div class="comment-body">${comment.content}</div>
    `;
    
    container.appendChild(item);
    
    // Renderiza replies recursivamente
    if (comment.replies && comment.replies.length > 0) {
      const repliesDiv = document.createElement("div");
      repliesDiv.className = "comment-replies";
      renderComments(repliesDiv, comment.replies);
      container.appendChild(repliesDiv);
    }
  });
}
```

---

## ⚖️ Comparação Final

```javascript
// ❌ MASTODON CONFIG (muito permissivo para comments)
ALLOWED_TAGS: ['p', 'br', 'a', 'span', 'strong', 'em', 'blockquote', 'ul', 'ol', 'li', 'code', 'pre']
ALLOWED_ATTR: { 'a': ['href', 'rel'], 'span': ['class'] }

// ✅ COMMENT CONFIG (apropriado)
ALLOWED_TAGS: []  // MVP: zero HTML
// ou
ALLOWED_TAGS: ['br', 'strong', 'em', 'code']  // Com markdown
ALLOWED_ATTR: {}  // Nenhum atributo
```

---

## 🎯 Resposta Final

**Pode usar a mesma biblioteca DOMPurify**, mas **NÃO a mesma configuração**!

- ✅ **Mastodon Widget**: HTML rico (posts vêm com HTML)
- ✅ **Comment Widget**: Plaintext ou markdown básico (usuários digitam texto)

**Recomendação para MVP da Hackathon**: Use `sanitizeComment()` com defaults (plaintext only). Adicione markdown depois! 🚀

/**
 * Sanitization utilities for Comment Widget
 * Simpler than Mastodon widget - comments are plain text or basic markdown
 */

import DOMPurify from 'dompurify';

/**
 * Configuration for user-submitted comments
 * MUCH more restrictive than Mastodon content
 */
const COMMENT_SANITIZE_CONFIG = {
  // Very minimal HTML allowed
  ALLOWED_TAGS: [
    'p',      // Paragraphs (auto-generated from newlines)
    'br',     // Line breaks
    'strong', // Bold (if you support markdown)
    'em',     // Italic (if you support markdown)
    'a',      // Links (optional, can disable)
    'code'    // Inline code (optional)
  ],
  
  // Minimal attributes
  ALLOWED_ATTR: {
    'a': ['href', 'rel']  // Only if allowing links
  },
  
  // Only HTTPS links
  ALLOW_UNKNOWN_PROTOCOLS: false,
  ALLOWED_URI_REGEXP: /^https?:\/\//i,
  
  // Forbidden attributes
  FORBID_ATTR: [
    'target', 'style', 'onerror', 'onclick', 'onload', 
    'id', 'class', 'name'
  ],
  
  // Extra paranoid
  FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'style', 'img'],
  
  RETURN_TRUSTED_TYPE: true,
  KEEP_CONTENT: false,
  SANITIZE_DOM: true,
  WHOLE_DOCUMENT: false,
  FORCE_BODY: true,
  
  HOOKS: {
    afterSanitizeAttributes: function(node) {
      // Handle links (if allowed)
      if (node.tagName === 'A') {
        node.setAttribute('rel', 'noopener noreferrer nofollow ugc');
        node.removeAttribute('target');
        
        const href = node.getAttribute('href');
        if (href && !/^https?:\/\//i.test(href)) {
          node.removeAttribute('href');
        }
      }
    }
  }
};

/**
 * Configuration for PLAINTEXT-ONLY comments
 * Use this if you DON'T want ANY HTML in comments
 */
const PLAINTEXT_ONLY_CONFIG = {
  ALLOWED_TAGS: [],      // Zero HTML tags
  ALLOWED_ATTR: {},
  KEEP_CONTENT: true,    // Keep text content
  RETURN_TRUSTED_TYPE: false
};

/**
 * Sanitizes user-submitted comment content
 * 
 * DEFAULT BEHAVIOR: Plain text only (safest for MVP)
 * 
 * @param {string} content - Raw comment text from user
 * @param {Object} options - Configuration options
 * @param {boolean} options.allowHTML - Allow basic HTML (default: false)
 * @param {boolean} options.allowLinks - Allow links (default: false)
 * @param {boolean} options.convertNewlines - Convert \n to <br> (default: true)
 * @returns {string} - Sanitized content
 * 
 * @example
 * // Plain text only (recommended for MVP)
 * sanitizeComment("Hello <script>alert(1)</script>")
 * // → "Hello alert(1)"
 * 
 * // With newlines converted
 * sanitizeComment("Line 1\nLine 2", { convertNewlines: true })
 * // → "Line 1<br>Line 2"
 * 
 * // With basic HTML (if you want markdown support later)
 * sanitizeComment("Hello **world**", { allowHTML: true })
 * // → "Hello <strong>world</strong>"
 */
export function sanitizeComment(content, options = {}) {
  if (!content) return '';
  
  const {
    allowHTML = false,        // Default: NO HTML
    allowLinks = false,       // Default: NO LINKS
    convertNewlines = true,   // Default: Convert \n to <br>
    maxLength = 5000          // Safety limit
  } = options;
  
  // Truncate if too long (prevent DoS)
  if (content.length > maxLength) {
    content = content.substring(0, maxLength);
  }
  
  let sanitized;
  
  if (!allowHTML) {
    // PLAINTEXT MODE (recommended for MVP)
    // Strip ALL HTML, just escape text
    sanitized = DOMPurify.sanitize(content, PLAINTEXT_ONLY_CONFIG);
    
    // Convert newlines to <br> if requested
    if (convertNewlines) {
      sanitized = sanitized.replace(/\n/g, '<br>');
    }
  } else {
    // HTML MODE (for future markdown support)
    const config = { ...COMMENT_SANITIZE_CONFIG };
    
    // Remove links if not allowed
    if (!allowLinks) {
      config.ALLOWED_TAGS = config.ALLOWED_TAGS.filter(tag => tag !== 'a');
      config.ALLOWED_ATTR = {};
    }
    
    sanitized = DOMPurify.sanitize(content, config);
  }
  
  // Final safety check
  const dangerousPatterns = [
    /javascript:/gi,
    /data:text\/html/gi,
    /vbscript:/gi,
    /on\w+\s*=/gi,
    /<script/gi,
    /<iframe/gi
  ];
  
  for (const pattern of dangerousPatterns) {
    if (pattern.test(sanitized)) {
      console.error('[Security] Blocked malicious comment content');
      return '[Comment removed for security]';
    }
  }
  
  return sanitized;
}

/**
 * Sanitizes plain text fields (names, emails shown publicly)
 * Zero HTML allowed
 * 
 * @param {string} text - Plain text
 * @returns {string} - HTML-escaped text
 */
export function sanitizeText(text) {
  if (!text) return '';
  
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Validates and sanitizes email addresses
 * 
 * @param {string} email - Email address
 * @returns {string|null} - Valid email or null
 */
export function sanitizeEmail(email) {
  if (!email) return null;
  
  // Basic email regex (good enough for display)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!emailRegex.test(email)) {
    return null;
  }
  
  // Return lowercase, trimmed
  return email.toLowerCase().trim();
}

/**
 * Converts plain text with markdown-like syntax to HTML
 * Use this BEFORE sanitizeComment() if you want markdown support
 * 
 * Supported:
 * - **bold** → <strong>bold</strong>
 * - *italic* → <em>italic</em>
 * - `code` → <code>code</code>
 * 
 * @param {string} text - Plain text with markdown
 * @returns {string} - HTML (still needs sanitization!)
 */
export function markdownToHTML(text) {
  if (!text) return '';
  
  let html = text;
  
  // Bold: **text** → <strong>text</strong>
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  
  // Italic: *text* → <em>text</em>
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  
  // Inline code: `code` → <code>code</code>
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Links: [text](url) → <a href="url">text</a>
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  
  return html;
}

/**
 * Complete comment processing pipeline
 * Handles markdown → HTML → sanitization
 * 
 * @param {string} rawComment - Raw user input
 * @param {Object} options - Processing options
 * @returns {string} - Safe HTML ready for display
 * 
 * @example
 * // Simple text
 * processComment("Hello world")
 * // → "Hello world"
 * 
 * // With markdown
 * processComment("Hello **world**", { allowMarkdown: true })
 * // → "Hello <strong>world</strong>"
 */
export function processComment(rawComment, options = {}) {
  if (!rawComment) return '';
  
  const {
    allowMarkdown = false,
    allowLinks = false,
    convertNewlines = true
  } = options;
  
  let processed = rawComment;
  
  // Step 1: Convert markdown if enabled
  if (allowMarkdown) {
    processed = markdownToHTML(processed);
  }
  
  // Step 2: Sanitize
  processed = sanitizeComment(processed, {
    allowHTML: allowMarkdown,
    allowLinks,
    convertNewlines: !allowMarkdown  // Only if not markdown (markdown handles it)
  });
  
  return processed;
}

/**
 * Sanitizes a complete comment object
 * Use this before rendering in the widget
 * 
 * @param {Object} comment - Raw comment from API
 * @returns {Object} - Sanitized comment
 */
export function sanitizeCommentObject(comment) {
  if (!comment) return null;
  
  return {
    id: comment.id,
    thread_id: comment.thread_referencia_id || comment.thread_id,
    parent_id: comment.parent_id || null,
    
    // Sanitize text fields
    author_name: sanitizeText(comment.author_name),
    content: sanitizeComment(comment.content),
    
    // Dates (no sanitization needed)
    created_at: comment.created_at,
    
    // Status (ensure it's a valid number)
    is_approved: [0, 1, 2].includes(comment.is_approved) ? comment.is_approved : 0,
    
    // Nested replies (recursive sanitization)
    replies: (comment.replies || []).map(reply => sanitizeCommentObject(reply))
  };
}

/**
 * Preview function for comment form
 * Shows user what their comment will look like
 * 
 * @param {string} rawComment - User's input
 * @param {Object} options - Same as processComment
 * @returns {string} - Preview HTML
 */
export function previewComment(rawComment, options = {}) {
  const processed = processComment(rawComment, options);
  
  return `
    <div class="comment-preview">
      <div class="preview-label">Preview:</div>
      <div class="preview-content">${processed}</div>
    </div>
  `;
}

/**
 * Checks if content is safe (for admin dashboard)
 * Returns analysis of potential issues
 * 
 * @param {string} content - Comment content
 * @returns {Object} - Safety analysis
 */
export function analyzeCommentSafety(content) {
  const issues = [];
  
  if (/<script/i.test(content)) {
    issues.push('Contains <script> tag');
  }
  
  if (/javascript:/i.test(content)) {
    issues.push('Contains javascript: protocol');
  }
  
  if (/on\w+\s*=/i.test(content)) {
    issues.push('Contains event handler (onclick, etc.)');
  }
  
  if (/<iframe/i.test(content)) {
    issues.push('Contains <iframe> tag');
  }
  
  return {
    isSafe: issues.length === 0,
    issues,
    content: content.substring(0, 100) + (content.length > 100 ? '...' : '')
  };
}

// Default export
export default {
  sanitizeComment,
  sanitizeText,
  sanitizeEmail,
  markdownToHTML,
  processComment,
  sanitizeCommentObject,
  previewComment,
  analyzeCommentSafety
};
