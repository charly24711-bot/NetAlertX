import os
import time
import paramiko

host = '192.168.3.4'
username = 'crolon'
password = '24711351'
remote_app_dir = '/mnt/Serranapool/APPS/medikquest'
local_src_dir = r'c:\ENTORNO LOCAL\NetAlertX\MedikQuest'

docker_compose_content = """services:
  medikquest:
    image: nginx:alpine
    container_name: upms_medikquest
    restart: unless-stopped
    ports:
      - "3040:80"
    volumes:
      - ./public:/usr/share/nginx/html:ro
"""

print(f"==> Conectando a TrueNAS SCALE ({host})...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password, timeout=10)

print(f"==> Preparando directorios en {remote_app_dir}...")
ssh.exec_command(f"echo '{password}' | sudo -S mkdir -p {remote_app_dir}/public")
ssh.exec_command(f"echo '{password}' | sudo -S chown -R {username}:{username} {remote_app_dir}")
time.sleep(1)

sftp = ssh.open_sftp()

def upload_dir(local_path, remote_path):
    try:
        sftp.mkdir(remote_path)
    except IOError:
        pass
    for item in os.listdir(local_path):
        if item in ['.git', '__pycache__', 'node_modules']:
            continue
        l_item = os.path.join(local_path, item)
        r_item = f"{remote_path}/{item}"
        if os.path.isdir(l_item):
            upload_dir(l_item, r_item)
        else:
            print(f"Subiendo {r_item}...")
            sftp.put(l_item, r_item)

print("==> Subiendo archivos del juego a TrueNAS...")
upload_dir(local_src_dir, f"{remote_app_dir}/public")

# Subir docker-compose.yml
with sftp.file(f"{remote_app_dir}/docker-compose.yml", 'w') as f:
    f.write(docker_compose_content)

sftp.close()

print("==> Orquestando contenedor Docker en TrueNAS (puerto 3070)...")
cmds = [
    f"cd {remote_app_dir} && echo '{password}' | sudo -S docker compose down 2>/dev/null || true",
    f"cd {remote_app_dir} && echo '{password}' | sudo -S docker compose up -d"
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()

time.sleep(2)

print("==> Verificando Healthcheck en http://127.0.0.1:3040...")
stdin, stdout, stderr = ssh.exec_command("curl -I http://127.0.0.1:3040")
output = stdout.read().decode('utf-8', 'ignore')
print("Respuesta de TrueNAS:")
print(output)

ssh.close()
print("==> ¡Despliegue de MedikQuest completado exitosamente en TrueNAS!")
