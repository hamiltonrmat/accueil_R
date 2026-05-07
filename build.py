"""
build.py — v2 (plus permissif pour plateformes interactives)

Variables d'environnement attendues :
  - PLATFORM_URL     : URL complète de la plateforme d'examen
  - QUIT_PASSWORD    : mot de passe de sortie de SEB
  - ADMIN_PASSWORD   : mot de passe admin SEB
"""
import os
import sys
import hashlib
from pathlib import Path
from urllib.parse import urlparse


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"✗ Variable d'environnement manquante : {name}")
    return value


def main() -> None:
    platform_url   = require_env("PLATFORM_URL").rstrip("/") + "/"
    quit_password  = require_env("QUIT_PASSWORD")
    admin_password = require_env("ADMIN_PASSWORD")

    domain = urlparse(platform_url).netloc
    if not domain:
        sys.exit(f"✗ URL invalide : {platform_url}")

    quit_hash  = sha256_hex(quit_password)
    admin_hash = sha256_hex(admin_password)

    seb_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>startURL</key>
    <string>{platform_url}</string>

    <key>hashedQuitPassword</key>
    <string>{quit_hash}</string>
    <key>hashedAdminPassword</key>
    <string>{admin_hash}</string>

    <key>sebConfigPurpose</key><integer>0</integer>

    <!-- Sortie de SEB -->
    <key>allowQuit</key><true/>
    <key>ignoreExitKeys</key><true/>
    <key>allowPreferencesWindow</key><false/>

    <!-- Plein écran -->
    <key>browserViewMode</key><integer>1</integer>
    <key>mainBrowserWindowWidth</key><string>100%</string>
    <key>mainBrowserWindowHeight</key><string>100%</string>

    <!-- Blocage captures (essentiel) -->
    <key>allowScreenCapture</key><false/>
    <key>allowWindowCapture</key><false/>
    <key>blockScreenShotsLegacy</key><true/>
    <key>allowScreenSharing</key><false/>
    <key>allowSiri</key><false/>
    <key>allowDictation</key><false/>
    <key>allowAirPlayMirroring</key><false/>

    <!-- Navigation : on garde l'essentiel mais on relâche les pop-ups -->
    <key>browserWindowAllowAddressBar</key><false/>
    <key>browserWindowAllowReload</key><true/>
    <key>showReloadButton</key><false/>
    <key>showMenuBar</key><false/>
    <key>browserWindowShowURL</key><integer>0</integer>

    <!-- JavaScript ESSENTIEL pour plateformes interactives -->
    <key>enableJavaScript</key><true/>
    <key>enableJava</key><false/>
    <key>enablePlugIns</key><true/>
    <key>blockPopUpWindows</key><false/>
    <key>newBrowserWindowByLinkPolicy</key><integer>2</integer>
    <key>newBrowserWindowByScriptPolicy</key><integer>2</integer>

    <!-- Clic droit autorisé (sinon certains menus contextuels cassent) -->
    <key>enableRightMouse</key><true/>

    <!-- Filtre URL : seul le domaine d'examen autorisé -->
    <key>URLFilterEnable</key><true/>
    <key>URLFilterEnableContentFilter</key><false/>
    <key>URLFilterRules</key>
    <array>
        <dict>
            <key>active</key><true/>
            <key>action</key><integer>1</integer>
            <key>expression</key><string>*{domain}*</string>
            <key>regex</key><false/>
        </dict>
    </array>

    <!-- Téléchargements/téléversements autorisés -->
    <key>allowDownloads</key><true/>
    <key>allowUploads</key><true/>
    <key>downloadAndOpenSebConfig</key><false/>

    <!-- IMPORTANT : AAC désactivé (mode kiosque classique de SEB).
         AAC est trop strict et casse de nombreuses apps web interactives. -->
    <key>enableMacOSAAC</key><false/>
</dict>
</plist>
"""

    output_dir = Path("exams")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "learnr.seb"
    output_path.write_text(seb_xml, encoding="utf-8")

    print("══════════════════════════════════════════════════════════════")
    print("  GÉNÉRATION DU FICHIER .SEB (v2 — permissif)")
    print("══════════════════════════════════════════════════════════════")
    print(f"  ✓ Fichier         : {output_path}")
    print(f"  ✓ Taille          : {output_path.stat().st_size} octets")
    print(f"  ✓ URL plateforme  : {platform_url}")
    print(f"  ✓ Filtre URL      : *{domain}*")
    print(f"  ✓ AAC             : désactivé (compatibilité)")
    print(f"  ✓ JavaScript      : activé")
    print(f"  ✓ Pop-ups         : autorisés")
    print("══════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
