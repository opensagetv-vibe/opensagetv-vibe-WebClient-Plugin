#!/usr/bin/env python3
"""Render public release manifests without changing local-install manifests."""
from pathlib import Path
import hashlib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    version = (ROOT / 'VERSION').read_text().strip()
    source = ROOT / 'dist/local-install/SageTVPluginsDev.d'
    package = source / f'sagetv-webplayer-{version}.zip'
    digest = hashlib.md5(package.read_bytes()).hexdigest()
    public = ROOT / 'dist/public-release'
    public.mkdir(parents=True, exist_ok=True)
    for name in ('sagetv-webplayer.xml', 'sagetv-webplayer-windows.xml'):
        text = (source / name).read_text(encoding='utf-8')
        old = f'https://local.invalid/sagetv-webplayer-{version}.zip'
        assert text.count(old) == 1
        url = ('https://github.com/opensagetv-vibe/opensagetv-vibe-WebClient-Plugin/'
               f'releases/download/v{version}/{package.name}')
        text = text.replace(old, url)
        root = ET.fromstring(text)
        assert root.findtext('Version') == version
        assert root.findtext('Package/MD5') == digest
        assert root.findtext('Package/Location') == url
        (public / name).write_text(text, encoding='utf-8', newline='\n')
    assets = [ROOT / 'dist/SageTVWebPlayer.war', package,
              public / 'sagetv-webplayer.xml', public / 'sagetv-webplayer-windows.xml']
    (public / 'SHA256SUMS').write_text(''.join(
        hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n'
        for path in assets), encoding='ascii')
    print('PASS public manifests, package MD5 and release SHA256SUMS')


if __name__ == '__main__':
    main()
