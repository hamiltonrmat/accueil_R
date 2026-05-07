"""
build.py — Génère exams/learnr.seb à partir des variables d'environnement Render.

Variables attendues (à définir dans Render → Environment) :
  - PLATFORM_URL     : URL complète de la plateforme d'examen
  - QUIT_PASSWORD    : mot de passe de sortie de SEB (en clair, sera hashé)
  - ADMIN_PASSWORD   : mot de passe admin SEB (en clair, sera hashé)

Exécuté automatiquement par Render avant chaque déploiement.
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

    <key>allowQuit</key><true/>
    <key>ignoreExitKeys</key><true/>
    <key>allowPreferencesWindow</key><false/>

    <key>browserViewMode</key><integer>1</integer>
    <key>mainBrowserWindowWidth</key><string>100%</string>
    <key>mainBrowserWindowHeight</key><string>100%</string>
    <key>mainBrowserWindowPositioning</key><integer>1</integer>

    <key>allowScreenCapture</key><false/>
    <key>allowWindowCapture</key><false/>
    <key>blockScreenShotsLegacy</key><true/>
    <key>allowScreenSharing</key><false/>
    <key>allowSiri</key><false/>
    <key>allowDictation</key><false/>
    <key>allowAirPlayMirroring</key><false/>

    <key>enableRightMouse</key><false/>
    <key>browserWindowAllowAddressBar</key><false/>
    <key>browserWindowAllowReload</key><false/>
    <key>showReloadButton</key><false/>
    <key>showMenuBar</key><false/>
    <key>browserWindowShowURL</key><integer>0</integer>
    <key>enableJavaScript</key><true/>
    <key>enableJava</key><false/>
    <key>enablePlugIns</key><false/>
    <key>blockPopUpWindows</key><true/>
    <key>clipboardPolicy</key><integer>0</integer>

    <key>URLFilterEnable</key><true/>
    <key>URLFilterEnableContentFilter</key><true/>
    <key>URLFilterRules</key>
    <array>
        <dict>
            <key>active</key><true/>
            <key>action</key><integer>1</integer>
            <key>expression</key><string>*{domain}*</string>
            <key>regex</key><false/>
        </dict>
    </array>

    <key>allowDownloads</key><false/>
    <key>allowUploads</key><false/>
    <key>downloadAndOpenSebConfig</key><false/>

    <key>enableMacOSAAC</key><true/>
</dict>
</plist>
"""

    output_dir = Path("exams")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "learnr.seb"
    output_path.write_text(seb_xml, encoding="utf-8")

    # Affichage diagnostique (sans révéler les mots de passe en clair)
    print("══════════════════════════════════════════════════════════════")
    print("  GÉNÉRATION DU FICHIER .SEB")
    print("══════════════════════════════════════════════════════════════")
    print(f"  ✓ Fichier         : {output_path}")
    print(f"  ✓ Taille          : {output_path.stat().st_size} octets")
    print(f"  ✓ URL plateforme  : {platform_url}")
    print(f"  ✓ Filtre URL      : *{domain}*")
    print(f"  ✓ Hash quit       : {quit_hash[:16]}…")
    print(f"  ✓ Hash admin      : {admin_hash[:16]}…")
    print("══════════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
