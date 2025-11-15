import unittest
from resonanceX import detector
import pandas as pd

class TestDetector(unittest.TestCase):
    def test_detect_resonances(self):
        periods = [1.0, 2.0, 3.0, 4.5]
        result = detector.detect_resonances(periods)
        self.assertTrue(any(r[2] == 2 for r in result))