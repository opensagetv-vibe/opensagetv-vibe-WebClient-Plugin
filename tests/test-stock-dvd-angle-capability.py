#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('capability', Path(__file__).resolve().parents[1] / 'scripts/verify-stock-dvd-angle.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
MARKER = 'public synchronized boolean playControlEx(int, long, long, sage.dvd.pci_t);'
BODY = MARKER + '''
 Code:
  12: lookupswitch { // 2
    213: 510
    default: 1291
  }
  510: goto 1291
  1291: iconst_0
  1292: ireturn
 public synchronized int getDVDAngle();
 Code:
  510: iconst_1
'''


class CapabilityTest(unittest.TestCase):
    def test_exact_noop(self):
        self.assertTrue(C.angle_path(BODY)['angleIsNoOpReturningFalse'])

    def test_different_dispatch_not_called_noop(self):
        self.assertFalse(C.angle_path(BODY.replace('510: goto 1291', '510: invokevirtual #32'))['angleIsNoOpReturningFalse'])

    def test_true_return_not_called_noop(self):
        self.assertFalse(C.angle_path(BODY.replace('1291: iconst_0', '1291: iconst_1'))['angleIsNoOpReturningFalse'])

    def test_unknown_method_rejected(self):
        with self.assertRaises(ValueError):
            C.angle_path(BODY.replace(MARKER, 'different method'))

    def test_missing_angle_rejected(self):
        with self.assertRaises(ValueError):
            C.angle_path(BODY.replace('213: 510', '214: 510'))


if __name__ == '__main__':
    unittest.main()
