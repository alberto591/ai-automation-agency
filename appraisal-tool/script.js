// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Dynamic API URL: Use localhost for dev, relative path for prod
    const API_BASE = (window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.protocol === 'file:' ||
        !window.location.hostname)
        ? 'http://localhost:8000'
        : '';
    console.log('🚀 AI Backend targeting:', API_BASE || 'Production (Relative)');


    // Mobile Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('active');
            const icon = navToggle.querySelector('i');
            icon.classList.toggle('ph-list');
            icon.classList.toggle('ph-x');
        });
    }

    // Smooth scrolling for navigation links
    const navAnchors = document.querySelectorAll('a[href^="#"]');
    navAnchors.forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const navHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = target.offsetTop - navHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                if (navLinks && navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                    const icon = navToggle.querySelector('i');
                    icon.classList.remove('ph-x');
                    icon.classList.add('ph-list');
                }
            }
        });
    });

    // Demo Conversation Animation
    function startDemoConversation() {
        const conversationSteps = document.querySelectorAll('.conversation-step');
        let currentStep = 0;

        function showNextStep() {
            if (currentStep < conversationSteps.length) {
                // Hide current step
                conversationSteps.forEach(step => step.classList.remove('active'));

                // Show next step
                const nextStep = conversationSteps[currentStep];
                nextStep.classList.add('active');

                currentStep++;

                // Continue to next step after delay
                setTimeout(showNextStep, 3000);
            } else {
                // Reset to beginning after completion
                setTimeout(() => {
                    currentStep = 0;
                    showNextStep();
                }, 5000);
            }
        }

        // Start the conversation animation
        setTimeout(showNextStep, 1000);
    }

    // Initialize demo conversation when in view
    const demoContainer = document.querySelector('.demo-conversation');
    if (demoContainer) {
        const demoObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    startDemoConversation();
                }
            });
        }, { threshold: 0.5 });

        demoObserver.observe(demoContainer);
    }

    // Contact Form Handling
    const contactForm = document.querySelector('.contact-form');
    const submitButton = document.querySelector('.contact-form .btn-primary');

    if (contactForm && submitButton) {
        submitButton.addEventListener('click', function (e) {
            e.preventDefault();

            // Get form data
            const formData = new FormData(contactForm);
            const name = formData.get('name');
            const agency = formData.get('agency');
            const phone = formData.get('phone');

            // Basic validation
            if (!name || !agency || !phone) {
                showNotification('Per favore compila tutti i campi obbligatori', 'error');
                return;
            }

            // Phone validation (Italy +39 and Spain +34)
            const phoneRegex = /^(\+39|0039|\+34|0034|0)?[0-9]{9,10}$/;
            if (!phoneRegex.test(phone.replace(/\s/g, ''))) {
                showNotification('Per favore inserisci un numero di telefono valido', 'error');
                return;
            }

            // Send data to backend API
            this.innerHTML = '<i class="ph ph-spinner"></i> Elaborazione IA...';
            this.disabled = true;

            const payload = {
                name: name,
                agency: agency,
                phone: phone,
                properties: formData.get('properties')
            };

            fetch(`${API_BASE}/api/leads`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            })
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    // Success
                    const currentLang = document.documentElement.lang;
                    const successMessage = currentLang === 'it'
                        ? '✅ Lead ricevuto! Controlla il tuo WhatsApp tra 10 secondi.'
                        : '✅ Lead received! Check your WhatsApp in 10 seconds.';

                    // Use showNotification if available, otherwise alert fallback (though we removed the annoying one, this is key feedback)
                    if (typeof showNotification === 'function') {
                        showNotification(successMessage, 'success');
                    } else {
                        alert(successMessage);
                    }

                    contactForm.reset();
                    this.innerHTML = '<i class="ph ph-check-circle"></i> Inviato!';

                    // Open Cal.com as secondary step
                    setTimeout(() => openBooking(), 2000);
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorMsg = document.documentElement.lang === 'it'
                        ? 'Errore di connessione. Riprova.'
                        : 'Connection error. Please try again.';

                    if (typeof showNotification === 'function') {
                        showNotification(errorMsg, 'error');
                    } else {
                        alert(errorMsg);
                    }

                    this.innerHTML = '<i class="ph ph-warning"></i> Riprova';
                    this.disabled = false;
                });
        });
    }

    // Cal.com Integration
    function openBooking() {
        // Direct link fallback for reliability
        window.open('https://cal.com/anzevino-ai/demo', '_blank');
    }

    // Demo Button Handling
    // Disabled to allow native <a> tag behavior (more reliable)
    /* 
    const demoButtons = document.querySelectorAll('.btn-primary');
    demoButtons.forEach(button => {
        if (button.textContent.includes('Demo') || button.textContent.includes('Prenota') || button.textContent.includes('Book')) {
            button.addEventListener('click', function (e) {
                e.preventDefault();
                openBooking();
            });
        }
    });
    */

    // WhatsApp Integration
    const whatsappButtons = document.querySelectorAll('[href*="whatsapp"]');
    whatsappButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const phoneNumber = '+393401234567'; // Replace with actual number
            const message = encodeURIComponent('Ciao! Vorrei saperne di più sui vostri servizi AI per agenzie immobiliari.');
            const whatsappUrl = `https://wa.me/${phoneNumber}?text=${message}`;
            window.open(whatsappUrl, '_blank');
        });
    });

    // Navbar Background on Scroll
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', function () {
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 4px 20px rgba(15, 23, 42, 0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });

    // Intersection Observer for Animations
    const animatedElements = document.querySelectorAll('.feature-card, .feature-item, .problem-stat, .stat-card');

    const animationObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0) scale(1)';
                }, index * 100);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px) scale(0.95)';
        element.style.transition = 'all 0.8s cubic-bezier(0.22, 1, 0.36, 1)';
        animationObserver.observe(element);
    });

    // Appraisal Form Handling (Lead Magnet)
    const appraisalForm = document.getElementById('appraisal-form');
    if (appraisalForm) {
        appraisalForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const submitBtn = this.querySelector('button[type="submit"]');
            const address = document.getElementById('appraisal-address').value;
            const postcode = document.getElementById('appraisal-postcode').value;
            const phone = document.getElementById('appraisal-phone').value;
            const condition = document.getElementById('appraisal-condition').value;

            if (!address || !postcode || !phone || !condition) {
                showNotification('Compila tutti i campi obbligatori', 'error');
                return;
            }

            // Validazione telefono (Italia +39, Spagna +34)
            const phoneRegex = /^(\+39|0039|\+34|0034|0)?[0-9]{9,10}$/;
            if (!phoneRegex.test(phone.replace(/\s/g, ''))) {
                showNotification('Numero di telefono non valido', 'error');
                return;
            }

            submitBtn.innerHTML = '<i class="ph ph-spinner"></i> Analisi...';
            submitBtn.disabled = true;

            const payload = {
                name: "AI Appraisal Lead",
                agency: "Fifi Appraisal Tool",
                phone: phone,
                postcode: postcode,
                properties: "RICHIESTA VALUTAZIONE: " + address + " (Condizione: " + condition + ")"
            };

            fetch(`${API_BASE}/api/leads`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
                .then(response => response.json())
                .then(data => {
                    showNotification('Valutazione in arrivo su WhatsApp!', 'success');

                    // Show Instant Result UI
                    document.querySelector('.appraisal-form-box').style.display = 'none';
                    const resultBox = document.getElementById('appraisal-result');
                    resultBox.style.display = 'block';

                    // Simulate Calculation Animation
                    animateValue("res-min", 0, 450000, 1500);
                    animateValue("res-max", 0, 485000, 1500);
                    animateValue("res-sqm", 0, 5200, 1500);
                    animateValue("res-rent", 0, 1850, 1500);
                    animateValue("res-yield", 0, 5.2, 1500, true); // true for decimal
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Errore. Riprova più tardi.', 'error');
                    submitBtn.innerHTML = '<i class="ph ph-warning"></i> Riprova';
                    submitBtn.disabled = false;
                });
        });
    }

    // Typing Animation for Hero Chat
    function simulateTyping() {
        const typingBubble = document.querySelector('.typing-indicator');
        if (typingBubble) {
            setTimeout(() => {
                const chatContainer = document.querySelector('.chat-container');
                const newMessage = document.createElement('div');
                newMessage.className = 'chat-message from-ai';
                newMessage.innerHTML = `
                    <div class="message-time">14:23</div>
                    <div class="message-bubble ai-bubble">
                        Perfetto! Ho trovato 3 trilocali disponibili a Porta Nuova nel tuo budget. Ti invio le foto e organizziamo una visita per domani alle 16:00?
                    </div>
                `;
                typingBubble.closest('.chat-message').remove();
                chatContainer.appendChild(newMessage);

                // Continue the conversation
                setTimeout(() => {
                    const clientResponse = document.createElement('div');
                    clientResponse.className = 'chat-message from-client';
                    clientResponse.innerHTML = `
                        <div class="message-time">14:24</div>
                        <div class="message-bubble">
                            Sì, mi interessa! Grazie per la velocità della risposta
                        </div>
                    `;
                    chatContainer.appendChild(clientResponse);

                    // Scroll to bottom
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }, 2000);

                chatContainer.scrollTop = chatContainer.scrollHeight;
            }, 2000);
        }
    }

    // Start typing simulation after page load
    setTimeout(simulateTyping, 3000);

    // Dashboard Stats Animation
    const dashboardStats = document.querySelectorAll('.stat-content .stat-number');
    let dashboardAnimated = false;

    function animateDashboardStats() {
        if (dashboardAnimated) return;

        dashboardStats.forEach(stat => {
            const target = parseInt(stat.textContent);
            let current = 0;
            const increment = target / 50;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                    dashboardAnimated = true;
                }
                stat.textContent = Math.floor(current);
            }, 40);
        });
    }

    // Intersection Observer for dashboard animation
    const dashboardSection = document.querySelector('.dashboard-section');
    if (dashboardSection && dashboardStats.length > 0) {
        const dashboardObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(animateDashboardStats, 500);
                }
            });
        }, {
            threshold: 0.3
        });

        dashboardObserver.observe(dashboardSection);
    }

    // Conversation Step Navigation
    const conversationItems = document.querySelectorAll('.conversation-item');
    conversationItems.forEach(item => {
        item.addEventListener('click', function () {
            // Remove active state from all items
            conversationItems.forEach(conv => conv.classList.remove('active'));

            // Add active state to clicked item
            this.classList.add('active');

            // You could add logic here to show conversation details
        });
    });

    // Feature Card Hover Effects
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-12px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Problem Stats Animation
    const problemStats = document.querySelectorAll('.problem-stat');
    let problemStatsAnimated = false;

    function animateProblemStats() {
        if (problemStatsAnimated) return;

        problemStats.forEach((stat, index) => {
            const numberElement = stat.querySelector('.stat-number');
            const targetText = numberElement.textContent;
            const isPercentage = targetText.includes('%');
            const isEuro = targetText.includes('€');

            let target = parseInt(targetText.replace(/[^0-9]/g, ''));
            let current = 0;
            const increment = target / 60;

            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                    problemStatsAnimated = true;
                }

                let displayValue = Math.floor(current);
                if (isPercentage) displayValue += '%';
                if (isEuro) displayValue = '€' + displayValue.toLocaleString();

                numberElement.textContent = displayValue;
            }, 30 + (index * 100));
        });
    }

    // Intersection Observer for problem stats
    const problemSection = document.querySelector('.problem-section');
    if (problemSection && problemStats.length > 0) {
        const problemObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(animateProblemStats, 800);
                }
            });
        }, {
            threshold: 0.4
        });

        problemObserver.observe(problemSection);
    }

    // Form Input Enhancements
    const formInputs = document.querySelectorAll('.form-group input, .form-group select');
    formInputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('focused');
            if (this.value) {
                this.parentElement.classList.add('filled');
            } else {
                this.parentElement.classList.remove('filled');
            }
        });
    });

    // Parallax Effect for Hero Section
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', function () {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.3;
            hero.style.transform = `translateY(${rate}px)`;
        });
    }

    // Loading states for buttons
    function addLoadingState(button, originalText) {
        button.innerHTML = '<i class="ph ph-spinner"></i> Caricamento...';
        button.disabled = true;

        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 2000);
    }

    // Success/Error Notifications
    function showNotification(message, type = 'info') {
        // Remove existing notification
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="ph ph-${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : 'info'}"></i>
                <span>${message}</span>
                <button class="notification-close class="ph ph">
                    <i-x"></i>
                </button>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#059669' : type === 'error' ? '#dc2626' : '#1e40af'};
            color: white;
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
            max-width: 400px;
            font-family: Inter, sans-serif;
        `;

        notification.querySelector('.notification-content').style.cssText = `
            display: flex;
            align-items: center;
            gap: 12px;
        `;

        notification.querySelector('.notification-close').style.cssText = `
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 4px;
            margin-left: auto;
        `;

        // Add to DOM
        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Close functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    // Add mobile menu styles
    const mobileMenuStyles = `
        @media (max-width: 768px) {
            .nav-links {
                position: fixed;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border-top: 1px solid rgba(148, 163, 184, 0.2);
                padding: 24px;
                display: flex;
                flex-direction: column;
                gap: 16px;
                transform: translateY(-100%);
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
                box-shadow: 0 8px 25px rgba(15, 23, 42, 0.15);
                z-index: 999;
            }

            .nav-links.active {
                transform: translateY(0);
                opacity: 1;
                visibility: visible;
            }

            .nav-links .btn-primary {
                margin-top: 16px;
                align-self: flex-start;
            }
        }
    `;

    // Inject mobile menu styles
    const styleSheet = document.createElement('style');
    styleSheet.textContent = mobileMenuStyles;
    document.head.appendChild(styleSheet);

    // Performance optimization: Debounce scroll events
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Apply debounce to scroll handlers
    const debouncedScrollHandler = debounce(function () {
        // Additional scroll-based animations can be added here
    }, 16); // ~60fps

    window.addEventListener('scroll', debouncedScrollHandler);

    // Accessibility improvements
    document.addEventListener('keydown', function (e) {
        // ESC key closes mobile menu
        if (e.key === 'Escape' && navLinks && navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            const icon = navToggle.querySelector('i');
            icon.classList.remove('ph-x');
            icon.classList.add('ph-list');
        }
    });

    // Focus management for mobile menu
    if (navLinks) {
        const focusableElements = navLinks.querySelectorAll('a, button');
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];

        navToggle.addEventListener('click', function () {
            setTimeout(() => {
                if (navLinks.classList.contains('active')) {
                    firstFocusable.focus();
                }
            }, 300);
        });

        navLinks.addEventListener('keydown', function (e) {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        lastFocusable.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        firstFocusable.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }

    console.log('🏠 Anzevino AI Real Estate - Website Loaded Successfully');
});

// Utility Functions
function animateValue(id, start, end, duration, isDecimal = false) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = progress * (end - start) + start;
        obj.innerHTML = isDecimal ? current.toFixed(1) : Math.floor(current).toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function resetAppraisal() {
    document.getElementById('appraisal-form').reset();
    document.querySelector('.appraisal-form-box').style.display = 'block';
    document.getElementById('appraisal-result').style.display = 'none';

    // Reset button state
    const submitBtn = document.querySelector('#appraisal-form button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span data-translate="appraisal-cta">Ottieni Valutazione AI</span> <i class="ph ph-arrow-right"></i>';
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^(\+39|0039|\+34|0034|0)?[0-9]{9,10}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
}

// Performance monitoring
window.addEventListener('load', function () {
    // Log performance metrics
    if (window.performance) {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log(`Page load time: ${loadTime}ms`);
    }
});

// Language Translation Data
const translations = {
    it: {
        // Navigation
        'nav-soluzione': 'Soluzione',
        'nav-dashboard': 'Dashboard',
        'nav-caratteristiche': 'Caratteristiche',
        'nav-contatto': 'Contatto',
        'nav-prenota-demo': 'Prenota Demo',
        'nav-valutazione': 'Valutazione AI',

        // Hero Section
        'hero-subtitle': 'Il Futuro dell\'Immobiliare',
        'hero-title': 'Vendi più case ',
        'hero-title-highlight': 'mentre dormi',
        'hero-description': 'Il tuo primo Agente AI che qualifica i lead su WhatsApp in 15 secondi, 24 ore su 24. Trasforma ogni notturna in un\'opportunità di vendita.',
        'hero-cta-button': 'Prenota una Demo Gratuita',
        'hero-cta-note': 'Nessun impegno • Setup in 24 ore • Garanzia risultati',

        // Problem Section
        'problem-tag': 'Il Problema',
        'problem-title': 'Stai perdendo il 80% dei tuoi migliori clienti',
        'problem-description': 'Ogni giorno, centinaia di potenziali acquirenti visitano Immobiliare.it e Idealista, compilano moduli e ti contattano via WhatsApp. Ma quando li chiami, sono già passati alla concorrenza.',
        'problem-stat-lost': 'dei lead persi entro 2 ore',
        'problem-stat-money': 'perdita media annua per agenzia',
        'problem-stat-whatsapp': 'dei clienti preferisce WhatsApp',
        'problem-scenario-1-title': 'Ore 22:30 - Cliente notturno',
        'problem-scenario-1-desc': 'Interessato a un bilocale, scrive su WhatsApp. Tu dormi. Il concorrente risponde in 2 minuti.',
        'problem-scenario-2-title': 'Domenica pomeriggio - Weekend',
        'problem-scenario-2-desc': 'Coppia vuole vedere 3 appartamenti. Chiami lunedì: "Abbiamo già comprato".',
        'chart-title': 'Lead Persi nel Tempo',



        // Demo Live Section
        'demo-live-tag': 'Demo Live',
        'demo-live-title': 'Guarda l\'AI in Azione',
        'demo-live-desc': 'In questo video ti mostro esattamente come l\'AI gestisce un lead dal primo contatto all\'appuntamento.',

        // Dashboard Section
        'dashboard-tag': 'Dashboard di Controllo',
        'dashboard-title': 'Monitora tutto in tempo reale',
        'dashboard-subtitle': 'La tua console di comando per controllare ogni conversazione AI, gestire i lead e ottimizzare le performance di vendita.',
        'dashboard-logo-name': 'Anzevino AI',
        'dashboard-conversazioni': 'Conversazioni',
        'dashboard-clienti': 'Clienti',
        'dashboard-proprieta': 'Proprietà',
        'dashboard-appuntamenti': 'Appuntamenti',
        'dashboard-analytics': 'Analytics',
        'dashboard-conversazioni-oggi': 'Conversazioni Oggi',
        'dashboard-lead-qualificati': 'Lead Qualificati',
        'dashboard-visite-prenotate': 'Visite Prenotate',
        'dashboard-conversazioni-recenti': 'Conversazioni Recenti',
        'dashboard-vedi-tutte': 'Vedi tutte',
        'dashboard-whatsapp': 'WhatsApp',
        'dashboard-time-2min': '2 min fa',
        'dashboard-time-5min': '5 min fa',
        'dashboard-time-8min': '8 min fa',
        'dashboard-status-hot': 'HOT LEAD',
        'dashboard-status-qualified': 'QUALIFICATO',
        'dashboard-status-followup': 'FOLLOW UP',
        'dashboard-preview-1': 'Budget 500k, trilocale zona Porta Nuova...',
        'dashboard-preview-2': 'Visita prenotata per domani alle 15:00...',
        'dashboard-preview-3': 'Inviate 3 alternative bilocali zona Niguarda...',

        // Features Section
        'features-tag': 'Caratteristiche',
        'features-title': 'Tutto quello che ti serve per vendere di più',
        'features-subtitle': 'Una suite completa di strumenti AI progettata specificamente per le agenzie immobiliari italiane.',
        'feature-item-language': 'Supporto multilingue (IT/EN)',
        'feature-item-tone': 'Tone of voice personalizzabile',
        'feature-item-takeover': 'Takeover umano immediato',

        // Stats Grid
        'stat-speed-title': 'Velocità Estrema',
        'stat-speed-desc': 'Risposte in meno di 15 secondi su WhatsApp, superando ogni aspettativa del cliente.',
        'stat-conv-title': 'Conversion Rate +300%',
        'stat-conv-desc': 'Trasforma semplici curiosi in lead qualificati pronti per la visita.',
        'stat-team-title': 'Team Potenziato',
        'stat-team-desc': 'I tuoi agenti si concentrano solo sulle visite, l\'AI gestisce tutto il funnel iniziale.',

        // Contact Section
        'contact-tag': 'Inizia Oggi',
        'contact-title': 'Trasforma la tua agenzia in una macchina di vendite',
        'contact-subtitle': 'Parla con un esperto e scopri come l\'AI può aumentare le tue vendite del 300% in soli 90 giorni.',
        'contact-form-title': 'Prenota la tua demo gratuita',
        'contact-form-subtitle': 'Compila il form e ti contatteremo entro 2 ore',
        'form-name': 'Nome *',
        'form-agency': 'Nome Agenzia *',
        'form-phone': 'Telefono *',
        'form-email': 'Email',
        'form-properties': 'Quante proprietà gestisci?',
        'form-submit': 'Prenota Demo Gratuita',
        'form-note': 'I tuoi dati sono protetti e non verranno mai condivisi',
        'form-name-placeholder': 'Il tuo nome completo',
        'form-agency-placeholder': 'Nome della tua agenzia',
        'form-phone-placeholder': '+39 123 456 7890',
        'form-email-placeholder': 'tua@email.it (opzionale)',
        'form-properties-option-empty': 'Seleziona una opzione',
        'form-properties-option-1-50': '1-50 proprietà',
        'form-properties-option-51-100': '51-100 proprietà',
        'form-properties-option-101-200': '101-200 proprietà',
        'form-properties-option-200+': 'Oltre 200 proprietà',

        // Footer
        'footer-description': 'Il primo agente AI per le agenzie immobiliari italiane. Trasforma ogni contatto in un\'opportunità di vendita.',
        'footer-soluzione': 'Soluzione',
        'footer-come-funziona': 'Come Funziona',
        'footer-dashboard': 'Dashboard',
        'footer-caratteristiche': 'Caratteristiche',
        'footer-prezzi': 'Prezzi',
        'footer-azienda': 'Azienda',
        'footer-chi-siamo': 'Chi Siamo',
        'footer-case-study': 'Case Study',
        'footer-partner': 'Partner',
        'footer-careers': 'Careers',
        'footer-supporto': 'Supporto',
        'footer-centro-assistenza': 'Centro Assistenza',
        'footer-documentazione': 'Documentazione',
        'footer-stato-sistema': 'Stato Sistema',
        'footer-contatto': 'Contatto',
        'footer-legal': 'Legal',
        'footer-privacy': 'Privacy Policy',
        'footer-terms': 'Termini di Servizio',
        'footer-cookies': 'Cookie Policy',
        'footer-gdpr': 'GDPR',
        'footer-copyright': '© 2025 Anzevino AI Real Estate. Tutti i diritti riservati.',

        // Demo Conversation
        'demo-title': 'Esempio di Conversazione AI',
        'demo-ai-in-azione': 'AI in azione',
        'demo-client-label': 'Cliente',
        'demo-ai-label': 'Anzevino AI',
        'demo-step-1-msg': 'Buongiorno, vorrei informazioni su appartamenti a Milano Porta Nuova',
        'demo-step-2-msg': 'Buongiorno! Sono l\'assistente virtuale dell\'agenzia. Per aiutarti al meglio, mi puoi dire il budget disponibile e che tipologia stai cercando?',
        'demo-step-3-msg': 'Budget 400k, vorrei un bilocale moderno',
        'demo-step-4-msg': 'Perfetto! Ho trovato 3 bilocali in Porta Nuova nel tuo budget. Ti invio le planimetrie e organizziamo una visita per giovedì alle 16:00?',
        'demo-step-5-msg': 'Sì, perfetto! A giovedì allora',
        'demo-step-6-msg': 'Confermato! Appuntamento giovedì 16:00 in Via Dante 12. Riceverai un promemoria domani. Buona giornata!',

        // Stats
        'stat-tempo-risposta': 'Tempo di risposta',
        'stat-disponibilita': 'Disponibilità',
        'stat-lead-qualificati': 'Lead qualificati',



        // Benefits
        'benefit-demo': 'Demo personalizzata in 30 minuti',
        'benefit-setup': 'Setup gratuito e senza impegno',
        'benefit-formazione': 'Formazione inclusa per il tuo team',
        'benefit-supporto': 'Supporto tecnico dedicato',

        // Appraisal (Lead Magnet)
        'appraisal-tag': 'Novità',
        'appraisal-title': 'Scopri il valore della tua casa in 15 secondi',
        'appraisal-subtitle': 'L\'IA analizza i prezzi di mercato della tua zona e ti invia una valutazione istantanea su WhatsApp. Gratuito, veloce, preciso.',
        'appraisal-f1': 'Analisi Big Data real-time',
        'appraisal-f2': 'Risultato diretto su WhatsApp',
        'appraisal-f3': 'Precisione per quartiere',
        'appraisal-address-placeholder': 'Indirizzo dell\'immobile',
        'appraisal-postcode-placeholder': 'CAP / Codice Postale',
        'appraisal-phone-placeholder': 'Tuo WhatsApp (+39 ...)',
        'appraisal-cta': 'Ottieni Valutazione AI',
        'appraisal-disclaimer': 'Zero spam. Solo i dati che ti servono.'
    },
    en: {
        // Navigation
        'nav-soluzione': 'Solution',
        'nav-dashboard': 'Dashboard',
        'nav-caratteristiche': 'Features',
        'nav-contatto': 'Contact',
        'nav-prenota-demo': 'Book Demo',
        'nav-valutazione': 'AI Valuation',

        // Hero Section
        'hero-subtitle': 'The Future of Real Estate',
        'hero-title': 'Sell more homes ',
        'hero-title-highlight': 'while you sleep',
        'hero-description': 'Your first AI Agent that qualifies leads on WhatsApp in 15 seconds, 24/7. Turn every night into a sales opportunity.',
        'hero-cta-button': 'Book a Free Demo',
        'hero-cta-note': 'No commitment • Setup in 24 hours • Results guaranteed',

        // Problem Section
        'problem-tag': 'The Problem',
        'problem-title': 'You\'re losing 80% of your best customers',
        'problem-description': 'Every day, hundreds of potential buyers visit portals, fill out forms and contact you via WhatsApp. But when you call them, they\'ve already gone to the competition.',
        'problem-stat-lost': 'of leads lost within 2 hours',
        'problem-stat-money': 'avg annual loss per agency',
        'problem-stat-whatsapp': 'of customers prefer WhatsApp',
        'problem-scenario-1-title': '10:30 PM - Nightly Lead',
        'problem-scenario-1-desc': 'Interested in a flat, writes on WhatsApp. You are asleep. The competitor responds in 2 minutes.',
        'problem-scenario-2-title': 'Sunday Afternoon - Weekend',
        'problem-scenario-2-desc': 'Couple wants to see 3 apartments. You call on Monday: "We already bought one".',
        'chart-title': 'Leads Lost Over Time',



        // Demo Live Section
        'demo-live-tag': 'Live Demo',
        'demo-live-title': 'Watch AI in Action',
        'demo-live-desc': 'In this video I show you exactly how the AI handles a lead from first contact to appointment.',

        // Dashboard Section
        'dashboard-tag': 'Control Dashboard',
        'dashboard-title': 'Monitor everything in real time',
        'dashboard-subtitle': 'Your command console to control every AI conversation, manage leads and optimize sales performance.',
        'dashboard-logo-name': 'Anzevino AI',
        'dashboard-conversazioni': 'Conversations',
        'dashboard-clienti': 'Clients',
        'dashboard-proprieta': 'Properties',
        'dashboard-appuntamenti': 'Appointments',
        'dashboard-analytics': 'Analytics',
        'dashboard-conversazioni-oggi': 'Conversations Today',
        'dashboard-lead-qualificati': 'Qualified Leads',
        'dashboard-visite-prenotate': 'Booked Visits',
        'dashboard-conversazioni-recenti': 'Recent Conversations',
        'dashboard-vedi-tutte': 'View All',
        'dashboard-whatsapp': 'WhatsApp',
        'dashboard-time-2min': '2 min ago',
        'dashboard-time-5min': '5 min ago',
        'dashboard-time-8min': '8 min ago',
        'dashboard-status-hot': 'HOT LEAD',
        'dashboard-status-qualified': 'QUALIFIED',
        'dashboard-status-followup': 'FOLLOW UP',
        'dashboard-preview-1': 'Budget 500k, 3-room apt in Porta Nuova...',
        'dashboard-preview-2': 'Viewing booked for tomorrow at 3 PM...',
        'dashboard-preview-3': 'Sent 3 alternatives in Niguarda area...',

        // Features Section
        'features-tag': 'Features',
        'features-title': 'Everything you need to sell more',
        'features-subtitle': 'A complete suite of AI tools designed specifically for real estate agencies.',
        'feature-item-language': 'Multilingual Support (IT/EN)',
        'feature-item-tone': 'Customizable Tone of Voice',
        'feature-item-takeover': 'Immediate Human Takeover',

        // Stats Grid
        'stat-speed-title': 'Extreme Speed',
        'stat-speed-desc': 'Responses in less than 15 seconds on WhatsApp, exceeding every customer expectation.',
        'stat-conv-title': 'Conversion Rate +300%',
        'stat-conv-desc': 'Turns simple curious prospects into qualified leads ready for viewing.',
        'stat-team-title': 'Boosted Team',
        'stat-team-desc': 'Your agents focus only on viewings, the AI manages the entire initial funnel.',

        // Contact Section
        'contact-tag': 'Start Today',
        'contact-title': 'Turn your agency into a sales machine',
        'contact-subtitle': 'Talk to an expert and discover how AI can increase your sales by 300% in just 90 days.',
        'contact-form-title': 'Book your free demo',
        'contact-form-subtitle': 'Fill out the form and we\'ll contact you within 2 hours',
        'form-name': 'Name *',
        'form-agency': 'Agency Name *',
        'form-phone': 'Phone *',
        'form-email': 'Email',
        'form-properties': 'How many properties do you manage?',
        'form-submit': 'Book Free Demo',
        'form-note': 'Your data is protected and will never be shared',
        'form-name-placeholder': 'Your full name',
        'form-agency-placeholder': 'Your agency name',
        'form-phone-placeholder': '+39 123 456 7890',
        'form-email-placeholder': 'your@email.com (optional)',
        'form-properties-option-empty': 'Select an option',
        'form-properties-option-1-50': '1-50 properties',
        'form-properties-option-51-100': '51-100 properties',
        'form-properties-option-101-200': '101-200 properties',
        'form-properties-option-200+': 'Over 200 properties',

        // Footer
        'footer-description': 'The first AI agent for Italian real estate agencies. Turn every contact into a sales opportunity.',
        'footer-soluzione': 'Solution',
        'footer-come-funziona': 'How It Works',
        'footer-dashboard': 'Dashboard',
        'footer-caratteristiche': 'Features',
        'footer-prezzi': 'Pricing',
        'footer-azienda': 'Company',
        'footer-chi-siamo': 'About Us',
        'footer-case-study': 'Case Studies',
        'footer-partner': 'Partners',
        'footer-careers': 'Careers',
        'footer-supporto': 'Support',
        'footer-centro-assistenza': 'Help Center',
        'footer-documentazione': 'Documentation',
        'footer-stato-sistema': 'System Status',
        'footer-contatto': 'Contact',
        'footer-legal': 'Legal',
        'footer-privacy': 'Privacy Policy',
        'footer-terms': 'Terms of Service',
        'footer-cookies': 'Cookie Policy',
        'footer-gdpr': 'GDPR',
        'footer-copyright': '© 2025 Anzevino AI Real Estate. All rights reserved.',

        // Demo Conversation
        'demo-title': 'AI Conversation Example',
        'demo-ai-in-azione': 'AI in action',
        'demo-client-label': 'Client',
        'demo-ai-label': 'Anzevino AI',
        'demo-step-1-msg': 'Hello, I would like information about apartments in Milan Porta Nuova',
        'demo-step-2-msg': 'Hello! I am the agency\'s virtual assistant. To help you better, can you tell me your budget and what type you are looking for?',
        'demo-step-3-msg': 'Budget 400k, I\'d like a modern 2-room apartment',
        'demo-step-4-msg': 'Perfect! I found 3 apartments in Porta Nuova within your budget. Shall I send you the plans and organize a visit for Thursday at 4 PM?',
        'demo-step-5-msg': 'Yes, perfect! See you on Thursday then',
        'demo-step-6-msg': 'Confirmed! Appointment Thursday 4 PM in Via Dante 12. You\'ll receive a reminder tomorrow. Have a great day!',

        // Stats
        'stat-tempo-risposta': 'Response time',
        'stat-disponibilita': 'Availability',
        'stat-lead-qualificati': 'Qualified leads',



        // Benefits
        'benefit-demo': 'Personalized demo in 30 minutes',
        'benefit-setup': 'Free setup with no commitment',
        'benefit-formazione': 'Training included for your team',
        'benefit-supporto': 'Dedicated technical support',

        // Appraisal (Lead Magnet)
        'appraisal-tag': 'New',
        'appraisal-title': 'Discover your home\'s value in 15 seconds',
        'appraisal-subtitle': 'AI analyzes market prices in your area and sends you an instant valuation on WhatsApp. Free, fast, precise.',
        'appraisal-f1': 'Real-time Big Data analysis',
        'appraisal-f2': 'Direct results on WhatsApp',
        'appraisal-f3': 'Neighborhood precision',
        'appraisal-address-placeholder': 'Property address',
        'appraisal-postcode-placeholder': 'CAP / Postcode',
        'appraisal-phone-placeholder': 'Your WhatsApp (+39 ...)',
        'appraisal-cta': 'Get AI Valuation',
        'appraisal-disclaimer': 'Zero spam. Only the data you need.'
    }
};

// Language Switching Function
function switchLanguage(language) {
    // Update all translatable elements
    for (const [key, text] of Object.entries(translations[language])) {
        const elements = document.querySelectorAll(`[data-translate="${key}"]`);
        elements.forEach(element => {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = text;
            } else {
                element.textContent = text;
            }
        });
    }

    // Update HTML lang attribute
    document.documentElement.lang = language;

    // Update URL for language
    const currentUrl = window.location.href;
    if (currentUrl.includes('?lang=')) {
        const newUrl = currentUrl.replace(/\?lang=[a-z]{2}/, `?lang=${language}`);
        window.history.pushState({}, '', newUrl);
    } else {
        window.history.pushState({}, '', `${currentUrl}?lang=${language}`);
    }

    // Store language preference
    localStorage.setItem('preferredLanguage', language);
}

// Initialize Language
function initializeLanguage() {
    // Check URL parameter first
    const urlParams = new URLSearchParams(window.location.search);
    const urlLang = urlParams.get('lang');

    // Check localStorage
    const savedLang = localStorage.getItem('preferredLanguage');

    // Determine language (URL takes precedence over localStorage)
    let language = urlLang || savedLang || 'it';

    // Validate language
    if (!['it', 'en'].includes(language)) {
        language = 'it'; // Default to Italian
    }

    // Set active button
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === language) {
            btn.classList.add('active');
        }
    });

    // Apply translations
    switchLanguage(language);
}

// Language Toggle Functionality
const languageToggle = document.querySelector('.language-toggle');
if (languageToggle) {
    const langButtons = languageToggle.querySelectorAll('.lang-btn');

    langButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove active class from all buttons
            langButtons.forEach(btn => btn.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Get selected language
            const selectedLang = this.getAttribute('data-lang');

            // Switch language
            switchLanguage(selectedLang);

            // Show notification
            const languageName = selectedLang === 'it' ? 'Italiano' : 'English';
            if (typeof showNotification === 'function') {
                showNotification(`Lingua: ${languageName}`, 'info');
            }
        });
    });

    // Initialize language on page load
    initializeLanguage();
}

// Error handling
window.addEventListener('error', function (e) {
    console.error('JavaScript error:', e.error);
    // You could send this to an error tracking service
});
