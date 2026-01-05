// Service Worker for Offline Support & Caching
const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `anzevino-ai-${CACHE_VERSION}`;

// Assets to cache immediately on install
const STATIC_ASSETS = [
    '/appraisal/',
    '/appraisal/index.html',
    '/appraisal/dist/bundle.min.js',
    '/appraisal/dist/styles.min.css',
    '/appraisal/dist/modules.min.js',
    'https://unpkg.com/@phosphor-icons/web@2.0.3/src/regular/style.css'
];

// API endpoints to cache (with network-first strategy)
const API_ENDPOINTS = [
    '/api/leads',
    '/api/appraisals/estimate'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');

    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Caching static assets');
            return cache.addAll(STATIC_ASSETS);
        }).then(() => {
            console.log('[SW] Installation complete');
            return self.skipWaiting(); // Activate immediately
        }).catch((error) => {
            console.error('[SW] Installation failed:', error);
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');

    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name.startsWith('anzevino-ai-') && name !== CACHE_NAME)
                    .map((name) => {
                        console.log('[SW] Deleting old cache:', name);
                        return caches.delete(name);
                    })
            );
        }).then(() => {
            console.log('[SW] Activation complete');
            return self.clients.claim(); // Take control immediately
        })
    );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip cross-origin requests (except known CDNs)
    if (url.origin !== location.origin && !url.origin.includes('unpkg.com')) {
        return;
    }

    // API requests - Network-first strategy
    if (API_ENDPOINTS.some(endpoint => url.pathname.includes(endpoint))) {
        event.respondWith(networkFirst(request));
        return;
    }

    // Static assets - Cache-first strategy
    event.respondWith(cacheFirst(request));
});

// Cache-first strategy (for static assets)
async function cacheFirst(request) {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);

    if (cached) {
        console.log('[SW] Cache hit:', request.url);
        return cached;
    }

    console.log('[SW] Cache miss, fetching:', request.url);
    try {
        const response = await fetch(request);

        // Cache successful responses
        if (response.ok) {
            cache.put(request, response.clone());
        }

        return response;
    } catch (error) {
        console.error('[SW] Fetch failed:', error);

        // Return offline page if available
        const offlinePage = await cache.match('/offline.html');
        if (offlinePage) {
            return offlinePage;
        }

        // Fallback response
        return new Response('Offline - Content unavailable', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
                'Content-Type': 'text/plain'
            })
        });
    }
}

// Network-first strategy (for API calls)
async function networkFirst(request) {
    const cache = await caches.open(CACHE_NAME);

    try {
        const response = await fetch(request);

        // Cache successful API responses
        if (response.ok) {
            cache.put(request, response.clone());
        }

        return response;
    } catch (error) {
        console.error('[SW] Network request failed, trying cache:', error);

        const cached = await cache.match(request);
        if (cached) {
            console.log('[SW] Serving from cache (offline)');
            return cached;
        }

        throw error;
    }
}

// Background sync for form submissions (future enhancement)
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-appraisals') {
        event.waitUntil(syncAppraisals());
    }
});

async function syncAppraisals() {
    // Retrieve pending submissions from IndexedDB
    // Attempt to submit when back online
    console.log('[SW] Syncing pending appraisals...');
}

// Push notifications (future enhancement)
self.addEventListener('push', (event) => {
    const data = event.data.json();

    const options = {
        body: data.body,
        icon: '/icon-192.png',
        badge: '/badge-72.png',
        vibrate: [200, 100, 200]
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    event.waitUntil(
        clients.openWindow('/appraisal/')
    );
});

console.log('[SW] Service Worker loaded');
