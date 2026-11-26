"""Read-only current release metadata consistency; no publication or field PASS."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile

EXACT = '--exact-artifacts' in sys.argv
if EXACT:
    sys.argv.remove('--exact-artifacts')

ROOT = Path(__file__).resolve().parents[1]


class BuildInfoTests(unittest.TestCase):
    def setUp(self):
        self.info = json.loads((ROOT / 'BUILD_INFO.json').read_text(encoding='utf-8'))
        self.package = ROOT / 'dist/local-install/SageTVPluginsDev.d'

    def test_version_and_development_boundary(self):
        self.assertEqual(self.info['version'], (ROOT / 'VERSION').read_text().strip())
        self.assertEqual('2026-11-26', self.info['release_date'])
        self.assertIn('QUALIFIED-SCOPES-RELEASED', self.info['phase'])

    def test_clean_ci_has_verified_real_provider_dependency(self):
        workflow = (ROOT / '.github/workflows/repository-checks.yml').read_text()
        self.assertIn('releases/download/v0.1.36/SageTVFFmpegPlugin-jar-0.1.36.zip', workflow)
        self.assertIn('60d58439250eec189fd3002088a0f869389bd16a2b901cb3054f9286705a9274', workflow)
        self.assertIn('sha256sum --check --strict', workflow)
        self.assertIn('SAGETV_FFMPEG_PLUGIN_JAR: ${{ runner.temp }}', workflow)
        helper = (ROOT / 'scripts/prepare-process-control-tests.sh').read_text()
        self.assertIn('cd build/manual/test-classes', helper)
        self.assertNotIn('cd build/manual/classes', helper)

    def test_current_artifact_hashes(self):
        paths = {'war_sha256': ROOT / 'dist/SageTVWebPlayer.war',
                 'local_installer_sha256': self.package / ('sagetv-webplayer-' + self.info['version'] + '.zip'),
                 'plugin_xml_sha256': self.package / 'sagetv-webplayer.xml',
                 'plugin_xml_windows_sha256': self.package / 'sagetv-webplayer-windows.xml'}
        for key, path in paths.items():
            self.assertRegex(self.info[key], r'^[a-f0-9]{64}$')
            if EXACT:
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), self.info[key], key)
        package = paths['local_installer_sha256']
        md5 = hashlib.md5(package.read_bytes()).hexdigest()
        self.assertRegex(self.info['local_installer_md5'], r'^[a-f0-9]{32}$')
        if EXACT:
            self.assertEqual(md5, self.info['local_installer_md5'])
        # The committed hashes identify the commissioned build, not arbitrary
        # compiler output. CI's Java11 must validate its OWN embedded WAR/XML.
        with zipfile.ZipFile(package) as archive:
            self.assertEqual(archive.read('jetty/webapps/SageTVWebPlayer.war'), paths['war_sha256'].read_bytes())
        for name in ('sagetv-webplayer.xml', 'sagetv-webplayer-windows.xml'):
            self.assertEqual(ET.parse(self.package / name).findtext('Package/MD5'), md5)

    def test_epoch_and_manifest_version(self):
        values = dict(line.split('=', 1) for line in (ROOT / 'release.properties').read_text().splitlines() if '=' in line)
        self.assertEqual(int(values['SOURCE_DATE_EPOCH']), self.info['source_date_epoch'])
        for name in ('sagetv-webplayer.xml', 'sagetv-webplayer-windows.xml'):
            manifest = ET.parse(self.package / name)
            self.assertEqual(manifest.findtext('Version'), self.info['version'])
            provider = 'SageTVFFmpegPluginWinx64' if 'windows' in name else 'SageTVFFmpegPluginLinux'
            dependency = next(d for d in manifest.findall('Dependency') if d.findtext('Plugin') == provider)
            platform = 'WINDOWS' if 'windows' in name else 'LINUX'
            self.assertEqual(dependency.findtext('MinVersion'), values.get('FFMPEG_PLUGIN_'+platform+'_MIN_VERSION', values['FFMPEG_PLUGIN_VERSION']))
            self.assertEqual(dependency.findtext('MinVersion'), '0.1.35' if platform=='WINDOWS' else '0.1.32')


if __name__ == '__main__':
    unittest.main()
