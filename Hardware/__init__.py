"""
This file used to list all the hardware we use.
"""

# from Hardware.XMT_E70D4.API import XMT
from Hardware.XMT_E70D4.API_Ser import XMT
# from Hardware.SynthUSB3 import SynthUSB3
from Hardware.Swabian_Pulse_Streamer.API import PulseGenerator
from Hardware.NI_PCIe_6321.API import TriggeredLocationSensor, TriggeredCounter, HardwareTimer, \
    OneTimeCounter_HardwareTimer, GScanner


class AllHardware():
    def __init__(self):
        self.mover = XMT()
        # self.mw_source = SynthUSB3()
        self.pulser = PulseGenerator(serial='00-26-32-f0-92-26')
        self.triggered_location_sensor = TriggeredLocationSensor()
        self.triggered_counter = TriggeredCounter()
        self.timer = HardwareTimer()
        self.one_time_counter = OneTimeCounter_HardwareTimer()

    def cleanup(self):
        try:
            self.mover.close_devices()
            self.pulser.reset_pulse_generator()
            # self.mw_source.clean_up()
        except BaseException as e:
            print(e)
        else:
            return 0
