/**
 * Nicetek Kenya - Main JavaScript
 * Minimal vanilla JS for enhanced interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // ============================================
    // 1. Smooth Scroll
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ============================================
    // 2. Navbar Scroll Effect
    // ============================================
    const navbar = document.querySelector('.navbar');
    let lastScrollY = 0;
    
    window.addEventListener('scroll', function() {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 50) {
            navbar.classList.add('shadow-sm');
            navbar.style.backgroundColor = 'rgba(255,255,255,0.95)';
            navbar.style.backdropFilter = 'blur(10px)';
        } else {
            navbar.classList.remove('shadow-sm');
            navbar.style.backgroundColor = 'rgba(255,255,255,1)';
            navbar.style.backdropFilter = 'none';
        }
        
        lastScrollY = currentScrollY;
    });
    
    // ============================================
    // 3. Package Price Calculator
    // ============================================
    const calculatorForms = document.querySelectorAll('.price-calculator');
    calculatorForms.forEach(form => {
        const inputs = form.querySelectorAll('input[data-price]');
        const totalDisplay = form.querySelector('[data-total]');
        
        if (inputs.length && totalDisplay) {
            inputs.forEach(input => {
                input.addEventListener('change', function() {
                    calculateTotal(form);
                });
            });
            
            function calculateTotal(form) {
                let total = 0;
                form.querySelectorAll('input[data-price]:checked').forEach(input => {
                    total += parseFloat(input.dataset.price);
                });
                totalDisplay.textContent = 'KSh ' + total.toLocaleString();
            }
        }
    });
    
    // ============================================
    // 4. Auto-dismiss Alerts
    // ============================================
    const alerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
    
    // ============================================
    // 5. Back to Top Button
    // ============================================
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTop.className = 'btn btn-primary position-fixed bottom-0 end-0 m-4 rounded-circle';
    backToTop.style.width = '50px';
    backToTop.style.height = '50px';
    backToTop.style.display = 'none';
    backToTop.style.zIndex = '1000';
    backToTop.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
    document.body.appendChild(backToTop);
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 400) {
            backToTop.style.display = 'block';
            backToTop.style.animation = 'fadeIn 0.3s ease';
        } else {
            backToTop.style.display = 'none';
        }
    });
    
    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // ============================================
    // 6. Client Portal Sidebar Toggle
    // ============================================
    const sidebarToggle = document.querySelector('[data-toggle="sidebar"]');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // ============================================
    // 7. Form Validation Helpers
    // ============================================
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9+() -]/g, '');
        });
    });
    
    // ============================================
    // 8. Newsletter Form Handler
    // ============================================
    const newsletterForms = document.querySelectorAll('form.newsletter-form');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const email = this.querySelector('input[type="email"]');
            if (email && !email.value.trim()) {
                e.preventDefault();
                email.classList.add('is-invalid');
                email.focus();
            }
        });
    });
    
    // ============================================
    // 9. Package Comparison
    // ============================================
    const compareButtons = document.querySelectorAll('[data-compare]');
    compareButtons.forEach(button => {
        button.addEventListener('click', function() {
            const packageId = this.dataset.package;
            // Add to comparison array and redirect
            const compareIds = JSON.parse(sessionStorage.getItem('compareIds') || '[]');
            if (!compareIds.includes(packageId)) {
                compareIds.push(packageId);
                sessionStorage.setItem('compareIds', JSON.stringify(compareIds));
            }
            window.location.href = '/packages/compare/?ids=' + compareIds.join(',');
        });
    });
    
    // ============================================
    // 10. Lazy Loading Images
    // ============================================
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    }
});

// ============================================
// 11. Toast Notification System
// ============================================
function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
    toast.role = 'alert';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.querySelector('.toast-container').appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ============================================
// 12. Package Filter
// ============================================
function filterPackages(category) {
    const packages = document.querySelectorAll('.package-card');
    packages.forEach(pkg => {
        if (category === 'all' || pkg.dataset.category === category) {
            pkg.style.display = 'block';
        } else {
            pkg.style.display = 'none';
        }
    });
}
