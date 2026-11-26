"""Offline analysis grouping; no camera, phone or server access."""
import importlib.util, unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('analysis',ROOT/'scripts/analyze-calibration-hdmi.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
class OnsetTests(unittest.TestCase):
    def test_no_bursts(self):self.assertEqual(A.onset_times(np.array([]),.4),[])
    def test_group_consecutive_red_frames(self):self.assertEqual(A.onset_times(np.array([1.5,1.533,1.566,3.5,3.533]),.4),[1.5,3.5])
    def test_group_audio_samples_not_individual_sine_peaks(self):self.assertEqual(A.onset_times(np.array([1.5,1.50002,1.501,3.5,3.501]),.05),[1.5,3.5])
if __name__=='__main__':unittest.main()
