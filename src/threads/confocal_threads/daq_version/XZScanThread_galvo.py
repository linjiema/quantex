"""
This Thread used for confocal scanning part
"""

from PyQt5 import QtCore
import numpy as np
import sys
import time


class XZScanThread_galvo(QtCore.QThread):
    """
    Confocal Scanning module as a thread, based on PyQt5.QtCore.QThread

    """
    SIGNAL_update = QtCore.pyqtSignal(float, list, list, name='update')

    def __init__(self, hardware=None, parent=None):
        self._hardware = hardware
        super().__init__(parent)  # Inherit the init method of parent class
        self.running = False
        self.parameters = [-0.4, 0.4, 0.008, 0, 35, 0.35, 0, 0]
        # [X_Start, X_End, X_Step, Z_Start, Z_End, Z_Step, Y_Position, Line_Frequency]

    def run(self):
        self.running = True

        # Move to Goal layer
        print('move to goal layer')
        self._hardware.mover.move_position_single(channel=2, location=self.parameters[6])

        # Define the parameters
        x_start, x_end, x_step, z_start, z_end, z_step = self.parameters[:6]
        x_axis = np.linspace(start=x_start, stop=x_end, num=round((x_end - x_start) / x_step),
                             endpoint=True, dtype=float)
        z_axis = np.linspace(start=z_start, stop=z_end, num=round((z_end - z_start) / z_step),
                             endpoint=True, dtype=float)

        # Send the scanning parameter to stage
        full_wave = self._hardware.scanner.generating_scan_array(start_point=x_start,
                                                                 end_point=x_end,
                                                                 line_rate=self.parameters[7]
                                                                 )
        # Scanning process
        forward_back_status = True
        for z_points in z_axis:
            if self.running:
                # Move to one location
                self._hardware.mover.move_position_single(channel=4, location=z_points)
                while True:
                    try:
                        # Init all counting hardware
                        self._hardware.scanner.wave_form_x = full_wave
                        self._hardware.scanner.set_x_scan_param()
                        self._hardware.triggered_counter.init_task()
                        self._hardware.timer.init_task()

                        # Start scanning
                        self._hardware.scanner.start_scan_x()
                        self._hardware.timer.start_timer()
                        print(z_points)
                        # get data
                        posArr = full_wave[:len(full_wave) // 2]
                        ctsArr = self._hardware.triggered_counter.get_counts_array()
                        self._hardware.timer.recycle_timer()
                        # go back to start point
                        self._hardware.timer.init_task()
                        self._hardware.timer.start_timer()
                        self._hardware.scanner.wait_x_scan_finished()
                        self._hardware.timer.recycle_timer()
                        self._hardware.scanner.recycle_x_scanner()
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
                        # Processing the data
                        forward_back_status = bool(1 - forward_back_status)
                    except BaseException as e:
                        print(e, z_points)
                        self._hardware.scanner.recycle_x_scanner()
                        self._hardware.scanner.recycle_y_scanner()
                        self._hardware.triggered_counter.close()
                        self._hardware.timer.close()
                        return
                    break

                self.update.emit(z_points, list(posArr), list(ctsArr))
            else:
                print('Warning: Scanning is stopped!')
                break
        self.running = False
