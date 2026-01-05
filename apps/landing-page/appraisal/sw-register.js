// Service Worker Registration
// Add to main script.js or create separate file

if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
        try {
            const registration = await navigator.serviceWorker.register('/appraisal/sw.js', {
                scope: '/appraisal/'
            });

            console.log('✅ Service Worker registered:', registration.scope);

            // Check for updates periodically
            setInterval(() => {
                registration.update();
            }, 60 * 60 * 1000); // Check every hour

            // Listen for updates
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;

                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        // New version available
                        showUpdateNotification();
                    }
                });
            });

        } catch (error) {
            console.error('❌ Service Worker registration failed:', error);
        }
    });
}

function showUpdateNotification() {
    const banner = document.createElement('div');
    banner.className = 'update-banner';
    banner.innerHTML = `
        <p>🎉 New version available!</p>
        <button onclick="location.reload()">Update Now</button>
        <button onclick="this.parentElement.remove()">Later</button>
    `;
    document.body.appendChild(banner);
}

// Detect online/offline status
window.addEventListener('online', () => {
    console.log('🟢 Back online');
    showNotification('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    console.log('🔴 Offline mode');
    showNotification('No internet connection - Using cached version', 'warning');
});
