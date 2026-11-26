"""Offline guard for optional real-server field-test dependencies and trust."""
import re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class FieldSshContract(unittest.TestCase):
 def test_linux_dependencies_have_exact_versions_and_hashes(self):
  lines=[line for line in (ROOT/'requirements-field-ssh.txt').read_text().splitlines() if line and not line.startswith('#')]
  self.assertEqual(len(lines),7)
  for line in lines:self.assertRegex(line,r'^[a-z]+==[0-9.]+ --hash=sha256:[a-f0-9]{64}$')
  self.assertTrue(any(line.startswith('paramiko==5.0.0 ') for line in lines))
 def test_online_and_offline_install_preserve_verification(self):
  source=(ROOT/'scripts/setup-field-ssh.sh').read_text()
  self.assertEqual(source.count('pip install --require-hashes'),2)
  self.assertIn('--no-index --find-links',source)
  self.assertNotIn('--trusted-host',source);self.assertNotIn('PIP_TRUSTED_HOST',source)
  self.assertIn('/opt/opensagetv-vibe/web-python/bin/python3',source)
 def test_shared_local_trust_is_optional_private_and_rejects_unknown_peers(self):
  source=(ROOT/'scripts/commission-mobile.py').read_text()
  self.assertIn("ROOT/'config/ssh_known_hosts.local'",source)
  self.assertIn('shared_known.is_symlink()',source)
  self.assertIn('set_missing_host_key_policy(paramiko.RejectPolicy())',source)
  self.assertNotIn('AutoAddPolicy',source)
  self.assertIn('/config/ssh_known_hosts.local',(ROOT/'.gitignore').read_text().splitlines())
if __name__=='__main__':unittest.main()
