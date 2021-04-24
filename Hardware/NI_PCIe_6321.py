"""
This file is the functions for NI PCIe-6321 DAQ

"""
import collections
import ctypes
import os
import sys
import time

import numpy
import numpy as np
import nidaqmx


class Nontrigger_location_sensor():
    def __init__(self):
        pass

    def init_location_sensing_task(self):
        self.location_sensor = nidaqmx.Task()
        self.location_sensor.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai5',
                                                             name_to_assign_to_channel="",
                                                             terminal_config=nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL,
                                                             min_val=-10.0,
                                                             max_val=10.0,
                                                             units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                             custom_scale_name=""
                                                             )

        self.location_sensor.timing.cfg_samp_clk_timing(rate=1000,
                                                        source='',   # need to set the terminal
                                                        active_edge=nidaqmx.constants.Edge.RISING,
                                                        sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                        samps_per_chan=1000)
        self.location_sensor.start()

    def get_location_raw_data(self):
        self.location_sensor.wait_until_done()
        location_raw = self.location_sensor.read(number_of_samples_per_channel=1000)
        self.location_sensor.close()

        return location_raw


class TriggeredCounter():
    """
    This class defined a triggered counter used to get the pulse from APD.
    Use the pulses generated by DAQ to trigger the counter and sync with location sensor
    """

    def __init__(self):
        pass

    def init_tasks(self):
        self.counter = nidaqmx.Task()
        self.counter.ci_channels.add_ci_count_edges_chan(counter='',
                                                         name_to_assign_to_channel="",
                                                         edge=nidaqmx.constants.Edge.RISING,
                                                         initial_count=0,
                                                         count_direction=nidaqmx.constants.CountDirection.COUNT_UP)
        self.counter.timing.cfg_samp_clk_timing(rate=1000,
                                                source='',  # need to set the terminal
                                                active_edge=nidaqmx.constants.Edge.RISING,
                                                sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                samps_per_chan=1000)
        self.counter.start()

    def get_counts_array(self):
        self.counter.wait_until_done()
        cts_arr_raw = self.counter.read(number_of_samples_per_channel=1000)
        self.counter.close()

        deq = collections.deque(cts_arr_raw)
        deq.pop()
        deq.appendleft(0)
        cts_arr = numpy.asarray(cts_arr_raw) - numpy.asarray(deq)

        return cts_arr.tolist()[1:]
        # May need to change the size of the list we get
        # (the processing will decrease the size by 1)
        # maybe need to get 1 more data


if __name__ == '__main__':
    daq = Nontrigger_location_sensor()
