"""
Created on Jun 30, 2021

This Thread is used to do the Frequency Sweep experiment.

@author: Linjie
"""

from PyQt5 import QtCore
import time
from nidaqmx.errors import *
from src.threads.pulse_ESR_threads.TrackThread import TrackThread
import numpy as np
import random


class FrequencySweepThread(QtCore.QThread):

    # Signal for passing the data to main thread ([Signal, Reference, Frequency, Point Number, Loop Number])
    SIGNAL_update = QtCore.pyqtSignal(int, int, float, int, int, name='update')
    # Signal for passing the tracking data to main thread
    SIGNAL_tracking_data = QtCore.pyqtSignal(list, list, list, list, name='tracking_data')

    def __init__(self, hardware=None, parent=None):
        super().__init__(parent)
        # Get hardware from Main Thread
        self._hardware = hardware
        self.tThread = TrackThread(self._hardware)
        self.tThread.tracking_data.connect(self.emit_data)
        # Initialize scanning parameters
        # Parameters will not change in one experiment
        self.delay = None
        self.freq_arr = []
        self.pulse_form = []
        # Parameters can be changed when pause/resume the experiment
        self.loop_num = [0, 200]  # [Current Loop , Total Loop]
        self.point_num = [0, 0]  # [Current point, Total point]
        # Parameter may change during the experiment
        self.threshold = 0
        self.auto_track = False
        self.running_status = False
        self.pulse_init_status = False
        # Init
        self.pulse_seq = []

    def run(self):
        """
        Do the Scanning part
        :return: None
        :emit: [Signal, Reference, Frequency, Point Number, Loop Number]
        """
        # Define the running status
        self.running_status = True
        # Check the pulse initialized status
        # If haven't been initialized, init first
        if self.pulse_init_status is False:
            try:
                self.pulse_seq = generate_seq(pulse_form=self.pulse_form, delay_dic=self.delay)
                self._hardware.pulser.load_seq(pulse_seq=self.pulse_seq, repeat_time=self._hardware.sample_trigger.average)
                self.pulse_init_status = True

            except TypeError as e:
                print(e)
                print('Warning: Please select a Pulse sequence!')
                return

            except ValueError as e:
                print(e)
                print('Warning: Please use the sequence for Frequency Scan!')
                return

        # Sweeping Frequency
        try:  # Try can be used to jump out of all loops
            # Do the sweep  by loop
            for loop in range(self.loop_num[1])[self.loop_num[0]:]:
                # Sweep the frequency
                for freq in self.freq_arr[self.point_num[0]:]:
                    # If running, do the scan
                    while self.running_status is True:
                        # Set Microwave Frequency
                        self._hardware.mw_source.set_freq(freq=freq)
                        # Init Gated Counter
                        self._hardware.gate_counter.init_task()
                        self._hardware.sample_trigger.init_task()
                        # Start Gated Counter
                        self._hardware.gate_counter.start_task()
                        self._hardware.sample_trigger.start_task()
                        # Start Pulse Generator
                        self._hardware.pulser.start_output()
                        # Close SampleTrigger when finish sampling
                        self._hardware.sample_trigger.recycle_task()  # May meet timeout error
                        # Get the data and close the Counter
                        ref, sig = self._hardware.gate_counter.get_counts()
                        # print('ref=', ref, '  sig=', sig, '  freq=', freq)

                        # Track when Auto Track is activated
                        if self.auto_track is True:
                            # Track when ref can not reach the requirement of threshold
                            if ref < self.threshold:
                                self.tThread.start()
                                while self.tThread.isFinished() is False:
                                    time.sleep(1)
                                self.pulse_seq = generate_seq(pulse_form=self.pulse_form, delay_dic=self.delay)
                                self._hardware.pulser.load_seq(pulse_seq=self.pulse_seq, repeat_time=self._hardware.sample_trigger.average)
                                continue  # Redo the Scan for this frequency
                        # Emit the data to the Main Thread
                        self.update.emit(sig, ref, freq, self.point_num[0], self.loop_num[0])
                        self.point_num[0] = self.point_num[0] + 1
                        break

                    # If not scanning, jump out of all the loop
                    else:
                        raise EndForLoop()
                # When finish one loop, init the point number and update the loop number
                self.point_num[0] = 0
                self.loop_num[0] = self.loop_num[0] + 1

        except EndForLoop:
            pass

        except DaqError as e:
            print(e, '\n Loop=', loop, ', Frequency=', freq, '\n')
            self._hardware.gate_counter.close()
            self._hardware.sample_trigger.close()
            self._hardware.pulser.stop_output()
            self.running_status = False
            return

        # At the end of the scanning, set running status to False
        self.running_status = False
        # Sleep 1 second to update the data again
        time.sleep(1)
        # If the point_num and loop_num meet the following condition, means the scanning fully finish
        if self.point_num[0] == 0 and self.loop_num[0] == self.loop_num[1]:
            # Update the last data
            self.update.emit(sig, ref, freq, self.point_num[1] - 1, self.loop_num[1] - 1)
        else:
            # Update the last data
            self.update.emit(sig, ref, freq, self.point_num[0], self.loop_num[0])

    @QtCore.pyqtSlot(list, list, list, list)
    def emit_data(self, pos_list, cts_list, pos_origin, pos_final):
        self.tracking_data.emit(pos_list, cts_list, pos_origin, pos_final)


def generate_seq(pulse_form, delay_dic):
    """
    This method transform the pulse generated by the SeqEditor to the pulse with trigger pulse sequence and delay
    :param pulse_form: The pulse generated by the SeqEditor
    :param delay_dic:  The delay data of the AOM and Microwave
    :return: Pulse sequence with the trigger pulse channel and delay
    """
    # Add delay based on the delay data
    seq_with_delay = add_delay(pulse_form=pulse_form, delay_dic=delay_dic)
    # Add trigger pulse channel
    seq_with_trig_channel = add_trig_channel(pulse_form=seq_with_delay)
    return seq_with_trig_channel


def add_delay(pulse_form, delay_dic):
    """
    This method add delay for AOM and Microwave based on the delay data
    :param pulse_form: The pulse generated by the SeqEditor
    :param delay_dic: The delay data of the AOM and Microwave
    :return: Pulse sequence with delay
    """
    # Get delay data from dic
    laser_delay = delay_dic.get('AOM')
    mw_delay = delay_dic.get('MW')
    # Init Pulse Sequence with delay
    seq_with_delay = []
    # Add delay for Microwave and Laser
    if int(laser_delay) > int(mw_delay):
        for each_pulse in pulse_form:
            if each_pulse[0] == 'Laser':
                pass
            elif each_pulse[0] == 'MicroWave':
                each_pulse[1] = str(int(each_pulse[1]) + int(laser_delay) - int(mw_delay))
                each_pulse[2] = str(int(each_pulse[2]) + int(laser_delay) - int(mw_delay))
            else:
                each_pulse[1] = str(int(each_pulse[1]) + int(laser_delay))
                each_pulse[2] = str(int(each_pulse[2]) + int(laser_delay))
            seq_with_delay.append(each_pulse)
    else:
        for each_pulse in pulse_form:
            if each_pulse[0] == 'Laser':
                each_pulse[1] = str(int(each_pulse[1]) + int(mw_delay) - int(laser_delay))
                each_pulse[2] = str(int(each_pulse[2]) + int(mw_delay) - int(laser_delay))
            elif each_pulse[0] == 'MicroWave':
                pass
            else:
                each_pulse[1] = str(int(each_pulse[1]) + int(mw_delay))
                each_pulse[2] = str(int(each_pulse[2]) + int(mw_delay))
            seq_with_delay.append(each_pulse)

    return seq_with_delay


def add_trig_channel(pulse_form):
    """
    This method add trigger pulse sequence for any Pulse Sequence
    :param pulse_form: Any pulse sequence
    :return: Pulse sequence with trigger pulse channel
    """
    end_time = 0
    # Find the End time of Pulse Sequence
    for each_channel in pulse_form:
        if int(each_channel[2]) > end_time:
            end_time = int(each_channel[2])
    seq_with_trig_channel = pulse_form.copy()
    seq_with_trig_channel.append(['Trigger', str(end_time), str(end_time + 20)])

    return seq_with_trig_channel


class EndForLoop(Exception):
    pass