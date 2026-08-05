import random
import re
import unittest

from callsign_trainer.callsigns import callsign_to_phonetics, generate_callsign, normalize_callsign


class CallsignTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_callsign(" sp6 smr "), "SP6SMR")

    def test_phonetics(self):
        self.assertEqual(callsign_to_phonetics("SP6"), "Sierra Papa Six")

    def test_generator_shape_and_region(self):
        rng = random.Random(42)
        for _ in range(500):
            callsign, region = generate_callsign(rng)
            self.assertRegex(callsign, re.compile(r"^[A-Z0-9]+$"))
            self.assertTrue(any(char.isdigit() for char in callsign))
            self.assertTrue(region)


if __name__ == "__main__":
    unittest.main()

