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
        self.step_xy = 1  # mV
        self.step_z = 0.1  # Micron

    def run(self):
        self._hardware.one_time_counter.count_freq = self.count_freq
        self._hardware.one_time_counter.init_task()

        self.scan_galvo(_channel=1, step=self.step_xy)
        self.scan_galvo(_channel=2, step=self.step_xy)
        self.scan(_channel=4, step=self.step_z)

        self._hardware.one_time_counter.close()
        pos_xy = self._hardware.scanner.read_current_position()
        self.moved.emit(pos_xy[0],
                        pos_xy[1],
                        self._hardware.mover.read_position_single(channel=4))

    def scan_galvo(self, _channel, step):
        if _channel == 1:
            pos = self._hardware.scanner.read_current_position()[0]
            pos_list = np.arange(start=pos - 3 * step, stop=pos + 3 * step, step=step)
            max_cts = 0

            for point in pos_list:
                self._hardware.scanner.go_to_x(position=point)
                # self._hardware.mover.move_position_single(channel=_channel, location=point)
                cts = self._hardware.one_time_counter.count_once()
                self.counts.emit(cts)

                if cts > max_cts:
                    pos = point
                    max_cts = cts

            self._hardware.scanner.go_to_x(position=pos)
            # self._hardware.mover.move_position_single(channel=_channel, location=pos)
        elif _channel == 2:
            pos = self._hardware.scanner.read_current_position()[1]
            pos_list = np.arange(start=pos - 3 * step, stop=pos + 3 * step, step=step)
            max_cts = 0

            for point in pos_list:
                self._hardware.scanner.go_to_y(position=point)
                # self._hardware.mover.move_position_single(channel=_channel, location=point)
                cts = self._hardware.one_time_counter.count_once()
                self.counts.emit(cts)

                if cts > max_cts:
                    pos = point
                    max_cts = cts

            self._hardware.scanner.go_to_y(position=pos)

    def scan(self, _channel, step):
        pos = self._hardware.mover.read_position_single(channel=_channel)
        pos_list = np.arange(start=pos - 3 * step, stop=pos + 3 * step, step=step)
        max_cts = 0

        for point in pos_list:
            self._hardware.mover.move_position_single(channel=_channel, location=point)
            cts = self._hardware.one_time_counter.count_once()
            self.counts.emit(cts)

            if cts > max_cts:
                pos = point
                max_cts = cts

        self._hardware.mover.move_position_single(channel=_channel, location=pos)
