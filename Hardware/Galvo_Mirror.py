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
test_task.timing.cfg_samp_clk_timing(rate=20.0,
                                     source="",
                                     active_edge=nidaqmx.constants.Edge.RISING,
                                     sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                     samps_per_chan=40)
test_Writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(test_task.out_stream, auto_start=True)
samples = np.append(np.linspace(0, 8, num=30), np.zeros(10))

test_Writer.write_many_sample(samples)
test_task.wait_until_done()
test_task.stop()
test_task.close()
