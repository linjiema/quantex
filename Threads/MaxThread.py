"""
This Thread is used to find the point has the max value of counts
"""
from PyQt5 import QtCore
import sys
import numpy


class MaxThread(QtCore.QThread):
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
        self._hardware.
