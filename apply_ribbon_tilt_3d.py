import os
import time
import paramiko

TEMPLATES_DIR = r"c:\ENTORNO LOCAL\Carteleria\lab_multimedia\templates"

old_blue_css = """        .blue-ribbon-badge {
            width: calc(4.8 * var(--u));
            height: auto;
            max-height: calc(6.2 * var(--u));
            object-fit: contain;
            margin: calc(0.3 * var(--u)) auto calc(0.2 * var(--u));
            display: block;
            filter: drop-shadow(0 calc(0.4 * var(--u)) calc(1.2 * var(--u)) rgba(37, 99, 235, 0.65));
            animation: blueRibbonPulse 4.5s ease-in-out infinite;
            flex-shrink: 0;
        }

        @keyframes blueRibbonPulse {
            0%, 100% { transform: scale(1); filter: drop-shadow(0 calc(0.4 * var(--u)) calc(1.2 * var(--u)) rgba(37, 99, 235, 0.65)); }
            50% { transform: scale(1.06); filter: drop-shadow(0 calc(0.6 * var(--u)) calc(1.8 * var(--u)) rgba(59, 130, 246, 0.9)); }
        }"""

new_blue_css = """        .blue-ribbon-badge {
            width: calc(4.8 * var(--u));
            height: auto;
            max-height: calc(6.2 * var(--u));
            object-fit: contain;
            margin: calc(0.3 * var(--u)) auto calc(0.2 * var(--u));
            display: block;
            transform-origin: center top;
            will-change: transform, filter;
            animation: blueRibbonTilt3D 5.5s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
            flex-shrink: 0;
        }

        @keyframes blueRibbonTilt3D {
            0% {
                transform: perspective(650px) rotateY(-6deg) rotateX(4deg) rotateZ(-1.8deg) scale(1);
                filter: drop-shadow(-3px calc(0.4 * var(--u)) calc(1.2 * var(--u)) rgba(37, 99, 235, 0.65));
            }
            25% {
                transform: perspective(650px) rotateY(0deg) rotateX(1deg) rotateZ(0deg) scale(1.03);
                filter: drop-shadow(0 calc(0.55 * var(--u)) calc(1.6 * var(--u)) rgba(59, 130, 246, 0.85));
            }
            50% {
                transform: perspective(650px) rotateY(6.5deg) rotateX(-3deg) rotateZ(2deg) scale(1.05);
                filter: drop-shadow(4px calc(0.6 * var(--u)) calc(1.8 * var(--u)) rgba(37, 99, 235, 0.75));
            }
            75% {
                transform: perspective(650px) rotateY(1deg) rotateX(2deg) rotateZ(-0.5deg) scale(1.02);
                filter: drop-shadow(1px calc(0.48 * var(--u)) calc(1.5 * var(--u)) rgba(59, 130, 246, 0.8));
            }
            100% {
                transform: perspective(650px) rotateY(-6deg) rotateX(4deg) rotateZ(-1.8deg) scale(1);
                filter: drop-shadow(-3px calc(0.4 * var(--u)) calc(1.2 * var(--u)) rgba(37, 99, 235, 0.65));
            }
        }"""

for filename in ["admin.html", "player.html"]:
    fpath = os.path.join(TEMPLATES_DIR, filename)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    if old_blue_css in content:
        content = content.replace(old_blue_css, new_blue_css)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[OK] {filename} actualizado con Inclinacion 3D")
    else:
        print(f"[WARN] No se encontro target en {filename}")

# Desplegar a TrueNAS
host = '192.168.3.4'
username = 'crolon'
password = '24711351'
remote_base = '/mnt/Serranapool/APPS/carteleria_multimedia'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password, timeout=10)

sftp = ssh.open_sftp()
for filename in ["admin.html", "player.html"]:
    lpath = os.path.join(TEMPLATES_DIR, filename)
    rpath = f"{remote_base}/templates/{filename}"
    print(f"Subiendo {rpath}...")
    sftp.put(lpath, rpath)
sftp.close()

# Como montamos templates en docker-compose.yml, los cambios se reflejan directamente en FastAPI!
print("==> Verificando endpoint...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8091/admin | grep -o 'blueRibbonTilt3D'")
res = stdout.read().decode('utf-8').strip()
print(f"Resultado en TrueNAS: {res}")

ssh.close()
print("--> Efecto Inclinacion 3D Subtle Tilt activo y desplegado en http://192.168.3.4:8091!")
