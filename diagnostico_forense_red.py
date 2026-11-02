# -*- coding: utf-8 -*-
import csv
import subprocess
import time
import re
from concurrent.futures import ThreadPoolExecutor

CSV_FILE = r"c:\ENTORNO LOCAL\NetAlertX\inventario_red_ips_upms.csv"

def ping_stats(ip, count=3, timeout_ms=450):
    cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), ip]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3.5)
        out = res.stdout
        
        # Extraer porcentaje de pérdidas
        loss_m = re.search(r'\((\d+)%\s*(?:perdidos|loss)\)', out, re.IGNORECASE)
        loss = int(loss_m.group(1)) if loss_m else (0 if res.returncode == 0 else 100)
        
        # Extraer RTT promedio
        rtt_m = re.search(r'(?:Media|Average)\s*=\s*(\d+)ms', out, re.IGNORECASE)
        avg_rtt = int(rtt_m.group(1)) if rtt_m else (-1 if loss == 100 else 0)
        
        # Extraer RTT máximo
        max_m = re.search(r'(?:M[aá]ximo|Maximum)\s*=\s*(\d+)ms', out, re.IGNORECASE)
        max_rtt = int(max_m.group(1)) if max_m else avg_rtt
        
        return loss, avg_rtt, max_rtt
    except Exception as e:
        return 100, -1, -1

def main():
    targets = []
    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ip = row.get('IP', '').strip()
            if ip and ip.startswith('192.168.3.'):
                targets.append({
                    'ip': ip,
                    'host': row.get('Hostname', 'DESCONOCIDO'),
                    'sector': row.get('Departamento_Sector', ''),
                    'usuario': row.get('Responsable_Usuario', ''),
                    'tipo': row.get('Tipo_Equipo', '')
                })

    print(f"[*] Iniciando auditoria forense en paralelo de {len(targets)} nodos...")
    t0 = time.time()
    
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_map = {executor.submit(ping_stats, t['ip']): t for t in targets}
        for fut in future_map:
            t = future_map[fut]
            loss, avg_rtt, max_rtt = fut.result()
            results.append({
                'ip': t['ip'],
                'host': t['host'],
                'sector': t['sector'],
                'usuario': t['usuario'],
                'tipo': t['tipo'],
                'loss': loss,
                'avg_rtt': avg_rtt,
                'max_rtt': max_rtt
            })

    elapsed = round(time.time() - t0, 1)
    print(f"[+] Escaneo completado en {elapsed}s\n")
    
    # Separar en categorías
    criticos = []
    con_problemas = []
    saludables = []
    offline = []
    
    for r in results:
        if r['loss'] == 100:
            offline.append(r)
        elif r['loss'] > 0 or r['avg_rtt'] > 15 or r['max_rtt'] > 30:
            con_problemas.append(r)
        else:
            saludables.append(r)

    print("=" * 85)
    print("  RESULTADO DEL DIAGNÓSTICO FORENSE DE RED - UPMS CDE")
    print("=" * 85)
    
    print("\n[!] NODOS CON PÉRDIDA DE PAQUETES O LATENCIA ALTA (>15ms / Jitter):")
    if con_problemas:
        for r in con_problemas:
            print(f"  -> IP: {r['ip']:<15} | Loss: {r['loss']:>3}% | RTT Avg: {r['avg_rtt']:>2}ms (Max: {r['max_rtt']:>2}ms) | {r['host']:<16} | {r['usuario']} ({r['sector']})")
    else:
        print("  (Ningun nodo activo reporto degradacion severa en esta muestra puntual)")

    print("\n[+] INFRAESTRUCTURA TRONCAL (Servidores, Switches, APs):")
    for r in results:
        if any(keyword in r['tipo'].lower() or keyword in r['host'].lower() for keyword in ['router', 'servidor', 'switch', 'access point', 'ap-', 'truenas', 'gateway', 'server']):
            estado = "OFFLINE" if r['loss'] == 100 else f"OK ({r['avg_rtt']}ms)"
            print(f"  * {r['ip']:<15} {r['host']:<16} : {estado:<12} (Loss: {r['loss']}%) | {r['tipo']}")

    print("\n[-] EQUIPOS OFFLINE (Apagados o sin responder ICMP):")
    print(f"  Total offline: {len(offline)} de {len(targets)}")
    for r in offline[:10]:
        print(f"  x {r['ip']:<15} {r['host']:<16} - {r['usuario']} ({r['sector']})")
    if len(offline) > 10:
        print(f"  ... y {len(offline) - 10} equipos mas.")

if __name__ == '__main__':
    main()
