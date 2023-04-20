"""
This file used to list all the hardware we use.
"""

from Hardware.XMT_E70D4_Ser import XMT
from Hardware.Swabian_Pulse_Streamer.API import PulseGenerator
from Hardware.Swabian_TimeTagger20.API import TimeTagger20
from Hardware.NI_PCIe_6321 import TriggeredLocationSensor
from Hardware.NI_PCIe_6321 import HardwareTimer


class AllHardware():
    def __init__(self):
        self.mover = XMT()
        # self.mw_source = SynthUSB3()
        self.pulser = PulseGenerator(serial='00-26-32-f0-92-26')
        self.counter = TimeTagger20(serial="2208000ZCM")
        self.triggered_location_sensor = TriggeredLocationSensor()
        self.triggered_counter = TriggeredCounter()
        self.timer = HardwareTimer()
        self.one_time_counter = OneTimeCounter_HardwareTimer()

    def cleanup(self):
        try:
            self.mover.close_devices()
            self.pulser.reset_pulse_generator()
            self.counter.free_tt()
            # self.mw_source.clean_up()
        except BaseException as e:
            print(e)
        else:
            return 0
