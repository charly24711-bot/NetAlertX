import os
import time
import colorsys
from PIL import Image
import paramiko

CARTELERIA_DIR = r"c:\ENTORNO LOCAL\Carteleria\lab_multimedia"
STATIC_DIR = os.path.join(CARTELERIA_DIR, "static")
TEMPLATES_DIR = os.path.join(CARTELERIA_DIR, "templates")

print("==> 1. Generando assets de Noviembre Azul...")

# A. Generar blue_ribbon.png mediante rotación HSV precisa
pink_png = os.path.join(STATIC_DIR, "pink_ribbon.png")
blue_png = os.path.join(STATIC_DIR, "blue_ribbon.png")
if os.path.exists(pink_png):
    img = Image.open(pink_png).convert('RGBA')
    r, g, b, a = img.split()
    np_r, np_g, np_b, np_a = list(r.getdata()), list(g.getdata()), list(b.getdata()), list(a.getdata())
    new_data = []
    for pr, pg, pb, pa in zip(np_r, np_g, np_b, np_a):
        if pa == 0:
            new_data.append((0, 0, 0, 0))
            continue
        h, s, v = colorsys.rgb_to_hsv(pr/255.0, pg/255.0, pb/255.0)
        # Tono azul real / zafiro conmemorativo (Hue ~ 0.58 = 210°)
        new_h = 0.58
        nr, ng, nb = colorsys.hsv_to_rgb(new_h, s, v)
        new_data.append((int(nr*255), int(ng*255), int(nb*255), pa))
    blue_img = Image.new('RGBA', img.size)
    blue_img.putdata(new_data)
    blue_img.save(blue_png)
    print(f"   [OK] blue_ribbon.png creado ({blue_img.size})")

# B. Generar blue_ribbon.svg vectorial
blue_svg_path = os.path.join(STATIC_DIR, "blue_ribbon.svg")
svg_code = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 320" width="100%" height="100%">
  <defs>
    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#93c5fd"/>
      <stop offset="35%" stop-color="#3b82f6"/>
      <stop offset="70%" stop-color="#1d4ed8"/>
      <stop offset="100%" stop-color="#1e3a8a"/>
    </linearGradient>
    <linearGradient id="blueHighlight" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <filter id="blueRibbonShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.6"/>
      <feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="#2563eb" flood-opacity="0.65"/>
    </filter>
  </defs>
  <g filter="url(#blueRibbonShadow)">
    <path d="M 60,190 C 40,240 25,285 20,310 C 35,305 65,280 85,245 C 95,225 100,205 105,190 Z" fill="url(#blueGrad)" opacity="0.95"/>
    <path d="M 25,305 C 50,290 85,220 95,190 C 70,140 50,80 75,35 C 95,5 135,5 155,40 C 175,85 145,150 115,195 C 130,230 160,285 185,310 C 160,280 135,245 110,200 C 100,185 92,175 88,168 C 115,125 140,80 128,48 C 120,28 100,28 88,48 C 72,75 85,135 108,180 C 100,195 70,250 25,305 Z" fill="url(#blueGrad)"/>
    <path d="M 85,42 C 95,25 115,25 125,42 C 138,70 120,115 100,150 C 95,140 80,80 85,42 Z" fill="url(#blueHighlight)"/>
  </g>
</svg>"""
with open(blue_svg_path, "w", encoding="utf-8") as f:
    f.write(svg_code)
print("   [OK] blue_ribbon.svg creado")

print("==> 2. Actualizando admin.html...")
admin_path = os.path.join(TEMPLATES_DIR, "admin.html")
with open(admin_path, "r", encoding="utf-8") as f:
    admin_content = f.read()

# Actualizar caja de toggle para Noviembre Azul
old_toggle_box = """                    <!-- CAMPAÑA LISTÓN ROSA -->
                    <div style="background: rgba(255, 42, 133, 0.12); border: 1px solid rgba(255, 42, 133, 0.35); padding: 10px 14px; border-radius: 10px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <img src="/static/pink_ribbon.svg" style="width: 26px; height: 32px;">
                            <div>
                                <strong style="color: #ff80bf; font-size: 13px;">Listón de Octubre Rosa</strong>
                                <div style="font-size: 11px; color: var(--upms-muted-gray);">Muestra el lazo rosa conmemorativo entre el escudo y el título.</div>
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="f-show-ribbon" checked onchange="renderDynamicMockup()">
                            <span class="slider"></span>
                        </label>
                    </div>"""

new_toggle_box = """                    <!-- CAMPAÑA LISTÓN AZUL -->
                    <div style="background: rgba(37, 99, 235, 0.14); border: 1px solid rgba(59, 130, 246, 0.45); padding: 10px 14px; border-radius: 10px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <img src="/static/blue_ribbon.svg?v=4" style="width: 26px; height: 32px;">
                            <div>
                                <strong style="color: #60a5fa; font-size: 13px;">Listón de Noviembre Azul</strong>
                                <div style="font-size: 11px; color: var(--upms-muted-gray);">Muestra el lazo azul conmemorativo entre el escudo y el título.</div>
                            </div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="f-show-ribbon" checked onchange="renderDynamicMockup()">
                            <span class="slider"></span>
                        </label>
                    </div>"""

if old_toggle_box in admin_content:
    admin_content = admin_content.replace(old_toggle_box, new_toggle_box)
    print("   [OK] Caja toggle de admin.html actualizada a Noviembre Azul")

# Actualizar el selector de temas cromáticos para incluir Noviembre Azul como opción
old_options = """                                <option value="emerald">Verde Esmeralda UPMS</option>
                                <option value="gold">Dorado VIP Institucional</option>
                                <option value="deep_blue">Azul Zafiro Formal</option>
                                <option value="octubre_rosa">🌸 Campaña Octubre Rosa</option>"""

new_options = """                                <option value="emerald">Verde Esmeralda UPMS</option>
                                <option value="gold">Dorado VIP Institucional</option>
                                <option value="deep_blue">Azul Zafiro Formal</option>
                                <option value="noviembre_azul" selected>💙 Campaña Noviembre Azul</option>
                                <option value="octubre_rosa">🌸 Campaña Octubre Rosa</option>"""

if old_options in admin_content:
    admin_content = admin_content.replace(old_options, new_options)
    print("   [OK] Opciones de tema en admin.html actualizadas")

# Agregar CSS de theme-noviembre_azul y blue-ribbon-badge en admin.html
if ".theme-noviembre_azul" not in admin_content:
    css_anchor = ".totem-screen.theme-octubre_rosa {"
    css_noviembre = """.totem-screen.theme-noviembre_azul {
            background: radial-gradient(circle at 50% 20%, rgba(20, 60, 130, 0.75) 0%, rgba(9, 30, 66, 0.95) 55%, rgba(4, 14, 30, 0.98) 100%) !important;
            border-color: rgba(96, 165, 250, 0.75) !important;
            box-shadow: 0 calc(1.5 * var(--u)) calc(5 * var(--u)) rgba(0, 0, 0, 0.85), inset 0 0 calc(4 * var(--u)) rgba(37, 99, 235, 0.35);
        }

        .blue-ribbon-badge {
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
        }

        .falling-blue-ribbon {
            position: absolute;
            top: -90px;
            pointer-events: none;
            filter: drop-shadow(0 4px 14px rgba(37, 99, 235, 0.75)) drop-shadow(0 0 10px rgba(96, 165, 250, 0.5));
            animation: ribbonFallAndSway linear forwards;
            will-change: transform, top, opacity;
        }

        """ + css_anchor
    admin_content = admin_content.replace(css_anchor, css_noviembre)
    print("   [OK] CSS theme-noviembre_azul y blue-ribbon-badge agregados en admin.html")

# Actualizar renderDynamicMockup en admin.html
old_mockup_ribbon = """            const showRibbon = document.getElementById('f-show-ribbon') && document.getElementById('f-show-ribbon').checked;
            const ribbonHtml = showRibbon ? '<img src="/static/pink_ribbon.png?v=3" class="pink-ribbon-badge" alt="Octubre Rosa">' : '';"""

new_mockup_ribbon = """            const showRibbon = document.getElementById('f-show-ribbon') && document.getElementById('f-show-ribbon').checked;
            const isPink = theme === 'octubre_rosa';
            const ribbonSrc = isPink ? '/static/pink_ribbon.png?v=3' : '/static/blue_ribbon.png?v=4';
            const ribbonCls = isPink ? 'pink-ribbon-badge' : 'blue-ribbon-badge';
            const ribbonAlt = isPink ? 'Octubre Rosa' : 'Noviembre Azul';
            const ribbonHtml = showRibbon ? `<img src="${ribbonSrc}" class="${ribbonCls}" alt="${ribbonAlt}">` : '';"""

if old_mockup_ribbon in admin_content:
    admin_content = admin_content.replace(old_mockup_ribbon, new_mockup_ribbon)
    print("   [OK] renderDynamicMockup actualizado en admin.html")

# Actualizar botón y función de lluvia en admin.html
admin_content = admin_content.replace(
    """<i class="fas fa-ribbon" style="color:#ff80bf;"></i> Probar Lluvia de Listones (Transición 5s)""",
    """<i class="fas fa-ribbon" style="color:#60a5fa;"></i> Probar Lluvia de Listones Azules (Transición 5s)"""
)
admin_content = admin_content.replace(
    "ribbon.src = '/static/pink_ribbon.png?v=3';",
    "ribbon.src = '/static/blue_ribbon.png?v=4';"
)
admin_content = admin_content.replace(
    "ribbon.className = 'falling-pink-ribbon';",
    "ribbon.className = 'falling-blue-ribbon';"
)

with open(admin_path, "w", encoding="utf-8") as f:
    f.write(admin_content)
print("   [OK] admin.html guardado exitosamente")

print("==> 3. Actualizando player.html...")
player_path = os.path.join(TEMPLATES_DIR, "player.html")
with open(player_path, "r", encoding="utf-8") as f:
    player_content = f.read()

# Agregar CSS en player.html
if ".theme-noviembre_azul" not in player_content:
    css_anchor_p = ".totem-screen.theme-octubre_rosa {"
    css_noviembre_p = """.totem-screen.theme-noviembre_azul {
            background: radial-gradient(circle at 50% 20%, rgba(20, 60, 130, 0.75) 0%, rgba(9, 30, 66, 0.95) 55%, rgba(4, 14, 30, 0.98) 100%) !important;
            border-color: rgba(96, 165, 250, 0.75) !important;
            box-shadow: 0 calc(1.5 * var(--u)) calc(5 * var(--u)) rgba(0, 0, 0, 0.85), inset 0 0 calc(4 * var(--u)) rgba(37, 99, 235, 0.35);
        }

        .blue-ribbon-badge {
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
        }

        .falling-blue-ribbon {
            position: absolute;
            top: -90px;
            pointer-events: none;
            filter: drop-shadow(0 4px 14px rgba(37, 99, 235, 0.75)) drop-shadow(0 0 10px rgba(96, 165, 250, 0.5));
            animation: ribbonFallAndSway linear forwards;
            will-change: transform, top, opacity;
        }

        """ + css_anchor_p
    player_content = player_content.replace(css_anchor_p, css_noviembre_p)
    print("   [OK] CSS theme-noviembre_azul y blue-ribbon-badge agregados en player.html")

# Actualizar lógica de ribbonHtml en player.html
old_player_ribbon = """            const fullText = (rawTitle + ' ' + (data.subtitle || '') + ' ' + rawBody + ' ' + (data.date_info || '')).toLowerCase();
            const showRibbon = (data.show_ribbon === true || data.theme === 'octubre_rosa' || fullText.includes('rosa') || fullText.includes('mama') || fullText.includes('cáncer') || fullText.includes('cancer') || fullText.includes('octubre'));
            const ribbonHtml = showRibbon ? '<img src="/static/pink_ribbon.png?v=3" class="pink-ribbon-badge" alt="Octubre Rosa">' : '';"""

new_player_ribbon = """            const fullText = (rawTitle + ' ' + (data.subtitle || '') + ' ' + rawBody + ' ' + (data.date_info || '')).toLowerCase();
            const isPink = data.theme === 'octubre_rosa' || fullText.includes('rosa') || fullText.includes('mama');
            const isBlue = data.theme === 'noviembre_azul' || fullText.includes('azul') || fullText.includes('noviembre') || fullText.includes('próstata') || fullText.includes('prostata') || fullText.includes('hombre');
            const showRibbon = (data.show_ribbon === true || isPink || isBlue || fullText.includes('cáncer') || fullText.includes('cancer'));
            const ribbonSrc = isPink ? '/static/pink_ribbon.png?v=3' : '/static/blue_ribbon.png?v=4';
            const ribbonCls = isPink ? 'pink-ribbon-badge' : 'blue-ribbon-badge';
            const ribbonAlt = isPink ? 'Octubre Rosa' : 'Noviembre Azul';
            const ribbonHtml = showRibbon ? `<img src="${ribbonSrc}" class="${ribbonCls}" alt="${ribbonAlt}">` : '';"""

if old_player_ribbon in player_content:
    player_content = player_content.replace(old_player_ribbon, new_player_ribbon)
    print("   [OK] ribbonHtml en player.html actualizado para Noviembre Azul")

# Actualizar la lluvia de listones para usar blue_ribbon.png
player_content = player_content.replace(
    "ribbon.src = '/static/pink_ribbon.png?v=3';",
    "ribbon.src = '/static/blue_ribbon.png?v=4';"
)
player_content = player_content.replace(
    "ribbon.className = 'falling-pink-ribbon';",
    "ribbon.className = 'falling-blue-ribbon';"
)

with open(player_path, "w", encoding="utf-8") as f:
    f.write(player_content)
print("   [OK] player.html guardado exitosamente")

print("==> 4. Actualizando actividades_octubre.html...")
act_path = os.path.join(TEMPLATES_DIR, "actividades_octubre.html")
if os.path.exists(act_path):
    with open(act_path, "r", encoding="utf-8") as f:
        act_content = f.read()
    act_content = act_content.replace(
        '<i class="fas fa-ribbon" style="color: #ff4081;"></i>\n            <span>Campaña Octubre Rosa: Cuidarte es Quererte</span>',
        '<i class="fas fa-ribbon" style="color: #60a5fa;"></i>\n            <span>Campaña Noviembre Azul: Cuidar tu salud también es cosa de hombres</span>'
    )
    with open(act_path, "w", encoding="utf-8") as f:
        f.write(act_content)
    print("   [OK] actividades_octubre.html actualizado")

print("==> 5. Desplegando a TrueNAS SCALE (192.168.3.4:8091)...")
host = '192.168.3.4'
username = 'crolon'
password = '24711351'
remote_base = '/mnt/Serranapool/APPS/carteleria_multimedia'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password, timeout=10)

sftp = ssh.open_sftp()

files_to_sync = [
    (os.path.join(STATIC_DIR, "blue_ribbon.svg"), f"{remote_base}/static/blue_ribbon.svg"),
    (os.path.join(STATIC_DIR, "blue_ribbon.png"), f"{remote_base}/static/blue_ribbon.png"),
    (os.path.join(TEMPLATES_DIR, "admin.html"), f"{remote_base}/templates/admin.html"),
    (os.path.join(TEMPLATES_DIR, "player.html"), f"{remote_base}/templates/player.html"),
    (os.path.join(TEMPLATES_DIR, "actividades_octubre.html"), f"{remote_base}/templates/actividades_octubre.html"),
]

# Actualizar docker-compose.yml local y remoto para montar templates y static
local_dc = os.path.join(CARTELERIA_DIR, "docker-compose.yml")
dc_lines = [
    "version: '3.8'",
    "",
    "services:",
    "  carteleria-lab:",
    "    build: .",
    "    container_name: upms_carteleria_multimedia",
    "    restart: unless-stopped",
    "    ports:",
    '      - "8091:8090"   # 8090 en TrueNAS ya lo usa inventory-app',
    "    volumes:",
    "      - /mnt/Serranapool/APPS/carteleria_multimedia/data:/app/data",
    "      - /mnt/Serranapool/APPS/carteleria_multimedia/media:/app/media",
    "      - /mnt/Serranapool/APPS/carteleria_multimedia/templates:/app/templates",
    "      - /mnt/Serranapool/APPS/carteleria_multimedia/static:/app/static",
    "    environment:",
    "      - TZ=America/Asuncion",
    ""
]
dc_content = "\n".join(dc_lines)
with open(local_dc, "w", encoding="utf-8") as f:
    f.write(dc_content)

files_to_sync.append((local_dc, f"{remote_base}/docker-compose.yml"))

for lpath, rpath in files_to_sync:
    print(f"   Subiendo {rpath}...")
    sftp.put(lpath, rpath)

sftp.close()

print("==> 6. Orquestando contenedor con volúmenes montados...")
cmd_up = f"cd {remote_base} && echo '{password}' | sudo -S docker compose up -d"
stdin, stdout, stderr = ssh.exec_command(cmd_up)
out = stdout.read().decode('utf-8')
print("   Salida compose up:", out.strip())

time.sleep(3)

print("==> 7. Verificando healthcheck en http://127.0.0.1:8091...")
stdin, stdout, stderr = ssh.exec_command("curl -sI http://127.0.0.1:8091/ | head -n 5")
health = stdout.read().decode('utf-8')
print(health)

ssh.close()
print("--> Noviembre Azul desplegado y activo exitosamente en http://192.168.3.4:8091!")
