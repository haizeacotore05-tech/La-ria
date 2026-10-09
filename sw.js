// La Ría — service worker: la app abre sin conexión y guarda las ediciones leídas.
const SHELL = "laria-shell-v2";
const DATA = "laria-data-v1";
const SHELL_FILES = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => ![SHELL, DATA].includes(k)).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  // Datos: primero la red (lo más nuevo); si no hay conexión, lo guardado.
  if (url.origin === location.origin && url.pathname.includes("/data/")) {
    e.respondWith(fetch(e.request).then(res => {
      const copy = res.clone(); caches.open(DATA).then(c => c.put(e.request, copy)); return res;
    }).catch(() => caches.match(e.request)));
    return;
  }
  // Página y fuentes: primero la red para la página, caché para el resto.
  if (url.origin === location.origin && (e.request.mode === "navigate" || url.pathname.endsWith("/index.html"))) {
    e.respondWith(fetch(e.request).then(res => {
      const copy = res.clone(); caches.open(SHELL).then(c => c.put("index.html", copy)); return res;
    }).catch(() => caches.match("index.html")));
    return;
  }
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
    if (res.ok && (url.origin === location.origin || url.hostname.endsWith("gstatic.com") || url.hostname.endsWith("googleapis.com"))) {
      const copy = res.clone(); caches.open(SHELL).then(c => c.put(e.request, copy));
    }
    return res;
  })));
});
