// Theme management
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme icon
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.querySelector('.theme-icon').textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
    
    // Notify server
    fetch('/toggle_theme').catch(err => console.error('Theme toggle error:', err));
}

// Initialize theme from localStorage
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.querySelector('.theme-icon').textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }
}

// Language switching
function changeLanguage(language) {
    window.location.href = `/set_language/${language}`;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
});

// Utility functions
function formatCurrency(amount, currency = 'USD') {
    const currencySymbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'INR': '₹',
        'FCFA': '₣',
        'CAD': 'C$',
        'AUD': 'A$',
        'CHF': 'CHF'
    };
    
    const symbol = currencySymbols[currency] || currency;
    return `${symbol}${amount.toFixed(2)}`;
}

function formatDate(date) {
    return new Date(date).toLocaleDateString();
}

function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        ${message}
        <button class="close-btn" onclick="this.parentElement.style.display='none';">&times;</button>
    `;
    
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.insertBefore(alertDiv, mainContent.firstChild);
    }
}

// API helper functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        showNotification('An error occurred. Please try again.', 'error');
        throw error;
    }
}
