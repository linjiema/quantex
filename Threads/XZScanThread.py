"""
This Thread used for confocal scanning part
"""

from PyQt5 import QtCore
import numpy as np
import sys
import time


class XZScanThread(QtCore.QThread):
    """
    Confocal Scanning module as a thread, based on PyQt5.QtCore.QThread

    """
    SIGNAL_update = QtCore.pyqtSignal(float, list, list, name='update')

    def __init__(self, hardware=None, parent=None):
        self._hardware = hardware
        super().__init__(parent)  # Inherit the init method of parent class
        self.running = False
        self.parameters = [0, 100, 1, 0, 50, 0.5, 0, 0]
        # [X_Start, X_End, X_Step, Z_Start, Z_End, Z_Step, Y_Position, Line_Frequency]

    def run(self):
        self.running = True

        # Move to Goal layer
        print('move to goal layer')
        self._hardware.mover.move_position_single(channel=4, location=self.parameters[6])

        # Define the parameters
        x_start, x_end, x_step, z_start, z_end, z_step = self.parameters[:6]
        x_axis = np.arange(x_start, x_end, x_step)
        z_axis = np.arange(z_start, z_end, z_step)

        # Send the scanning parameter to stage
        wave_forward, wave_back = self._hardware.mover.generating_scan_array(channel=1,
                                                                             start_point=x_start,
                                                                             end_point=x_end,
                                                                             line_rate=1
                                                                             )

        # Scanning process
        forward_back_status = True
        for z_points in z_axis:
            if self.running:
                self._hardware.mover.move_position_single(channel=4, location=z_points)  # Move to one location
                while True:
                    try:
                        # Init all counting hardware
                        self._hardware.triggered_location_sensor.init_task()
                        self._hardware.triggered_counter.init_task()
                        self._hardware.timer.init_task()

                        # Start scanning
                        '''
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
                        # Processing the data
                        posArr = self._hardware.triggered_location_sensor.get_location_data()
                        ctsArr = self._hardware.triggered_counter.get_counts_array()
                        self._hardware.timer.recycle_timer()
                        forward_back_status = bool(1 - forward_back_status)
                    except BaseException as e:
                        print(e, z_points)
                        self._hardware.triggered_location_sensor.close()
                        self._hardware.trigger_counter.close()
                        self._hardware.timer.close()
                        continue
                    break

                self.update.emit(z_points, posArr, ctsArr)
            else:
                print('Warning: Scanning is stopped!')
                break
        self.running = False
