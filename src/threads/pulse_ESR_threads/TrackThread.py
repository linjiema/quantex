"""
This Thread is used to Tracking.
"""
from PyQt5 import QtCore
import sys
import numpy as np


class TrackThread(QtCore.QThread):
    """
    Maximizing module as a thread, based on PyQt5.QtCore.QThread
    parameters:
    @hardware: python object of hardware control
    """

    SIGNAL_tracking_data = QtCore.pyqtSignal(list, list, list, list, name='tracking_data')

    def __init__(self, hardware=None, parent=None):
        super().__init__(parent)
        self._hardware = hardware
        self.count_freq = 10  # Hz
        self.step = 0.1  # Micron

    def run(self):
        self._hardware.one_time_counter.count_freq = self.count_freq
        self._hardware.one_time_counter.init_task()
        self._hardware.pulser.laser_on()

        x_axis = self.scan(_channel=1)
        y_axis = self.scan(_channel=2)
        z_axis = self.scan(_channel=4)

        self._hardware.one_time_counter.close()
        pos_list = [x_axis[0], y_axis[0], z_axis[0]]
        cts_list = [x_axis[1], y_axis[1], z_axis[1]]
        pos_origin = [x_axis[2], y_axis[2], z_axis[2]]
        pos_final = [x_axis[3], y_axis[3], z_axis[3]]

        self.tracking_data.emit(pos_list, cts_list, pos_origin, pos_final)
        self._hardware.pulser.laser_off()

    def scan(self, _channel):
        cts_arr = []
        pos = self._hardware.mover.read_position_single(channel=_channel)
        pos_list = np.arange(start=pos - 3 * self.step, stop=pos + 3 * self.step, step=self.step)
        pos_origin = pos
        max_cts = 0

        for point in pos_list:
            self._hardware.mover.move_position_single(channel=_channel, location=point)
            cts = self._hardware.one_time_counter.count_once()
            cts_arr.append(cts)

            if cts > max_cts:
                pos = point
                max_cts = cts

        pos_final = pos
        self._hardware.mover.move_position_single(channel=_channel, location=pos)
        return [pos_list, cts_arr, pos_origin, pos_final]
