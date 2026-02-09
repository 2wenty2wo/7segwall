"""Root conftest — patches RPi.GPIO before any project module is imported."""

import sys
from unittest.mock import MagicMock

# Inject a fake RPi.GPIO module so hardware.py and app.py can be imported
# without a real Raspberry Pi.
gpio_mock = MagicMock()
gpio_mock.BCM = 11
gpio_mock.OUT = 0
gpio_mock.HIGH = 1
gpio_mock.LOW = 0
sys.modules["RPi"] = MagicMock()
sys.modules["RPi.GPIO"] = gpio_mock
