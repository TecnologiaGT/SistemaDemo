"""Soporte de "Progressive Web App" (PWA): permite instalar el sistema como
si fuera una app en el celular (Android/iPhone), con su propio ícono y sin
la barra del navegador.

manifest_view sirve el manifest.webmanifest de forma DINÁMICA (no como
archivo estático) para que el nombre mostrado siga el tipo de sistema
elegido (Personalizacion.nombre_sistema) y el color coincida con la paleta
elegida. service_worker_view sirve sw.js desde la raíz del sitio (no desde
/static/) a propósito: así su "scope" cubre TODO el sitio sin necesitar
configuración extra en el servidor.

El service worker es intencionalmente muy limitado: solo cachea archivos
estáticos (CSS/JS/íconos) para que la instalación sea válida y la app
cargue un poco más rápido; nunca cachea páginas ni datos, porque este es
un sistema de ventas en vivo y no debe mostrar información vieja guardada
en el teléfono.
"""
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static

from .models import Personalizacion
from .paletas import variables_css

NOMBRE_CORTO = "T&P Demo"

SERVICE_WORKER_JS = """
const CACHE = "tp-demo-shell-v1";

self.addEventListener("install", (event) => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((nombres) =>
      Promise.all(nombres.filter((n) => n !== CACHE).map((n) => caches.delete(n)))
    )
  );
  self.clients.claim();
});

// Solo se cachean archivos estáticos (CSS/JS/íconos). Cualquier otra
// petición (páginas, formularios, login, datos) siempre va directo a la
// red: este es un sistema de ventas/compras en vivo y nunca debe mostrar
// información vieja guardada en el teléfono.
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || !url.pathname.startsWith("/static/")) {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cacheada) => {
      if (cacheada) return cacheada;
      return fetch(event.request).then((respuesta) => {
        const copia = respuesta.clone();
        caches.open(CACHE).then((cache) => cache.put(event.request, copia));
        return respuesta;
      });
    })
  );
});
""".strip()


def manifest_view(request):
    config = Personalizacion.obtener()
    variables = variables_css(config.paleta)
    datos = {
        "name": config.nombre_sistema,
        "short_name": NOMBRE_CORTO,
        "description": "Sistema de inventario, ventas y compras para demostraciones.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait-primary",
        "lang": "es",
        "background_color": variables.get("fondo-2", "#0a1230"),
        "theme_color": variables.get("azul-900", "#0f1a3d"),
        "icons": [
            {"src": static("pwa/icon-192.png"), "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": static("pwa/icon-192-maskable.png"), "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
            {"src": static("pwa/icon-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": static("pwa/icon-512-maskable.png"), "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    return JsonResponse(datos, content_type="application/manifest+json")


def service_worker_view(request):
    return HttpResponse(
        SERVICE_WORKER_JS,
        content_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )
