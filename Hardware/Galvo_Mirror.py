import collections
import ctypes
import os
import sys
import time
import numpy as np
import nidaqmx


class Mirror_controller():
    def __init__(self):
        pass

    def init_task(self):
        self.x_axis_mirror = nidaqmx.Task()
        self.y_axis_mirror = nidaqmx.Task()
        self.x_axis_mirror.ao_channels.add_ao_voltage_chan(physical_channel='Dev1/ao0',
                                                           name_to_assign_to_channel="",
                                                           min_val=-10.0,
                                                           max_val=10.0,
                                                           units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                           custom_scale_name=""
                                                           )
        self.x_axis_mirror.timing.cfg_samp_clk_timing(rate=20.0,
                                                      source="",
                                                      active_edge=nidaqmx.constants.Edge.RISING,
                                                      sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                      samps_per_chan=40)
        test_Writer = self.x_axis_mirror.stream_writers.AnalogSingleChannelWriter(self.x_axis_mirror.out_stream, auto_start=True)
        samples = np.append(np.linspace(0, 8, num=30), np.zeros(10))

        test_Writer.write_many_sample(samples)
        self.x_axis_mirror.wait_until_done()
        self.x_axis_mirror.stop()
        self.x_axis_mirror.close()


if __name__ == '__main__':
    mirror = Mirror_controller()
    mirror.init_task()