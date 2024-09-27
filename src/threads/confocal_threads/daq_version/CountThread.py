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

        self.init_counter()  # Init hardware

        while self.running:
            if self.count_freq_changed:
                self._hardware.one_time_counter.change_freq(new_freq=self.count_freq)
                self.count_freq_changed = False
            cts = self.get_counts()
            self.counts.emit(cts)

        self.cleanup()  # Clean up the hardware

    def init_counter(self):
        self._hardware.one_time_counter.count_freq = self.count_freq
        self._hardware.one_time_counter.init_task()

    def get_counts(self):
        __cts = self._hardware.one_time_counter.count_once()
        return __cts

    def cleanup(self):
        self._hardware.one_time_counter.close()
