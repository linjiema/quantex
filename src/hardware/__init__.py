"""
This file used to list all the hardware we use.
"""

# from src.hardware.XMT_E70D4.API import XMT
from src.hardware.XMT_E70D4.API_Ser import XMT
# from src.hardware.SynthUSB3 import SynthUSB3
from src.hardware.Swabian_Pulse_Streamer.API import PulseGenerator
from src.hardware.Swabian_TimeTagger20.API import TimeTagger20
from src.hardware.NI_PCIe_6321.API import TriggeredLocationSensor, TriggeredCounter, HardwareTimer, \
    OneTimeCounter_HardwareTimer


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
