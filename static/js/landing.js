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
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
