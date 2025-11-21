// ====================================
// FAQ Accordion
// ====================================

document.addEventListener('DOMContentLoaded', function() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            // Close other items
            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                }
            });

            // Toggle current item
            item.classList.toggle('active');
        });
    });
});

// ====================================
// Smooth Scroll for Navigation
// ====================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offset = 80; // Account for fixed navbar
            const targetPosition = target.offsetTop - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ====================================
// Download Button Analytics (Optional)
// ====================================

const downloadButtons = document.querySelectorAll('a[download]');
downloadButtons.forEach(button => {
    button.addEventListener('click', function() {
        // Track download event
        console.log('Download initiated');
        // You can add analytics tracking here
        // Example: gtag('event', 'download', { 'event_category': 'GameManager' });
    });
});

// ====================================
// Navbar Scroll Effect
// ====================================

let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
        navbar.style.boxShadow = 'none';
    } else {
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.3)';
    }

    lastScroll = currentScroll;
});

// ====================================
// Mobile Menu Toggle (for future implementation)
// ====================================

// If you want to add a hamburger menu for mobile:
/*
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('.nav-menu');

if (menuToggle) {
    menuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}
*/

// ====================================
// Scroll Reveal Animations (Optional)
// ====================================

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.querySelectorAll('.feature-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = `all 0.6s ease ${index * 0.1}s`;
    observer.observe(card);
});

// Observe steps
document.querySelectorAll('.step').forEach((step, index) => {
    step.style.opacity = '0';
    step.style.transform = 'translateX(-30px)';
    step.style.transition = `all 0.6s ease ${index * 0.2}s`;
    observer.observe(step);
});

// ====================================
// Download Link Warning (Important!)
// ====================================

// This warns users that the download link needs to be updated
const downloadLinks = document.querySelectorAll('a[href*="downloads/GameManager"]');
downloadLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        const href = this.getAttribute('href');

        // Check if the link points to a placeholder
        if (href.includes('downloads/GameManager-Setup.exe')) {
            // Get the actual download URL from GitHub releases
            // You'll need to update this with your GitHub repository URL
            const actualDownloadUrl = 'https://github.com/YOUR-USERNAME/GameManager/releases/latest/download/GameManager-Setup.exe';

            // For now, we'll show an alert
            // Once you upload to GitHub, replace this with the actual link
            console.log('Download link clicked. Update with actual GitHub releases URL');

            // Uncomment and update when ready:
            // this.setAttribute('href', actualDownloadUrl);
        }
    });
});

// ====================================
// Copy to Clipboard for Code Snippets (if needed)
// ====================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// ====================================
// Form Submission Handler (for future contact form)
// ====================================

/*
const contactForm = document.querySelector('#contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(contactForm);

        try {
            // Handle form submission
            console.log('Form submitted');
            // You can add email service integration here
        } catch (error) {
            console.error('Form submission error:', error);
        }
    });
}
*/

// ====================================
// Version Check (Optional)
// ====================================

// You can add version checking against GitHub API
async function checkLatestVersion() {
    try {
        // Replace with your GitHub API endpoint
        // const response = await fetch('https://api.github.com/repos/YOUR-USERNAME/GameManager/releases/latest');
        // const data = await response.json();
        // console.log('Latest version:', data.tag_name);

        // Update version display on page
        // document.querySelectorAll('.version').forEach(el => {
        //     el.textContent = data.tag_name;
        // });
    } catch (error) {
        console.error('Error checking version:', error);
    }
}

// Call on page load
// checkLatestVersion();

console.log('GameManager Website Loaded Successfully! 🎮');
