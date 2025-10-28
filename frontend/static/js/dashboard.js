/**
 * Dashboard JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm delete actions with accessibility
    document.querySelectorAll('form[onsubmit*="confirm"]').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var message = form.getAttribute('onsubmit').match(/confirm\('([^']+)'\)/);
            if (message && !confirm(message[1])) {
                e.preventDefault();
                announceToScreenReader('Action cancelled');
            }
        });
    });

    // Copy to clipboard functionality
    document.querySelectorAll('[data-copy]').forEach(function(element) {
        element.addEventListener('click', function() {
            var text = this.getAttribute('data-copy');
            copyToClipboard(text);
        });
    });

    // Form validation
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var isValid = validateForm(this);
            if (!isValid) {
                e.preventDefault();
                announceToScreenReader('Form validation failed. Please check required fields.');
            }
        });
    });

    // Live search functionality
    setupLiveSearch();

    // Auto-refresh data
    setupAutoRefresh();

    // Setup keyboard navigation
    setupKeyboardNavigation();

    // Setup focus management
    setupFocusManagement();
});

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            showNotification('Copied to clipboard!', 'success');
        }).catch(function(err) {
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

/**
 * Fallback copy function for older browsers
 */
function fallbackCopyTextToClipboard(text) {
    var textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    textArea.style.opacity = "0";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        var successful = document.execCommand('copy');
        if (successful) {
            showNotification('Copied to clipboard!', 'success');
        } else {
            showNotification('Failed to copy', 'error');
        }
    } catch (err) {
        showNotification('Failed to copy', 'error');
    }

    document.body.removeChild(textArea);
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    var notification = document.createElement('div');
    notification.className = 'alert alert-' + type + ' alert-dismissible fade show position-fixed';
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'assertive');
    notification.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close notification"></button>';

    document.body.appendChild(notification);

    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

/**
 * Validate form
 */
function validateForm(form) {
    var requiredFields = form.querySelectorAll('[required]');
    var isValid = true;

    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    // Email validation
    var emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(function(field) {
        if (field.value && !isValidEmail(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });

    // URL validation
    var urlFields = form.querySelectorAll('input[type="url"]');
    urlFields.forEach(function(field) {
        if (field.value && !isValidUrl(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });

    return isValid;
}

/**
 * Validate email address
 */
function isValidEmail(email) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate URL
 */
function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch (_) {
        return false;
    }
}

/**
 * Setup live search
 */
function setupLiveSearch() {
    var searchInputs = document.querySelectorAll('[data-live-search]');
    searchInputs.forEach(function(input) {
        var targetSelector = input.getAttribute('data-live-search');
        var targetElements = document.querySelectorAll(targetSelector);

        input.addEventListener('input', function() {
            var searchTerm = this.value.toLowerCase();

            targetElements.forEach(function(element) {
                var text = element.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    element.style.display = '';
                } else {
                    element.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Setup auto-refresh
 */
function setupAutoRefresh() {
    var refreshElements = document.querySelectorAll('[data-auto-refresh]');
    refreshElements.forEach(function(element) {
        var interval = parseInt(element.getAttribute('data-auto-refresh')) || 30000; // 30 seconds default

        setInterval(function() {
            if (element.style.display !== 'none') {
                location.reload();
            }
        }, interval);
    });
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';

    var date = new Date(dateString);
    var now = new Date();
    var diffInHours = Math.floor((now - date) / (1000 * 60 * 60));

    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return diffInHours + 'h ago';

    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    var timeout;
    return function executedFunction(...args) {
        var later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    var inThrottle;
    return function() {
        var args = arguments;
        var context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(function() {
                inThrottle = false;
            }, limit);
        }
    }
}

/**
 * Animate element
 */
function animateElement(element, animation, duration = 300) {
    if (!element) return;

    element.style.animation = animation + ' ' + duration + 'ms ease';
    setTimeout(function() {
        element.style.animation = '';
    }, duration);
}

/**
 * Smooth scroll to element
 */
function scrollToElement(elementId, offset = 0) {
    var element = document.getElementById(elementId);
    if (!element) return;

    var elementPosition = element.getBoundingClientRect().top;
    var offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}

/**
 * Toggle loading state
 */
function toggleLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || button.innerHTML;
    }
}

/**
 * Export data as JSON
 */
function exportAsJSON(data, filename) {
    var dataStr = JSON.stringify(data, null, 2);
    var dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

    var exportFileDefaultName = filename || 'data.json';

    var linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

/**
 * Print page
 */
function printPage() {
    window.print();
}

/**
 * Toggle dark mode
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Load dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

/**
 * Setup keyboard navigation
 */
function setupKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        // Skip navigation if user is typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.contentEditable === 'true') {
            return;
        }

        // Handle keyboard shortcuts
        switch (e.key) {
            case 'h':
            case 'H':
                if (e.altKey) {
                    e.preventDefault();
                    // Focus on main heading
                    const mainHeading = document.querySelector('h1');
                    if (mainHeading) {
                        mainHeading.focus();
                        announceToScreenReader('Focused on main heading');
                    }
                }
                break;
            case 'n':
            case 'N':
                if (e.altKey) {
                    e.preventDefault();
                    // Focus on create new button
                    const createBtn = document.querySelector('[data-bs-target="#createThreadModal"]');
                    if (createBtn) {
                        createBtn.focus();
                        announceToScreenReader('Focused on create new thread button');
                    }
                }
                break;
        }
    });
}

/**
 * Setup focus management
 */
function setupFocusManagement() {
    // Trap focus in modals
    document.addEventListener('shown.bs.modal', function(e) {
        const modal = e.target;
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        modal.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });

        // Focus first focusable element
        if (firstElement) {
            firstElement.focus();
        }
    });
}

/**
 * Announce to screen reader
 */
function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    // Remove after announcement
    setTimeout(function() {
        if (announcement.parentNode) {
            announcement.parentNode.removeChild(announcement);
        }
    }, 1000);
}