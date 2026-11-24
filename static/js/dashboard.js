// Dashboard JavaScript for Fraud Detection System

// Auto-refresh statistics
function refreshStats() {
    fetch('/api/stats/')
        .then(response => response.json())
        .then(data => {
            console.log('Stats updated:', data);
            // Update stats if needed
        })
        .catch(error => console.error('Error fetching stats:', error));
}

// Refresh every 30 seconds
setInterval(refreshStats, 30000);

// Smooth scroll to element
function scrollToElement(id) {
    const element = document.getElementById(id);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

// Observe all cards
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.stat-card, .section-card, .chart-card');
    cards.forEach(card => observer.observe(card));
});

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

console.log('Fraud Detection System initialized ✅');
