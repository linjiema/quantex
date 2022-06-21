import collections
import ctypes
import os
import sys
import time
import numpy as np
import nidaqmx
from nidaqmx import *

test_task = nidaqmx.Task()

test_task.ao_channels.add_ao_voltage_chan(physical_channel='Dev1/ao0',
                                          name_to_assign_to_channel="",
                                          min_val=-10.0,
                                          max_val=10.0,
                                          units=nidaqmx.constants.VoltageUnits.VOLTS,
                                          custom_scale_name=""
                                          )
test_task.timing.cfg_samp_clk_timing(rate=400,
                                     source="",
                                     active_edge=nidaqmx.constants.Edge.RISING,
                                     sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                     samps_per_chan=1000)
test_Writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(test_task.out_stream, auto_start=True)
samples = np.append(np.linspace(-8, 8, num=990), np.zeros(10))

test_Writer.write_many_sample(samples)
test_task.wait_until_done()
test_task.stop()
test_task.close()


class GalvoMirror:

    def __init__(self):
        self.voltage_angel_ratio = 1.0

    def move_to_position(self):
        pass

    def get_position(self):
        pass

    def init_x_voltage_sensor(self):
        self.x_voltage_sensor = nidaqmx.Task()
        self.x_voltage_sensor.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai0',
                                                              name_to_assign_to_channel="",
                                                              terminal_config=nidaqmx.constant.TerminalConfiguration.DIFFERENTIAL,
                                                              min_val=-10.0,
                                                              max_val=10.0,
                                                              units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                              custom_scale_name="")
        self.x_voltage_sensor.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                         samps_per_chan=2)

    def init_y_voltage_sensor(self):
        self.y_voltage_sensor = nidaqmx.Task()
        self.y_voltage_sensor.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai1',
                                                              name_to_assign_to_channel="",
                                                              terminal_config=nidaqmx.constant.TerminalConfiguration.DIFFERENTIAL,
                                                              min_val=-10.0,
                                                              max_val=10.0,
                                                              units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                              custom_scale_name="")
        self.y_voltage_sensor.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                         samps_per_chan=2)

    @staticmethod
    def trans_location_to_voltage(x):
        pass

    @staticmethod
    def trans_voltage_to_location(x):
        pass
