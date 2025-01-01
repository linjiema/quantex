"""
This file used to list all the hardware we use.
"""
import src.utils.logger as logger
from PyQt5 import QtCore
# from src.hardware.XMT_E70D4.API import XMT
from src.hardware.XMT_E70D4.API_Ser import XMT
# from src.hardware.SynthUSB3 import SynthUSB3
from src.hardware.Swabian_Pulse_Streamer.API import PulseGenerator
from src.hardware.Swabian_TimeTagger20.API import TimeTagger20
from src.hardware.SynthNVPro.API import SynthNVPro
from src.hardware.EM_CV5_1.API import RotationStage
from src.hardware.NI_PCIe_6321.API import GScanner, TriggeredLocationSensor, TriggeredCounter, HardwareTimer, \
    OneTimeCounter_HardwareTimer, GatedCounter, SampleTriggerOutput, counter_for_rotation

'''
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
'''


class DeviceManager(QtCore.QObject):
    SIGNAL_DeviceStatusUpdate = QtCore.pyqtSignal(str, bool, name='DeviceStatusUpdate')
    """

    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mover = None
        self.mover_status = 0
        self.scanner = None
        self.scanner_status = 0
        self.pulser = None
        self.pulser_status = 0
        self.counter = None
        self.counter_status = 0
        self.mw_source = None
        self.mw_source_status = 0
        self.rotator = None
        self.rotator_status = 0
        self.triggered_counter = None
        self.triggered_counter_status = 0
        self.triggered_location_sensor = None
        self.triggered_location_sensor_status = 0
        self.timer = None
        self.timer_status = 0
        self.one_time_counter = None
        self.one_time_counter_status = 0
        self.gate_counter = None
        self.gate_counter_status = 0
        self.sample_trigger = None
        self.sample_trigger_status = 0
        self.counter_rotation = None
        self.counter_rotation_status = 0

    def init_all_device(self, pulser_serial='00-26-32-f0-92-26', counter_serial="2208000ZCM"):
        self.init_mover()
        self.init_scanner()
        self.init_pulser(serial=pulser_serial)
        self.init_counter(serial=counter_serial)
        self.init_mw_source()
        self.init_rotator()
        self.init_ni()

        '''
        print(self.mover_status, self.scanner_status, self.pulser_status, self.counter_status, self.triggered_counter_status,
              self.triggered_location_sensor_status, self.timer_status, self.one_time_counter_status)
        print('Mover:', self.mover, '\n',
              'scanner:', self.scanner, '\n',
              'pulser:', self.pulser, '\n',
              'counter:', self.counter, '\n',
              'triggered_counter:', self.triggered_counter, '\n',
              'triggered_location_sensor:', self.triggered_location_sensor, '\n',
              'timer:', self.timer, '\n',
              'one_time_counter:', self.one_time_counter)
        '''

    def cleanup(self):
        self.reset_mover()
        self.reset_scanner()
        self.reset_pulser()
        self.reset_counter()
        self.reset_mw_source()
        self.reset_rotator()
        self.reset_ni()

    # function for all individual device

    def init_mover(self):
        if not self.mover_status:
            try:
                self.mover = XMT()
                if self.mover.scan_devices() == 0:
                    self.mover.open_devices()
                else:
                    raise ValueError('Piezo stage hasn\'t been connected!')
            except BaseException as e:
                self.mover = None
                logger.logger.info(f"Mover init failed! {e}")
            else:
                self.mover_status = 1
                self.DeviceStatusUpdate.emit('mover', self.mover_status)

    def reset_mover(self):
        if self.mover_status:
            try:
                self.mover.close_devices()
            except BaseException as e:
                logger.logger.info(f"Mover reset failed! {e}")
            else:
                self.mover = None
                self.mover_status = 0
                self.DeviceStatusUpdate.emit('mover', self.mover_status)

    def init_scanner(self):
        if not self.scanner_status:
            try:
                self.scanner = GScanner()
            except BaseException as e:
                logger.logger.info(f"Scanner init failed! {e}")
            else:
                self.scanner_status = 1
                self.DeviceStatusUpdate.emit('scanner', self.scanner_status)

    def reset_scanner(self):
        if self.scanner_status:
            try:
                self.scanner.close()
            except BaseException as e:
                logger.logger.info(f"Scanner reset failed! {e}")
            else:
                self.scanner = None
                self.scanner_status = 0
                self.DeviceStatusUpdate.emit('scanner', self.scanner_status)

    def init_pulser(self, serial='00-26-32-f0-92-26'):
        if not self.pulser_status:
            try:
                self.pulser = PulseGenerator(serial=serial)
            except BaseException as e:
                logger.logger.warning(f"Pulser init failed! {e}")
            else:
                self.pulser_status = 1
                self.DeviceStatusUpdate.emit('pulser', self.pulser_status)

    def reset_pulser(self):
        if self.pulser_status:
            try:
                self.pulser.reset_pulse_generator()
            except BaseException as e:
                logger.logger.warning(f"Pulser reset failed! {e}")
            else:
                self.pulser = None
                self.pulser_status = 0
                self.DeviceStatusUpdate.emit('pulser', self.pulser_status)

    def init_counter(self, serial="2208000ZCM"):
        if not self.counter_status:
            try:
                self.counter = TimeTagger20(serial=serial)
            except BaseException as e:
                logger.logger.info(f"Counter init failed! {e}")
            else:
                self.counter_status = 1
                self.DeviceStatusUpdate.emit('counter', self.counter_status)

    def reset_counter(self):
        if self.counter_status:
            try:
                self.counter.free_tt()
            except BaseException as e:
                logger.logger.info(f"Counter reset failed! {e}")
            else:
                self.counter = None
                self.counter_status = 0
                self.DeviceStatusUpdate.emit('counter', self.counter_status)

    def init_mw_source(self):
        if not self.mw_source_status:
            try:
                self.mw_source = SynthNVPro()
                self.mw_source.init_port()
            except BaseException as e:
                logger.logger.info(f"MW_source init failed! {e}")
            else:
                self.mw_source_status = 1
                self.DeviceStatusUpdate.emit('MW', self.mw_source_status)

    def reset_mw_source(self):
        if self.mw_source_status:
            try:
                self.mw_source.switch(state=False)
                self.mw_source.clean_up()
            except BaseException as e:
                logger.logger.info(f"MW_source reset failed! {e}")
            else:
                self.mw_source = None
                self.mw_source_status = 0
                self.DeviceStatusUpdate.emit('MW', self.mw_source_status)

    def init_rotator(self):
        if not self.rotator_status:
            try:
                self.rotator = RotationStage()
                status = self.rotator.open()
                if status == -1:
                    self.rotator = None
                    raise ValueError('Rotator hasn\'t been connected!')
            except BaseException as e:
                logger.logger.info(f"Rotator init failed! {e}")
            else:
                self.rotator_status = 1
                self.DeviceStatusUpdate.emit('rotator', self.rotator_status)

    def reset_rotator(self):
        if self.rotator_status:
            try:
                self.rotator.close()
            except BaseException as e:
                logger.logger.info(f"Rotator reset failed! {e}")
            else:
                self.rotator = None
                self.rotator_status = 0
                self.DeviceStatusUpdate.emit('rotator', self.rotator_status)

    def init_triggered_counter(self):
        if not self.triggered_counter_status:
            try:
                self.triggered_counter = TriggeredCounter()
            except BaseException as e:
                logger.logger.info(f"Triggered_Counter init failed! {e}")
            else:
                self.triggered_counter_status = 1

    def reset_triggered_counter(self):
        if self.triggered_counter_status:
            try:
                self.triggered_counter.close()
            except BaseException as e:
                logger.logger.info(f"Triggered_Counter reset failed! {e}")
            else:
                self.triggered_counter = None
                self.triggered_counter_status = 0

    def init_triggered_location_sensor(self):
        if not self.triggered_location_sensor_status:
            try:
                self.triggered_location_sensor = TriggeredLocationSensor()
            except BaseException as e:
                logger.logger.info(f"Triggered location sensor init failed! {e}")
            else:
                self.triggered_location_sensor_status = 1

    def reset_triggered_location_sensor(self):
        if self.triggered_location_sensor_status:
            try:
                self.triggered_location_sensor.close()
            except BaseException as e:
                logger.logger.info(f"Triggered location sensor reset failed! {e}")
            else:
                self.triggered_location_sensor = None
                self.triggered_location_sensor_status = 0

    def init_timer(self):
        if not self.timer_status:
            try:
                self.timer = HardwareTimer()
            except BaseException as e:
                logger.logger.info(f"Timer init failed! {e}")
            else:
                self.timer_status = 1

    def reset_timer(self):
        if self.timer_status:
            try:
                self.timer.close()
            except BaseException as e:
                logger.logger.info(f"Timer reset failed! {e}")
            else:
                self.timer = None
                self.timer_status = 0

    def init_one_time_counter(self):
        if not self.one_time_counter_status:
            try:
                self.one_time_counter = OneTimeCounter_HardwareTimer()
            except BaseException as e:
                logger.logger.info(f"One time counter init failed! {e}")
            else:
                self.one_time_counter_status = 1

    def reset_one_time_counter(self):
        if self.one_time_counter_status:
            try:
                self.one_time_counter.close()
            except BaseException as e:
                logger.logger.info(f"One time counter reset failed! {e}")
            else:
                self.one_time_counter = None
                self.one_time_counter_status = 0

    def init_gate_counter(self):
        if not self.gate_counter_status:
            try:
                self.gate_counter = GatedCounter()
            except BaseException as e:
                logger.logger.info(f"Gate counter init failed! {e}")
            else:
                self.gate_counter_status = 1

    def reset_gate_counter(self):
        if self.gate_counter_status:
            try:
                self.gate_counter.close()
            except BaseException as e:
                logger.logger.info(f"Gated counter reset failed! {e}")
            else:
                self.gate_counter = None
                self.gate_counter_status = 0

    def init_sample_trigger(self):
        if not self.sample_trigger_status:
            try:
                self.sample_trigger = SampleTriggerOutput()
            except BaseException as e:
                logger.logger.info(f"Sample Trigger Output init failed! {e}")
            else:
                self.sample_trigger_status = 1

    def reset_sample_trigger(self):
        if self.sample_trigger_status:
            try:
                self.sample_trigger.close()
            except BaseException as e:
                logger.logger.info(f"Sample Trigger Output reset failed! {e}")
            else:
                self.sample_trigger = None
                self.sample_trigger_status = 0

    def init_counter_rotation(self):
        if not self.counter_rotation_status:
            try:
                self.counter_rotation = counter_for_rotation()
            except BaseException as e:
                logger.logger.info(f"Counter for rotation init failed! {e}")
            else:
                self.counter_rotation_status = 1

    def reset_counter_rotation(self):
        if self.counter_rotation_status:
            try:
                self.counter_rotation.close()
            except BaseException as e:
                logger.logger.info(f"Counter for rotation reset failed! {e}")
            else:
                self.counter_rotation = None
                self.counter_rotation_status = 0

    def init_ni(self):
        self.init_triggered_counter()
        self.init_triggered_location_sensor()
        self.init_timer()
        self.init_one_time_counter()
        self.init_gate_counter()
        self.init_sample_trigger()
        self.init_counter_rotation()

        if self.triggered_counter_status and self.triggered_location_sensor_status and \
                self.timer_status and self.one_time_counter_status and self.gate_counter_status and \
                self.sample_trigger_status and self.counter_rotation_status:
            self.DeviceStatusUpdate.emit('NIDAQ', True)

    def reset_ni(self):
        self.reset_triggered_counter()
        self.reset_triggered_location_sensor()
        self.reset_timer()
        self.reset_one_time_counter()
        self.reset_gate_counter()
        self.reset_sample_trigger()
        self.reset_counter_rotation()
        if not self.triggered_counter_status and not self.triggered_location_sensor_status and \
                not self.timer_status and not self.one_time_counter_status and not self.gate_counter_status and \
                not self.sample_trigger_status and not self.counter_rotation_status:
            self.DeviceStatusUpdate.emit('NIDAQ', False)

