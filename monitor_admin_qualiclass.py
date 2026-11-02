# -*- coding: utf-8 -*-
"""
MONITOR CONTINUO FORENSE: ADMINISTRACIÓN Y CAJAS -> QUALICLASS & GATEWAY (UPMS CDE)
Mide en tiempo real la latencia y disponibilidad de:
  - Servidor Qualiclass (192.168.3.99)
  - Admin / Caja 1       (192.168.3.39)
  - Caja 2               (192.168.3.23)
  - Administración 2     (192.168.3.84)
  - Finanzas             (192.168.3.24)
  - MikroTik Gateway     (192.168.3.1)
"""
import os
import sys
import time
import subprocess
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

TARGETS = [
    {"ip": "192.168.3.99", "name": "SERVER-MS (Qualiclass)"},
    {"ip": "192.168.3.39", "name": "Admin / Caja 1"},
    {"ip": "192.168.3.23", "name": "Caja 2"},
    {"ip": "192.168.3.84", "name": "Administracion 2"},
    {"ip": "192.168.3.24", "name": "Finanzas"},
    {"ip": "192.168.3.1",  "name": "MikroTik Gateway"}
]

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, f"monitor_admin_qualiclass_{datetime.now().strftime('%Y-%m-%d')}.log")

def ping_host(ip, timeout_ms=350):
    t0 = time.time()
    try:
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=0.8)
        elapsed = int((time.time() - t0) * 1000)
        if res.returncode == 0:
            m = re.search(r'(?:tiempo|time)[=<](\d+)ms', res.stdout, re.IGNORECASE)
            rtt = int(m.group(1)) if m else elapsed
            return max(0, rtt)
        return -1
    except:
        return -1

def main():
    print("=" * 96)
    print("  MONITOR FORENSE EN VIVO: ADMIN, CAJA 1, CAJA 2 Y FINANZAS -> QUALICLASS (UPMS CDE)")
    print(f"  Archivo de log: {LOG_FILE}")
    print("  Muestreo: cada 1 segundo | Registra picos >15ms o caidas")
    print("=" * 96)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n=== INICIO SESION MONITOR (INCLUYE CAJA 2): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    cycle = 0
    while True:
        cycle += 1
        now_str = datetime.now().strftime("%H:%M:%S")

        # Pings concurrentes ultra-rápidos
        rtts = {}
        with ThreadPoolExecutor(max_workers=6) as ex:
            future_map = {ex.submit(ping_host, t["ip"]): t["ip"] for t in TARGETS}
            for fut in future_map:
                rtts[future_map[fut]] = fut.result()

        srv    = rtts.get("192.168.3.99", -1)
        caja1  = rtts.get("192.168.3.39", -1)
        caja2  = rtts.get("192.168.3.23", -1)
        admin2 = rtts.get("192.168.3.84", -1)
        finan  = rtts.get("192.168.3.24", -1)
        gw     = rtts.get("192.168.3.1", -1)

        def fmt(val):
            if val == -1: return "OFFLINE"
            return f"{val:>2}ms"

        # Detectar degradación relevante
        anomalia = False
        alertas = []

        if srv == -1:
            anomalia = True
            alertas.append("QUALICLASS CAIDO")
        elif srv > 15:
            anomalia = True
            alertas.append(f"PICO QUALICLASS ({srv}ms)")

        # Picos de latencia en terminales encendidas
        if caja1 > 20: alertas.append(f"Pico Caja1 ({caja1}ms)")
        if caja2 > 20: alertas.append(f"Pico Caja2 ({caja2}ms)")
        if admin2 > 20: alertas.append(f"Pico Admin2 ({admin2}ms)")
        if finan > 20: alertas.append(f"Pico Finanzas ({finan}ms)")

        if gw > 20:
            anomalia = True
            alertas.append(f"PICO ROUTER ({gw}ms)")

        status_text = " | ".join(alertas) if alertas else "OK ESTABLE"
        msg = f"[{now_str}] Qualiclass: {fmt(srv):<7} | Caja1: {fmt(caja1):<7} | Caja2: {fmt(caja2):<7} | Admin2: {fmt(admin2):<7} | Finanzas: {fmt(finan):<7} | Router: {fmt(gw):<7} | {status_text}"

        if anomalia or alertas:
            print(f"[*] {msg}")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}] [ALERTA] {msg}\n")
        elif cycle % 5 == 0:
            print(f"    {msg}")

        # Guardar muestra estable en el archivo cada 60s
        if cycle % 60 == 0:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{now_str}] [STATUS] {msg}\n")

        time.sleep(1.0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Monitor finalizado.")
