from PyQt5 import QtCore
import numpy as np
import sys, time


class ConfocalScanThread(QtCore.QThread):
    """
    Confocal Scaning module as a thread, based on PyQt5.QtCore.Qthread

    """
    SIGNAL_update = QtCore.pyqtSignal(float, list, list, name='update')

    def __init__(self, hardware=None, parent=None):
        self._hardware = hardware
        super().__init__(parent)  # Inherit the init method of parent class
        self.running = False
        self.parameters = [0, 100, 1, 0, 100, 1, 0, 0]
        # [X_Start, X_End, X_Step, Y_Start, Y_End, Y_Step, Z_Position, Line_Frequency]

    def run(self):
        self.running = True

        # Move to Goal layer
        print('move to goal layer')
        self._hardware.mover.move_position_single(channel=4, location=self.parameters[6])

        # Define the parameters
        x_start, x_end, x_step, y_start, y_end, y_step = self.parameters[:6]
        x_axis = np.array(x_start, x_end, x_step)
        y_axis = np.array(y_start, y_end, y_step)

        # Send the scanning parameter to stage
        self._hardware.mover.scaning_setting(channel=1,
                                             start_point=x_start, end_point=x_end,
                                             line_rate=4
                                             )

        # Scanning process
        for y_points in y_axis:
            if self.running:
                self._hardware.mover.move_position_single(channel=2, location=y_points)  # Move to one location
                while True:
                    pass



