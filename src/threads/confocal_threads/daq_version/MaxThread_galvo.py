"""
This Thread is used to find the point has the max value of counts
"""
from PyQt5 import QtCore
import sys
import numpy as np


class MaxThread_galvo(QtCore.QThread):
    """
    Maximizing module as a thread, based on PyQt5.QtCore.QThread
    parameters:
    @hardware: python object of hardware control
    """

    SIGNAL_counts = QtCore.pyqtSignal(int, name='counts')
    SIGNAL_moved = QtCore.pyqtSignal(float, float, float, name='moved')

    def __init__(self, hardware=None, parent=None):
        super().__init__(parent)
        self._hardware = hardware
        self.count_freq = 10  # Hz
        self.step = 0.1  # Micron

    def run(self):
        self._hardware.one_time_counter.count_freq = self.count_freq
        self._hardware.one_time_counter.init_task()

        self.scan(_channel=1)
        self.scan(_channel=2)
        self.scan(_channel=4)

        self._hardware.one_time_counter.close()
        self.moved.emit(self._hardware.mover.read_position_single(channel=1),
                        self._hardware.mover.read_position_single(channel=2),
                        self._hardware.mover.read_position_single(channel=4))

    def scan(self, _channel):
        pos = self._hardware.mover.read_position_single(channel=_channel)
        pos_list = np.arange(start=pos - 3 * self.step, stop=pos + 3 * self.step, step=self.step)
        max_cts = 0

        for point in pos_list:
            self._hardware.mover.move_position_single(channel=_channel, location=point)
            cts = self._hardware.one_time_counter.count_once()
            self.counts.emit(cts)

            if cts > max_cts:
                pos = point
                max_cts = cts

        self._hardware.mover.move_position_single(channel=_channel, location=pos)
