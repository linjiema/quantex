"""
This file used to list all the hardware we use.
"""

from Hardware.XMT_E70D4 import XMT
from Hardware.NI_PCIe_6321 import TriggeredLocationSensor
from Hardware.NI_PCIe_6321 import TriggeredCounter
from Hardware.NI_PCIe_6321 import HardwareTimer

class AllHardware():
    def __init__(self):
        self.mover = XMT()
        self.triggered_location_sensor = TriggeredLocationSensor
        self.triggered_counter = TriggeredCounter
        self.timer = HardwareTimer

    def cleanup(self):
        pass