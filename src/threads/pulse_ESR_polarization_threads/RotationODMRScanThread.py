"""

"""

from PyQt5 import QtCore
import time
from nidaqmx.errors import *
from src.threads.pulse_ESR_polarization_threads.RotationMonitorThread import RotationMonitorThread
import numpy as np
import random


class RotationODMRScanThread(QtCore.QThread):
    """
    This Thread is used to do the Rotation experiment.
    """

    # Signal for passing the data to main thread ([counts_reference, counts_signal, time])
    SIGNAL_update = QtCore.pyqtSignal(np.ndarray, np.ndarray, np.ndarray, name='update')

    def __init__(self, hardware=None, rmThread=None, parent=None):
        super().__init__(parent)
        # Get hardware from Main Thread
        self.running_status = None
        self._hardware = hardware
        self._rmThread = rmThread

    def run(self):
        # Define the running status
        self.running_status = True
        try:
            self._hardware.rotator.set_ttl_output(0)
            # prepare all related hardware
            self._hardware.pulser.load_rotation_gate_seq()
            self._hardware.rotator.move_abs()
            self._hardware.counter_rotation.init_task()
            # anti-clockwise rotation for 1 block (because we need to drop the first data)
            self._hardware.rotator.wait_until_finish()
            self._hardware.rotator.move_relative(angle=3, direction='AC')
            # start counter and the pulser
            self._hardware.pulser.start_output()
            self._hardware.counter_rotation.start_task()
            # set TTL output enable and start rotation
            self._hardware.rotator.wait_until_finish()
            self._hardware.rotator.set_ttl_output(1)
            self._hardware.rotator.move_jog(num=121, step=3, delay=0, direction='C')
            self._rmThread.continuous_state = True
            self._rmThread.start()
            self._hardware.rotator.wait_until_finish()
            # collect data
            _cts_ref, _cts_sig, _time = self._hardware.counter_rotation.get_counts_and_time()
        except BaseException as e:
            self._hardware.counter_rotation.close()
            self._hardware.pulser.laser_off()
            self._rmThread.continuous_state = False
            print(e)
            return
        else:
            # emit data to main thread
            self.update.emit(_cts_ref, _cts_sig, _time)
            self._hardware.pulser.laser_off()
            self._rmThread.continuous_state = False
