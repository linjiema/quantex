"""
This file used to list all the hardware we use.
"""
import src.utils.logger as logger
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
            logger.logger.warning(f"Warning: {e}")
            return e
        else:
            return 0


class device_manager():
    """

    """
    def __init__(self):
        self.mover = None
        self.mover_status = 0
        self.scanner = None
        self.scanner_status = 0
        self.pulser = None
        self.pulser_status = 0
        self.counter = None
        self.counter_status = 0
        self.triggered_location_sensor = None
        self.triggered_location_sensor_status = 0
        self.timer = None
        self.timer_status = 0
        self.one_time_counter = None
        self.one_time_counter_status = 0

    def init_all_device(self, pulser_serial='00-26-32-f0-92-26', counter_serial="2208000ZCM"):
        self.init_mover()
        self.init_scanner()
        self.init_pulser(serial=pulser_serial)
        self.init_counter(serial=counter_serial)
        self.init_triggered_location_sensor()
        self.init_timer()
        self.init_one_time_counter()

    def cleanup(self):
        self.reset_mover()
        self.reset_scanner()
        self.reset_pulser()
        self.reset_counter()
        self.reset_triggered_location_sensor()
        self.reset_timer()
        self.reset_one_time_counter()

    def init_mover(self):
        try:
            self.mover = XMT()
        except BaseException as e:
            logger.logger.warning(f"Warning: Mover init failed! {e}")
        else:
            self.mover_status = 1

    def reset_mover(self):
        if self.mover_status:
            try:
                self.mover.close_devices()
            except BaseException as e:
                logger.logger.warning(f"Warning: Mover reset failed! {e}")
            else:
                self.mover = None
                self.mover_status = 0

    def init_scanner(self):
        try:
            # self.scanner =
            pass
        except BaseException as e:
            logger.logger.warning(f"Warning: Scanner init failed! {e}")
        else:
            self.scanner_status = 1

    def reset_scanner(self):
        if self.scanner_status:
            try:
                # self.scanner =
                pass
            except BaseException as e:
                logger.logger.warning(f"Warning: Scanner reset failed! {e}")
            else:
                self.scanner = None
                self.scanner_status = 0

    def init_pulser(self, serial='00-26-32-f0-92-26'):
        try:
            self.pulser = PulseGenerator(serial=serial)
        except BaseException as e:
            logger.logger.warning(f"Warning: Pulser init failed! {e}")
        else:
            self.pulser_status = 1

    def reset_pulser(self):
        if self.pulser_status:
            try:
                self.pulser.reset_pulse_generator()
            except BaseException as e:
                logger.logger.warning(f"Warning: Pulser reset failed! {e}")
            else:
                self.pulser = None
                self.pulser_status = 0


    def init_counter(self, serial="2208000ZCM"):
        try:
            self.counter = TimeTagger20(serial=serial)
        except BaseException as e:
            logger.logger.warning(f"Warning: Counter init failed! {e}")
        else:
            self.counter_status = 1

    def reset_counter(self):
        if self.counter_status:
            try:
                self.counter.free_tt()
            except BaseException as e:
                logger.logger.warning(f"Warning: Counter reset failed! {e}")
            else:
                self.counter = None
                self.counter_status = 0

    def init_triggered_location_sensor(self):
        try:
            self.triggered_location_sensor = TriggeredLocationSensor()
        except BaseException as e:
            logger.logger.warning(f"Warning: Triggered location sensor init failed! {e}")
        else:
            self.triggered_location_sensor_status = 1

    def reset_triggered_location_sensor(self):
        if self.triggered_location_sensor_status:
            try:
                self.triggered_location_sensor.close()
            except BaseException as e:
                logger.logger.warning(f"Warning: Triggered location sensor reset failed! {e}")
            else:
                self.triggered_location_sensor = None
                self.triggered_location_sensor_status = 0

    def init_timer(self):
        try:
            self.timer = HardwareTimer()
        except BaseException as e:
            logger.logger.warning(f"Warning: Timer init failed! {e}")
        else:
            self.timer_status = 1

    def reset_timer(self):
        if self.timer_status:
            try:
                self.timer.close()
            except BaseException as e:
                logger.logger.warning(f"Warning: Timer reset failed! {e}")
            else:
                self.timer = None
                self.timer_status = 0

    def init_one_time_counter(self):
        try:
            self.one_time_counter = OneTimeCounter_HardwareTimer()
        except BaseException as e:
            logger.logger.warning(f"Warning: One time counter init failed! {e}")
        else:
            self.one_time_counter_status = 1

    def reset_one_time_counter(self):
        if self.one_time_counter_status:
            try:
                self.one_time_counter.close()
            except BaseException as e:
                logger.logger.warning(f"Warning: One time counter reset failed! {e}")
            else:
                self.one_time_counter = None
                self.one_time_counter_status = 0






