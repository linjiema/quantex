"""
This file used to list all the hardware we use.
"""

# from Hardware.XMT_E70D4 import XMT
from Hardware.XMT_E70D4_Ser import XMT
# from Hardware.SynthUSB3 import SynthUSB3
from Hardware.OpalKelly.API import PulseGenerator
from Hardware.NI_PCIe_6321 import TriggeredLocationSensor
from Hardware.NI_PCIe_6321 import TriggeredCounter
from Hardware.NI_PCIe_6321 import HardwareTimer
from Hardware.NI_PCIe_6321 import OneTimeCounter_HardwareTimer


class AllHardware():
    def __init__(self):
        self.mover = XMT()
        # self.mw_source = SynthUSB3()
        self.pulser = PulseGenerator()
        self.triggered_location_sensor = TriggeredLocationSensor()
        self.triggered_counter = TriggeredCounter()
        self.timer = HardwareTimer()
        self.one_time_counter = OneTimeCounter_HardwareTimer()

    def cleanup(self):
        try:
            self.mover.close_devices()
            # self.mw_source.clean_up()
        except BaseException as e:
            print(e)
        else:
            return 0
