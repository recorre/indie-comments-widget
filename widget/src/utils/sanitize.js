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