#!/usr/bin/env python3
"""Focused local candidate-package checks; never contacts a server."""
import importlib.util
from pathlib import Path
import stat
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('shared',ROOT/'scripts/commission-shared-plugins.py')
shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)

class Staging(unittest.TestCase):
    def test_closed_component_names(self):
        with self.assertRaises(ValueError):shared.component('arbitrary-path-or-plugin')

    def test_real_candidates_are_verified_manager_inputs(self):
        for name,identifier,count in [('ffmpeg','SageTVFFmpegPluginLinux',3),
                                      ('client-extension','OpenSageTVVibeClientExtensionPlugin',1),
                                      ('core-mcp','OpenSageTVVibeCoreMCPPlugin',1),
                                      ('sagemc','opensagetv-vibe-sagemc',2)]:
            actual,version,node,files,digests=shared.component(name)
            self.assertEqual(actual,identifier)
            self.assertRegex(version,r'^\d+\.\d+\.\d+$')
            self.assertEqual(len(files),count)
            self.assertEqual(set(files),set(digests))
            for package in node.findall('Package'):
                self.assertTrue(package.findtext('Location').startswith('file:///opt/sagetv/server/SageTVPluginsDev.d/'))
            self.assertTrue(all(len(value)==64 for value in digests.values()))

    def test_nonordinary_remote_paths_are_refused(self):
        class Remote:
            def lstat(self,path):
                return type('Entry',(),{'st_mode':stat.S_IFLNK|0o777})()
        with self.assertRaises(ValueError):shared.regular(Remote(),'/staging',directory=True)
        with self.assertRaises(ValueError):shared.regular(Remote(),'/staging.zip')

    def test_missing_is_explicit_not_silently_ordinary(self):
        class Remote:
            def lstat(self,path):raise FileNotFoundError(path)
        self.assertFalse(shared.regular(Remote(),'/missing',missing=True))
        with self.assertRaises(FileNotFoundError):shared.regular(Remote(),'/missing')

if __name__=='__main__':unittest.main()
