"""
This Thread used for confocal scanning part
"""
import src.utils.logger as logger
from PyQt5 import QtCore
import numpy as np
import sys
import time


class ConfocalScanThread_galvo(QtCore.QThread):
    """
    Confocal Scanning module as a thread, based on PyQt5.QtCore.QThread

    """
    SIGNAL_update = QtCore.pyqtSignal(float, list, list, name='update')

    def __init__(self, hardware=None, parent=None):
        self._hardware = hardware
        super().__init__(parent)  # Inherit the init method of parent class
        self.running = False
        self.parameters = [-400, 400, 8, -400, 400, 8, 0, 0]
        # [X_Start, X_End, X_Step, Y_Start, Y_End, Y_Step, Z_Position, Line_Frequency]

    def run(self):
        self.running = True
        # set timer frequency
        self._hardware.timer.change_freq(new_freq=int(200 * self.parameters[7] * 2))

        # Move to Goal layer
        # print('move to goal layer')
        self._hardware.mover.move_position_single(channel=4, location=self.parameters[6])
        if self.parameters[7] <= 20:
            self.normal_scan()
        elif self._hardware.scanner.pos_to_volt_x(self.parameters[1]-self.parameters[0]) < 0.4:
            logger.logger.info(f"Can not perform fast scan, please reduce range or speed.")
        else:
            logger.logger.info(f"Can not perform fast scan, please reduce range or speed.")
        self.running = False

    def normal_scan(self):
        # Define the parameters
        x_start, x_end, x_step, y_start, y_end, y_step = self.parameters[:6]
        x_axis = np.linspace(start=x_start, stop=x_end, num=round((x_end - x_start) / x_step),
                             endpoint=True, dtype=float)
        y_axis = np.linspace(start=y_start, stop=y_end, num=round((y_end - y_start) / y_step),
                             endpoint=True, dtype=float)

        # Send the scanning parameter to stage
        full_wave = self._hardware.scanner.generating_scan_array(start_point=x_start,
                                                                 end_point=x_end,
                                                                 line_rate=self.parameters[7]
                                                                 )
        # Scanning process
        forward_back_status = True
        # set counter sample number
        self._hardware.triggered_counter.sample_number = 200
        for y_points in y_axis:
            if self.running:
                # Move to one location
                self._hardware.scanner.go_to_y(position=y_points)
                try:
                    # Init all counting hardware
                    self._hardware.scanner.wave_form_x = full_wave
                    self._hardware.scanner.set_x_scan_param()
                    self._hardware.triggered_counter.init_task()
                    self._hardware.timer.init_task()

                    # Start scanning
                    self._hardware.scanner.start_scan_x()
                    self._hardware.timer.start_timer()
                    # print(y_points)
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
                    forward_back_status = bool(1 - forward_back_status)
                except BaseException as e:
                    print(e, y_points)
                    self._hardware.scanner.recycle_x_scanner()
                    self._hardware.scanner.recycle_y_scanner()
                    self._hardware.triggered_counter.close()
                    self._hardware.timer.close()
                    return

                self.update.emit(y_points, list(posArr), list(ctsArr))
            else:
                print('Warning: Scanning is stopped!')
                self._hardware.scanner.recycle_x_scanner()
                self._hardware.scanner.recycle_y_scanner()
                self._hardware.triggered_counter.close()
                self._hardware.timer.close()
                break

    def fast_scan(self):
        pass
        # TODO: Implement fast scan
        '''
        # set parameter
        try:
            # Init all counting hardware
            self._hardware.scanner.init_xy_fast_scanner()
            self._hardware.scanner.set_xy_fast_scan_param()
            self._hardware.triggered_counter.init_task()
            self._hardware.timer.init_task()

            # Start scanning
            self._hardware.scanner.start_xy_fast_scan()
            self._hardware.timer.start_timer()

            # get data
            posArr = full_wave[:len(full_wave) // 2]
            ctsArr = self._hardware.triggered_counter.get_counts_array()
            self._hardware.timer.recycle_timer()

            self._hardware.scanner.wait_xy_fast_scan_finished()

        except BaseException as e:
            print(e)
            self._hardware.scanner.recycle_x_scanner()
            self._hardware.scanner.recycle_y_scanner()
            self._hardware.triggered_counter.close()
            self._hardware.timer.close()
            return

        self.update.emit(y_points, list(posArr), list(ctsArr))
        '''

