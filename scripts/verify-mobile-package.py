#!/usr/bin/env python3
"""Read-only affected UI package proof; not live-server/media certification."""
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
war = (ROOT / 'dist/SageTVWebPlayer.war').read_bytes()
package_dir = ROOT / 'dist/local-install/SageTVPluginsDev.d'
package = (package_dir / ('sagetv-webplayer-' + version + '.zip')).read_bytes()
with zipfile.ZipFile(io.BytesIO(package)) as archive:
    assert archive.read('jetty/webapps/SageTVWebPlayer.war') == war, 'Packaged WAR differs'
with zipfile.ZipFile(io.BytesIO(war)) as archive:
    checked = 0
    for source in (ROOT / 'src/main/webapp').rglob('*'):
        if source.is_file():
            name = source.relative_to(ROOT / 'src/main/webapp').as_posix()
            assert archive.read(name) == source.read_bytes(), 'Stale asset: ' + name
            checked += 1
    classes = [name for name in archive.namelist() if name.endswith('.class')]
    assert classes
    assert not any(name.startswith('WEB-INF/classes/sage/') for name in classes), 'Stock Core classes must not be shadowed'
    assert not any(name.startswith('WEB-INF/classes/org/opensagetv/vibe/ffmpeg/') for name in classes), 'Dependency implementation must not be duplicated in Web WAR'
    assert not any(name.startswith('WEB-INF/classes/org/opensagetv/vibe/clientextension/') for name in classes), 'Optional companion must remain a separate plugin'
    assert not any(name.lower().endswith(('/sage.jar', '.so', '.dll', '.exe')) for name in archive.namelist()), 'Core/native dependencies must not be seeded by the Web WAR'
    for name in classes:
        data = archive.read(name)
        assert data[:4] == b'\xca\xfe\xba\xbe' and int.from_bytes(data[6:8], 'big') == 52, name
for name in ('sagetv-webplayer.xml', 'sagetv-webplayer-windows.xml'):
    manifest = ET.parse(package_dir / name).getroot()
    assert manifest.findtext('Version') == version
    assert manifest.findtext('Package/MD5') == hashlib.md5(package).hexdigest()
print(json.dumps({'passed': True, 'webAssetsByteVerified': checked,
    'java8ClassesVerified': len(classes), 'packagedWarMatches': True,
    'warSha256': hashlib.sha256(war).hexdigest(),
    'packageSha256': hashlib.sha256(package).hexdigest()}, indent=2))
