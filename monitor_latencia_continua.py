# -*- coding: utf-8 -*-
import subprocess
import time
import re
from datetime import datetime

LOG_FILE = r"c:\ENTORNO LOCAL\NetAlertX\latencia_continua.log"

def medir_rtt(host, timeout_ms=500):
    t0 = time.time()
    try:
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), host]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1.0)
        elapsed = int((time.time() - t0) * 1000)
        if res.returncode == 0:
            m = re.search(r'(?:tiempo|time)[=<](\d+)ms', res.stdout, re.IGNORECASE)
            rtt = int(m.group(1)) if m else elapsed
            return max(0, rtt)
        return -1 # Pérdida
    except:
        return -1

def main():
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n=== INICIO MONITOREO CONTINUO DE LATENCIA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        
    print(f"Monitoreando latencia continua cada 1s en {LOG_FILE}...")
    
    contador = 0
    picos_detectados = 0
    perdidas_detectadas = 0
    
    while True:
        contador += 1
        now_str = datetime.now().strftime("%H:%M:%S")
        
        rtt_gw  = medir_rtt("192.168.3.1", timeout_ms=400)
        rtt_net = medir_rtt("8.8.8.8", timeout_ms=600)
        rtt_srv = medir_rtt("192.168.3.99", timeout_ms=400)
        
        anomalia = False
        detalles = []
        
        if rtt_gw == -1 or rtt_net == -1 or rtt_srv == -1:
            anomalia = True
            perdidas_detectadas += 1
            detalles.append(f"PAQUETE PERDIDO -> GW:{rtt_gw}ms, NET:{rtt_net}ms, SRV:{rtt_srv}ms")
        elif rtt_gw > 10 or rtt_net > 40 or rtt_srv > 15:
            anomalia = True
            picos_detectados += 1
            detalles.append(f"PICO DE LATENCIA -> GW:{rtt_gw}ms, NET:{rtt_net}ms, SRV:{rtt_srv}ms")
            
        if anomalia:
            line = f"[{now_str}] [ALERTA] {' | '.join(detalles)}"
            print(line)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        elif contador % 10 == 0:
            status_line = f"[{now_str}] [OK SALUDABLE] Muestras: {contador} | Router: {rtt_gw}ms | Internet: {rtt_net}ms | Servidor: {rtt_srv}ms | Picos: {picos_detectados} | Perdidas: {perdidas_detectadas}"
            print(status_line)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(status_line + "\n")
                
        time.sleep(1)

if __name__ == "__main__":
    main()
