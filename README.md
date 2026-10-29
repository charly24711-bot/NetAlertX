# 🛡️ NetAlertX - Despliegue en TrueNAS SCALE

Guía rápida y estructurada para desplegar **NetAlertX** (sistema de monitoreo, escaneo de intrusos y detección de dispositivos de red) en **TrueNAS SCALE** (`192.168.3.4`).

---

## 📋 ¿Qué se necesita para el proyecto?

1. **Modo de Red Host (`network_mode: "host"`)**:
   - Esencial para que NetAlertX pueda leer la tabla ARP real de la interfaz de red física y capturar paquetes RAW de dispositivos conectados a la subred `192.168.3.0/24`.
2. **Capacidades de Red (`NET_ADMIN`, `NET_RAW`)**:
   - Permiten escaneos ARP, ICMP (Ping) y Nmap dentro del contenedor.
3. **Persistencia de Datos (Datasets/Directorios en TrueNAS)**:
   - Configuración: `/mnt/Serranapool/APPS/netalertx/config`
   - Base de Datos (SQLite): `/mnt/Serranapool/APPS/netalertx/db`
   - Registros de Eventos: `/mnt/Serranapool/APPS/netalertx/logs`

---

## 🚀 Paso a Paso de Instalación en TrueNAS SCALE

### 1. Crear la estructura de directorios en el servidor
Conéctate por SSH a TrueNAS (`192.168.3.4`) y ejecuta:

```bash
# Crear directorio de la aplicación
mkdir -p /mnt/Serranapool/APPS/netalertx/{config,db,logs}

# Asignar permisos obligatorios
chown -R crolon:crolon /mnt/Serranapool/APPS/netalertx
chmod -R 775 /mnt/Serranapool/APPS/netalertx
```

### 2. Copiar los archivos del proyecto
Transfiere los archivos [`docker-compose.yml`](docker-compose.yml) y [`.env`](.env) a `/mnt/Serranapool/APPS/netalertx/`.

### 3. Levantar el Contenedor
Dentro de la carpeta del proyecto en TrueNAS:

```bash
cd /mnt/Serranapool/APPS/netalertx
docker compose up -d
```

### 4. Acceso y Verificación
- **URL Web:** `http://192.168.3.4:20211`
- **Comprobar logs:**
  ```bash
  docker compose logs -f
  ```
- **Validar servicio:**
  ```bash
  curl -I http://localhost:20211
  ```
