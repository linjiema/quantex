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

    def run(self):
        """
        Move to setting position
        """
        if len(self.command) == 3:  # The input is a 3 axis value
            self.move_to_position(self.command)

        # Get position
        self.x_pos, self.y_pos, self.z_pos = self.get_current_position()
        self.moved.emit(self.x_pos, self.y_pos, self.z_pos)

    def get_current_position(self):
        pos = self._hardware.mover.read_position_single(channel=1), self._hardware.mover.read_position_single(channel=2), self._hardware.mover.read_position_single(channel=4)
        return pos

    def move_to_position(self, command=None):
        self._hardware.mover.move_position_all(location=command, check=False)
        time.sleep(1)


