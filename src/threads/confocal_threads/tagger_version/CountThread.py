"""
This Thread is used to counting
"""

from PyQt5 import QtCore
import numpy as np
import sys


class CountThread(QtCore.QThread):
    """
    Counting module as a thread, based on PyQt5.QtCore.QThread
    parameters:
    @hardware: python object of hardware control
    """

    SIGNAL_counts = QtCore.pyqtSignal(int, name='counts')

    def __init__(self, hardware=None, parent=None):
        self._hardware = hardware
        super().__init__(parent)
        self.running = False
        self.count_freq = 1
        self.count_freq_changed = False

    def run(self):
        # Make sure the class have hardware
        if self._hardware is None:
            pass

        self.running = True  # Label the status
        self._hardware.counter.arm_one_time_counter(freq=self.count_freq)

        while self.running:
            if self.count_freq_changed:
                self._hardware.counter.reset_tt()
                self._hardware.counter.arm_one_time_counter(freq=self.count_freq)
                self.count_freq_changed = False

            cts = self._hardware.counter.one_time_counter_count_once(freq=self.count_freq)
            self.counts.emit(cts)

        self._hardware.counter.reset_tt()  # Clean up the hardware

