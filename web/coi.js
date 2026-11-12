// Memoria condivisa su un sito che non manda le intestazioni giuste (GitHub Pages).
// Lo stesso file fa due lavori: nella pagina registra se stesso come service worker e ricarica
// una volta; come service worker aggiunge a ogni risposta le due intestazioni (COOP e COEP)
// che danno alla pagina crossOriginIsolated, cioè lo SharedArrayBuffer per il Worker del 5-way.
// Con web/servi.py le intestazioni ci sono già: qui non succede niente.
if (typeof window === "undefined") {
  self.addEventListener("install", () => self.skipWaiting());
  self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));
  self.addEventListener("fetch", (e) => {
    const r = e.request;
    if (r.cache === "only-if-cached" && r.mode !== "same-origin") return;
    e.respondWith(
      fetch(r).then((res) => {
        if (res.status === 0) return res;
        const h = new Headers(res.headers);
        h.set("Cross-Origin-Embedder-Policy", "require-corp");
        h.set("Cross-Origin-Opener-Policy", "same-origin");
        return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
      }),
    );
  });
} else if (window.crossOriginIsolated) {
  try {
    sessionStorage.removeItem("maelcum-coi-ricaricato"); // dopo una ricarica forzata si può riprovare
  } catch {}
} else if (window.isSecureContext && "serviceWorker" in navigator) {
  const CHIAVE = "maelcum-coi-ricaricato";
  const ricarica = () => {
    let gia = false;
    try {
      gia = sessionStorage.getItem(CHIAVE) === "1";
      sessionStorage.setItem(CHIAVE, "1");
    } catch {}
    if (!gia) location.reload(); // una volta sola: se non basta, il 5-way gira nel filo del motore
  };
  navigator.serviceWorker.register(document.currentScript.src).then((reg) => {
    if (navigator.serviceWorker.controller) ricarica();
    else navigator.serviceWorker.addEventListener("controllerchange", ricarica, { once: true });
    if (reg.active && !navigator.serviceWorker.controller) ricarica();
  }).catch(() => {});
}
