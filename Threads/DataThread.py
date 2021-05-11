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
    self.y: x command position for the line
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
        self.XArr = True
        self.yArr = []
        self.map = None



