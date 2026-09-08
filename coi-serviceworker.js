// coi-serviceworker.js
//
// Multi-threaded ffmpeg.wasm needs SharedArrayBuffer, which browsers only
// expose on "cross-origin isolated" pages — pages served with the
// Cross-Origin-Opener-Policy and Cross-Origin-Embedder-Policy response
// headers. Static hosts like GitHub Pages don't let you set response
// headers, so this service worker adds them itself by intercepting every
// same-origin fetch and rewriting the response headers on the way back.
//
// Usage: put this file next to index.html and load it before anything else:
//   <script src="./coi-serviceworker.js"></script>
// Requires HTTPS (or localhost) — service workers don't run on file:// or
// plain HTTP, so this has no effect when the page is opened as a local file.

if (typeof window === 'undefined') {
  // We ARE the service worker.
  self.addEventListener('install', () => self.skipWaiting());
  self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));

  self.addEventListener('fetch', (event) => {
    const request = event.request;
    // Don't touch cross-origin or cache-only requests — we can't safely
    // rewrite headers on responses we don't control.
    if (request.cache === 'only-if-cached' && request.mode !== 'same-origin') return;

    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.status === 0) return response; // opaque cross-origin response
          const headers = new Headers(response.headers);
          headers.set('Cross-Origin-Embedder-Policy', 'require-corp');
          headers.set('Cross-Origin-Opener-Policy', 'same-origin');
          return new Response(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers,
          });
        })
        .catch(() => new Response(null, { status: 599, statusText: 'coi-serviceworker fetch failed' }))
    );
  });
} else {
  // We're running in the page: register ourselves, then reload once we're
  // actually controlling the page so the isolation headers apply.
  (async () => {
    if (window.crossOriginIsolated) return; // already isolated, nothing to do
    if (!window.isSecureContext) {
      console.warn('coi-serviceworker: needs HTTPS or localhost — skipping (protocol: ' + location.protocol + ')');
      return;
    }
    if (!('serviceWorker' in navigator)) {
      console.warn('coi-serviceworker: service workers unsupported in this browser');
      return;
    }
    try {
      const registration = await navigator.serviceWorker.register(document.currentScript.src);
      registration.addEventListener('updatefound', () => window.location.reload());
      if (registration.active && !navigator.serviceWorker.controller) {
        window.location.reload();
      }
    } catch (err) {
      console.warn('coi-serviceworker: registration failed', err);
    }
  })();
}
