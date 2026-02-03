import unittest
from unittest.mock import patch
from io import StringIO
from your_module import LightSwitch  # Replace 'your_module' with the actual module name

class TestLightSwitch(unittest.TestCase):

    def test_init(self):
        light = LightSwitch()
        self.assertFalse(light.is_on)

    def test_turn_on(self):
        light = LightSwitch()
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            light.turn_on()
            self.assertTrue(light.is_on)
            self.assertEqual(fake_stdout.getvalue().strip(), "Light is on")

    def test_turn_on_already_on(self):
        light = LightSwitch()
        light.is_on = True
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            light.turn_on()
            self.assertTrue(light.is_on)
            self.assertEqual(fake_stdout.getvalue().strip(), "Light is already on")

    def test_turn_off(self):
        light = LightSwitch()
        light.is_on = True
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            light.turn_off()
            self.assertFalse(light.is_on)
            self.assertEqual(fake_stdout.getvalue().strip(), "Light is off")

    def test_turn_off_already_off(self):
        light = LightSwitch()
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            light.turn_off()
            self.assertFalse(light.is_on)
            self.assertEqual(fake_stdout.getvalue().strip(), "Light is already off")

if __name__ == "__main__":
    unittest.main()