// Modern Mobile App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add smooth transitions to form inputs
    const inputs = document.querySelectorAll('.hand-drawn-input, .hand-drawn-select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.transition = 'all 0.2s ease';
        });
    });
    
    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.5s ease-out';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.school-card, .curriculum-card').forEach(card => {
        observer.observe(card);
    });
    
    // Facility search functionality
    const facilitySearch = document.getElementById('facility-search');
    if (facilitySearch) {
        facilitySearch.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const facilities = document.querySelectorAll('.facility-checkbox');
            
            facilities.forEach(facility => {
                const text = facility.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    facility.style.display = 'inline-block';
                } else {
                    facility.style.display = 'none';
                }
            });
        });
    }
    
    // Quick search on home page
    const quickSearch = document.getElementById('quick-search');
    if (quickSearch) {
        quickSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const searchTerm = this.value;
                if (searchTerm.trim()) {
                    window.location.href = `/search/?name=${encodeURIComponent(searchTerm)}`;
                }
            }
        });
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add touch feedback for mobile
    const touchElements = document.querySelectorAll('.school-card, .hand-drawn-button, .nav-item');
    touchElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.opacity = '0.7';
        });
        element.addEventListener('touchend', function() {
            setTimeout(() => {
                this.style.opacity = '1';
            }, 150);
        });
    });
    
    // Prevent zoom on double tap for iOS
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // Page slide transitions
    const contentArea = document.querySelector('.content-area');
    if (contentArea) {
        // Add slide-in animation on page load
        contentArea.style.animation = 'slideInRight 300ms ease-out';
    }
    
    // Add slide transition for navigation links
    const navLinks = document.querySelectorAll('a[href]:not([href^="#"]):not([href^="javascript:"]):not([target="_blank"])');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Only apply to internal navigation
            const href = this.getAttribute('href');
            if (href && !href.startsWith('http') && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
                // Add slide-out animation
                if (contentArea) {
                    contentArea.style.animation = 'slideOutLeft 200ms ease-in';
                }
            }
        });
    });
    
    // Fix select dropdown styling - ensure selected options don't show red background
    const selectElements = document.querySelectorAll('.form-field-select, .form-select');
    selectElements.forEach(select => {
        // Remove any inline styles that might cause red background
        select.style.colorScheme = 'dark';
        
        // When select is opened, ensure proper styling
        select.addEventListener('focus', function() {
            this.style.outline = 'none';
            this.style.borderColor = 'var(--accent-green)';
        });
        
        // When option is selected, apply proper styling
        select.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption) {
                // Ensure the selected option is properly styled
                this.style.color = 'var(--text-primary)';
                this.style.backgroundColor = 'transparent';
            }
        });
    });
});
