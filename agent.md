# 🤖 Antigravity Workspace Guidelines (AGENTS.md)

Este documento define el contexto, estándares y reglas del espacio de trabajo para los agentes de **Google Antigravity**.

---

## 📁 1. Estructura y Módulos del Espacio de Trabajo

El espacio de trabajo contiene dos componentes principales:

### A. Aplicación Web: "Diario de Estudio"
* **Propósito:** Registro personal de sesiones de estudio y seguimiento de constancia mediante rachas consecutivas (🔥).
* **Archivos clave:**
  * [`index.html`](index.html): Estructura semántica accesible en español.
  * [`styles.css`](styles.css): Diseño moderno, centrado en tarjetas y responsivo (móvil y escritorio).
  * [`app.js`](app.js): Lógica de fechas locales, cálculo de racha diaria y persistencia en `localStorage`.

### B. Infraestructura: "NetAlertX" (Monitoreo de Red en TrueNAS SCALE)
* **Propósito:** Detección de intrusos, escaneo de subred `192.168.3.0/24` y monitoreo de dispositivos.
* **Servidor destino:** TrueNAS SCALE (`192.168.3.4`) en `/mnt/Serranapool/APPS/netalertx`.
* **Archivos clave:**
  * [`docker-compose.yml`](docker-compose.yml): Contenedor con `network_mode: "host"`, volumen `/data` y capacidades `NET_ADMIN`/`NET_RAW`.
  * [`.env`](.env): Variables de entorno (`America/Asuncion`, puerto `20211`, `PUID=950`).
  * [`README.md`](README.md): Guía y SOP de despliegue.

---

## 🛠️ 2. Convenciones de Desarrollo Frontend

1. **Stack Ligero:** Únicamente HTML5, CSS3 y JavaScript Vanilla. Sin frameworks (React, Vue, etc.) ni compiladores.
2. **Ejecución Local:** Toda aplicación frontend debe funcionar con doble clic en `index.html` sin requerir servidor local obligatorio.
3. **Manejo de Fechas:** Usar siempre la **hora local** del usuario (`new Date().getFullYear()`, `.getMonth()`, `.getDate()`), evitando conversiones UTC que desfasen días.
4. **Persistencia:** Almacenar datos en `localStorage` con claves descriptivas.
5. **Idioma:** Interfaz, mensajes y validaciones 100% en español.

---

## 🚢 3. Convenciones DevOps (TrueNAS SCALE)

1. **Ruta Base de Aplicaciones:** `/mnt/Serranapool/APPS/<nombre_proyecto>`
2. **Permisos de Archivos:** Asignar siempre propietario `truenas_admin:truenas_admin` (o `crolon:crolon`) con `chmod -R 775`.
3. **Modo de Red para Escaneo:** Obligatoriamente `network_mode: "host"` para escaneo ARP y resolución física de MACs.
4. **Reinicio Seguro:**
   ```bash
   cd /mnt/Serranapool/APPS/<proyecto> && docker compose down && docker compose up -d
   ```
