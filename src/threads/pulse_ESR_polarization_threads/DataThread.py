"""
Created on Jun 30, 2021

This Thread is used to do the data processing in the experiment.
The Raw Data is all 0, when the scanning get the new data, the data at corresponding location will be rewrite.

@author: Linjie
"""

from PyQt5 import QtCore
import numpy as np
import time


class DataThread(QtCore.QThread):

    SIGNAL_update = QtCore.pyqtSignal(list, list, name='update')

    def __init__(self, hardware=None, parent=None):
        super().__init__(parent)
        self.last_update_time = time.perf_counter()
        self._hardware = hardware
        self.running_status = False
        self.raw = None

        # Data for whole measurement
        self.ref_all = []
        self.sig_all = []
        # Input data
        self.sig = None
        self.ref = None
        self.freq_or_time = None
        self.point = None
        self.loop = None

        self.ref_ave_temp = []
        self.sig_ave_temp = []
        # Data used to emit
        self.ref_emit = []
        self.sig_emit = []
        # Init loop_old to -1 make sure the data will be update at the beginning of the scanning
        self.loop_old = -1

    def run(self):
        """
        Emit: List of the average value of Signal and Reference (Only for update the plot in GUI)
        Update the data for the plot every 1 second
        Rewrite the value in self.raw (Raw Data)
        """
        self.running_status = True
        # Rewrite the data in raw data
        # For each point data in raw, it contains 4 value: Signal Counts, Reference Counts, Frequency/Time, Loop Number
        self.raw[7][self.loop][self.point] = [self.sig, self.ref, self.freq_or_time, self.loop]
        # Decide if to add a new loop for the average
        state = self.loop > self.loop_old
        if state:
            self.loop_old = self.loop
            self.ref_all.append(self.ref_ave_temp)
            self.sig_all.append(self.sig_ave_temp)

        # Replace the data with the data we get in the scanning
        self.ref_all[self.loop][self.point] = self.ref
        self.sig_all[self.loop][self.point] = self.sig

        # Update the plot every 1 second.
        t = time.perf_counter()
        if t - self.last_update_time > 1 or state:
            self.ref_emit = list(np.average(self.ref_all, axis=0))
            self.sig_emit = list(np.average(self.sig_all, axis=0))
            self.update.emit(self.ref_emit, self.sig_emit)
            self.last_update_time = t

        self.running_status = False
