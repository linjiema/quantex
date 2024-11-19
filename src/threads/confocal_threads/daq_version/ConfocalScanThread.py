"""
This Thread used for confocal scanning part
"""

from PyQt5 import QtCore
import numpy as np
import sys
import time


class ConfocalScanThread(QtCore.QThread):
    """
    Confocal Scanning module as a thread, based on PyQt5.QtCore.QThread

    """
    SIGNAL_update = QtCore.pyqtSignal(float, list, list, name='update')

    def __init__(self, hardware=None, parent=None):
        self._hardware = hardware
        super().__init__(parent)  # Inherit the init method of parent class
        self.running = False
        self.parameters = [0, 65, 0.65, 0, 65, 0.65, 0, 0]
        # [X_Start, X_End, X_Step, Y_Start, Y_End, Y_Step, Z_Position, Line_Frequency]

    def run(self):
        self.running = True

        # Move to Goal layer
        # print('move to goal layer')
        self._hardware.mover.move_position_single(channel=4, location=self.parameters[6])

        # Define the parameters
        x_start, x_end, x_step, y_start, y_end, y_step = self.parameters[:6]
        x_axis = np.linspace(start=x_start, stop=x_end, num=round((x_end - x_start) / x_step),
                             endpoint=True, dtype=float)
        y_axis = np.linspace(start=y_start, stop=y_end, num=round((y_end - y_start) / y_step),
                             endpoint=True, dtype=float)

        # Send the scanning parameter to stage
        wave_forward, wave_back = self._hardware.mover.generating_scan_array(channel=1,
                                                                             start_point=x_start,
                                                                             end_point=x_end,
                                                                             line_rate=1
                                                                             )

        # Scanning process
        forward_back_status = True
        for y_points in y_axis:
            if self.running:
                # Move to one location
                self._hardware.mover.move_position_single(channel=2, location=y_points)
                while True:
                    try:
                        # Init all counting hardware
                        self._hardware.triggered_location_sensor.init_task()
                        self._hardware.triggered_counter.init_task()
                        self._hardware.timer.init_task()

                        # Start scanning
                        self._hardware.mover.move_position_single(channel=1, location=wave_forward[0])
                        self._hardware.timer.start_timer()
                        self._hardware.mover.scanning_single_line(channel=1, waveform=wave_forward)
                        self._hardware.mover.scanning_single_line(channel=1, waveform=wave_back)
                        '''
                        if forward_back_status:
                            self._hardware.mover.move_position_single(channel=1, location=wave_forward[0])
                            self._hardware.timer.start_timer()
                            self._hardware.mover.scanning_single_line(channel=1, waveform=wave_forward)
                        else:
                            self._hardware.mover.move_position_single(channel=1, location=wave_back[0])
                            self._hardware.timer.start_timer()
                            self._hardware.mover.scanning_single_line(channel=1, waveform=wave_back)
                        '''
                        # print(y_points)
                        # Processing the data
                        posArr = self._hardware.triggered_location_sensor.get_location_data()
                        ctsArr = self._hardware.triggered_counter.get_counts_array()
                        self._hardware.timer.recycle_timer()
                        forward_back_status = bool(1 - forward_back_status)
                    except BaseException as e:
                        print(e, y_points)
                        self._hardware.triggered_location_sensor.close()
                        self._hardware.triggered_counter.close()
                        self._hardware.timer.close()
                        return
                    break

                self.update.emit(y_points, list(posArr), list(ctsArr))
            else:
                print('Warning: Scanning is stopped!')
                break
        self.running = False
