from PyQt5 import QtCore
import numpy as np
import time
import sys


class RotationMonitorThread(QtCore.QThread):
    """
    Return the absolute position of the rotation stage
    emit signal: angle
    """

    SIGNAL_angle = QtCore.pyqtSignal(float, name='angle')

    def __init__(self, hardware=None, parent=None):
        self._hardware = hardware
        self.continuous_state = False
        super().__init__(parent)

    def run(self):
        time.sleep(0.2)
        while self.continuous_state or self._hardware.rotator.is_running():
            angle = self._hardware.rotator.read_position()
            self.angle.emit(angle)
            time.sleep(0.2)
        else:
            angle = self._hardware.rotator.read_position()
            self.angle.emit(angle)
