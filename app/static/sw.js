// AuraRise Service Worker - Pure Proxy & Cache Bypass Protocol (v3.0)
const CACHE_NAME = 'aurarise-v3-bypass';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => caches.delete(cache))
      );
    }).then(() => self.clients.claim())
  );
});

// Always fetch directly from network to ensure 100% fresh real-time server updates
self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request));
});
