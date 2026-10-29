# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Lista de equipos críticos a vigilar segundo a segundo
MONITOR_TARGETS = [
    ("192.168.3.1",   "MikroTik Core (Gateway)", "Datacenter"),
    ("192.168.3.4",   "TrueNAS SCALE",          "Datacenter"),
    ("192.168.3.99",  "SERVER-MS (Qualiclass)", "Datacenter"),
    ("192.168.3.69",  "AP TP-Link Planta Alta", "Pasillo PA"),
    ("192.168.3.39",  "Admin / Caja 1",         "Administración"),
    ("192.168.3.23",  "Caja 2",                 "Caja"),
    ("192.168.3.24",  "Finanzas",               "Finanzas"),
    ("192.168.3.36",  "Recepción",              "Hall Principal"),
    ("192.168.3.81",  "Caja 1 CDE",             "Planta Baja"),
    ("192.168.3.84",  "Administración 2",       "Administración"),
    ("192.168.3.123", "Coordinación Académica", "Académica"),
    ("192.168.3.147", "Oficina Ciclos",         "Administración"),
    ("192.168.3.222", "Laura Romero (RRHH)",    "Talento Humano"),
    ("192.168.3.204", "Atención al Alumno",     "Secretaría"),
    ("192.168.3.250", "PC Archivos/Legajos",    "Legajos"),
    ("192.168.3.62",  "Kiosco Digital TV",      "Recepción")
]

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, f"cazador_anomalias_{datetime.now().strftime('%Y-%m-%d')}.log")

def ping_host(ip, timeout_ms=350):
    try:
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1.0)
        return p.returncode == 0
    except:
        return False

def main():
    print("=" * 75)
    print("  INICIANDO CAZADOR FORENSE DE RED - UPMS CDE (VENTANA 16:00 - 17:30)")
    print(f"  Vigilando {len(MONITOR_TARGETS)} nodos troncales y estaciones de trabajo...")
    print(f"  Registro guardandose en: {LOG_FILE}")
    print("=" * 75)
    
    last_states = {}
    last_change_time = {}
    
    # Inicializar estados
    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = {ex.submit(ping_host, ip): (ip, name, sec) for ip, name, sec in MONITOR_TARGETS}
        for f in futures:
            ip, name, sec = futures[f]
            st = f.result()
            last_states[ip] = st
            last_change_time[ip] = datetime.now()
            print(f"  [{'ONLINE' if st else 'OFFLINE':<7}] {ip:<15} - {name} ({sec})")
            
    print("\n[+] Monitoreo en vivo activado. Presiona Ctrl+C para detener.\n")
    
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"\n--- INICIO SESION CAZADOR {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")

    iteration = 0
    while True:
        iteration += 1
        t_now = datetime.now()
        current_states = {}
        
        with ThreadPoolExecutor(max_workers=16) as ex:
            futures = {ex.submit(ping_host, ip): ip for ip, _, _ in MONITOR_TARGETS}
            for f in futures:
                ip = futures[f]
                current_states[ip] = f.result()
                
        # Evaluar cambios de estado
        for ip, name, sec in MONITOR_TARGETS:
            old = last_states.get(ip)
            new = current_states.get(ip)
            
            if old != new:
                last_states[ip] = new
                last_change_time[ip] = t_now
                hora_str = t_now.strftime("%H:%M:%S")
                
                if not new:
                    # Se apagó o desconectó
                    msg = f"[{hora_str}] [APAGADO/DESCONEXION] {ip:<15} ({name} - {sec}) se fue a OFFLINE."
                    print(msg)
                else:
                    # Se encendió o conectó
                    msg = f"[{hora_str}] [ENCENDIDO/CONEXION]  {ip:<15} ({name} - {sec}) paso a ONLINE."
                    print(msg)
                    
                with open(LOG_FILE, "a", encoding="utf-8") as log:
                    log.write(msg + "\n")
                    
        # Verificar si el Gateway o el Servidor tienen caída
        gw_ok = current_states.get("192.168.3.1", True)
        srv_ok = current_states.get("192.168.3.99", True)
        ap_ok = current_states.get("192.168.3.69", True)
        
        if not gw_ok or not srv_ok or not ap_ok:
            hora_str = t_now.strftime("%H:%M:%S")
            alert = f"\n*** [{hora_str}] ANOMALIA / CAIDA DETECTADA EN LA RED! (Router: {'OK' if gw_ok else 'FALLO'}, Servidor: {'OK' if srv_ok else 'FALLO'}, AP: {'OK' if ap_ok else 'FALLO'}) ***"
            print(alert)
            
            # Buscar que estaciones se apagaron o encendieron en los ultimos 90 segundos
            print("  --- Sospechosos recientes (cambios en el ultimo minuto y medio): ---")
            found_suspect = False
            for ip, name, sec in MONITOR_TARGETS:
                if ip not in ["192.168.3.1", "192.168.3.99", "192.168.3.69"]:
                    delta = (t_now - last_change_time[ip]).total_seconds()
                    if delta <= 90:
                        found_suspect = True
                        st_str = "SE APAGO" if not current_states[ip] else "SE CONECTO"
                        s_msg = f"   -> IP {ip} ({name} - {sec}) {st_str} hace {int(delta)} segundos!"
                        print(s_msg)
                        with open(LOG_FILE, "a", encoding="utf-8") as log:
                            log.write(f"   [SOSPECHOSO] {s_msg}\n")
            if not found_suspect:
                print("   (No hubo cambios de estado recientes en las estaciones monitoreadas)")
            print("-" * 75 + "\n")
            
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCazador finalizado por el usuario.")
