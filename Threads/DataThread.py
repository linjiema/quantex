"""
This Thread is used for data processing
"""

from PyQt5 import QtCore
from collections import deque
import numpy as np
import time
import sys


class DataThread(QtCore.QThread):
    """
    Data handler module as a thread, based on PyQt5.QtCore.QThread
    Use to handle line data and put it into image matrix.
    Needs:
    self.xArr: list of x command positions (100 points)
    self.y: y command position for the line
    self.yArr: list of y command positions (100 points)
    self.xData: position data
    self.countsData: photon count data
    """

    SIGNAL_update = QtCore.pyqtSignal(np.ndarray, name='update')

    def __init__(self, parent=None):
        self.lastUpdateTime = time.perf_counter()
        super().__init__(parent)
        self.raw = None
        self.running = False
        self.xArr = []
        self.yArr = []
        self.map = None
        self.sample_rate = 200

    def run(self):
        self.running = True

        # Because the first data in counts data is not good, we delete it
        # Cause self.xData has one more data point than self.countsData
        # Deal with this first
        x1 = deque(self.xData)
        x2 = deque(self.xData)
        x1.pop()
        x2.popleft()

        new_xData = (np.asarray(x1) + np.asarray(x2)) / 2
        self.xData = new_xData

        # Create count data array

        picked_counts = []

        for x_pos in self.xArr:
            # Search self.xData for the closest value
            each_x_arr = np.array([x_pos] * np.size(self.xData))
            diff_arr = list(np.abs(self.xData - each_x_arr))
            closest_index = diff_arr.index(min(diff_arr))

            cts_temp = self.countsData[closest_index]

            picked_counts.append(cts_temp * self.sample_rate)

        # Find the location in y axis
        y_index = list(self.yArr).index(self.y)
        # Put it into the image martix
        self.map[y_index] = np.asarray(picked_counts)

        # Save the raw data
        y_arr = [self.y] * len(self.xData)
        line_raw = np.transpose(np.asarray([self.xData, y_arr, self.countsData]))
        if self.raw is None:
            self.raw = line_raw
        else:
            self.raw = np.append(self.raw, line_raw, axis=0)

        # Update the image with 1 second interval
        t = time.perf_counter()
        if t - self.lastUpdateTime > 1:
            self.update.emit(self.map)
            self.lastUpdateTime = t

        self.running = False






