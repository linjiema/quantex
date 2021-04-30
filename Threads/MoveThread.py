"""
This Thread is used to move the position of the stage
"""

from PyQt5 import QtCore
import sys
import time


class MoveThread(QtCore.QThread):
    """
    Stage moving module as a thread, based on PyQt5.QtCore.QThread
    parameters:
    @hardware: python object of hardware control
    """

    SIGNAL_moved = QtCore.pyqtSignal(float, float, float, name='moved')

    def __init__(self, hardware=None, parent=None):
        super().__init__(parent)
        self._hardware = hardware
        self.command = []


