"""
This Thread is used to move the position of the stage
"""

from PyQt5 import QtCore
import sys
import time


class MoveThread_galvo(QtCore.QThread):
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
        pos_z = self._hardware.mover.read_position_single(channel=4)
        pos_xy = self._hardware.scanner.read_current_position()
        return pos_xy[0], pos_xy[1], pos_z

    def move_to_position(self, command=None):
        self._hardware.scanner.go_to_x(position=command[0])
        self._hardware.scanner.go_to_y(position=command[1])
        self._hardware.mover.move_position_single(channel=4, location=command[2])



