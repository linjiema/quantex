"""
This file is the functions for NI PCIe-6321 DAQ

"""
import ctypes
import os
import sys
import time
import numpy as np
import nidaqmx


class DAQ():
    def __init__(self):
        print(nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL)

    def init_task(self):
        self.daq = nidaqmx.Task()
        self.daq.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai5',
                                                 name_to_assign_to_channel="",
                                                 terminal_config=nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL,
                                                 min_val=-10.0,
                                                 max_val=10.0,
                                                 units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                 custom_scale_name=""
                                                 )


if __name__ == '__main__':
    daq = DAQ()
