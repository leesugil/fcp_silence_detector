import unittest
import numpy as np

from fcp_silence_detector import detect_silence

class TestDetect(unittest.TestCase):

    def test_cases(self):
        cases = [
                # ordinary
                (frame,
                 top,
                 left,
                 bottom,
                 right,
                 expected),
                ]

        for a, b, c, d, e, expected in cases:
            with self.subTest(a=a, b=b, c=c, d=d, e=e):
                self.assertEqual(detect_text.crop_frame(a, b, c, d, e), expected)

class TestParse(unittest.TestCase):

    def test_cases(self):
        cases = [
                # ordinary
                (frame,
                 top,
                 left,
                 bottom,
                 right,
                 expected),
                ]

        for a, b, c, d, e, expected in cases:
            with self.subTest(a=a, b=b, c=c, d=d, e=e):
                self.assertEqual(detect_text.crop_frame(a, b, c, d, e), expected)

class TestPolish(unittest.TestCase):

    def test_cases(self):
        cases = [
                # ordinary
                (frame,
                 top,
                 left,
                 bottom,
                 right,
                 expected),
                ]

        for a, b, c, d, e, expected in cases:
            with self.subTest(a=a, b=b, c=c, d=d, e=e):
                self.assertEqual(detect_text.crop_frame(a, b, c, d, e), expected)

class TestBuffer(unittest.TestCase):

    def test_cases(self):
        cases = [
                # ordinary
                (frame,
                 top,
                 left,
                 bottom,
                 right,
                 expected),
                ]

        for a, b, c, d, e, expected in cases:
            with self.subTest(a=a, b=b, c=c, d=d, e=e):
                self.assertEqual(detect_text.crop_frame(a, b, c, d, e), expected)

class TestDetectSilences(unittest.TestCase):

    def test_cases(self):
        cases = [
                # ordinary
                (frame,
                 top,
                 left,
                 bottom,
                 right,
                 expected),
                ]

        for a, b, c, d, e, expected in cases:
            with self.subTest(a=a, b=b, c=c, d=d, e=e):
                self.assertEqual(detect_text.crop_frame(a, b, c, d, e), expected)

if __name__ == '__main__':
    unittest.main()
