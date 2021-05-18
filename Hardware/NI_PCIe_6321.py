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


class TriggeredLocationSensor():
    def __init__(self):
        pass

    def init_task(self):
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
                                                        source='',  # need to set the terminal
                                                        active_edge=nidaqmx.constants.Edge.RISING,
                                                        sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                        samps_per_chan=1000)
        self.location_sensor.start()

    def get_location_raw_data(self):
        self.location_sensor.wait_until_done()
        location_raw = self.location_sensor.read(number_of_samples_per_channel=1000)
        self.location_sensor.close()

        return location_raw

    def get_location_data(self):
        raw_location_data = self.get_location_raw_data()
        location_data = raw_location_data * 10  # Transform voltage data to position data
        return location_data

    def close(self):
        self.location_sensor.close()


class TriggeredCounter():
    """
    This class defined a triggered counter used to get the pulse from APD.
    Use the pulses generated by DAQ to trigger the counter and sync with location sensor
    """

    def __init__(self):
        pass

    def init_task(self):
        self.counter = nidaqmx.Task()
        self.counter.ci_channels.add_ci_count_edges_chan(counter='/Dev1/ctr0',
                                                         name_to_assign_to_channel="",
                                                         edge=nidaqmx.constants.Edge.RISING,
                                                         initial_count=0,
                                                         count_direction=nidaqmx.constants.CountDirection.COUNT_UP)
        self.counter.timing.cfg_samp_clk_timing(rate=1000,
                                                source='Dev1/PFI14',
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

    def close(self):
        self.counter.close()


class HardwareTimer():
    def __init__(self):
        self.count_freq = 1000

    def init_task(self):
        self.counter_out = nidaqmx.Task()
        self.counter_out.co_channels.add_co_pulse_chan_freq(counter='Dev1/ctr1',
                                                            name_to_assign_to_channel="",
                                                            units=nidaqmx.constants.FrequencyUnits.HZ,
                                                            idle_state=nidaqmx.constants.Level.LOW,
                                                            initial_delay=0.0,
                                                            freq=self.count_freq,
                                                            duty_cycle=0.5
                                                            )
        self.counter_out.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                    samps_per_chan=1000)

    def change_freq(self, new_freq):
        self.count_freq = new_freq
        self.counter_out.close()
        self.init_task()

    def start_count(self):
        self.counter_out.start()

    def close(self):
        self.counter_out.close()


class OneTimeCounter_HardwareTimer():
    """
    This class define a counter that counts incoming pulse at a fixe count frequency
    When finished, call self.close() to clean up.
    """

    def __init__(self):
        self.count_freq = 1

    def init_task(self):
        # Output as timer
        self.counter_out = nidaqmx.Task()
        self.counter_out.co_channels.add_co_pulse_chan_freq(counter='Dev1/ctr1',
                                                            name_to_assign_to_channel="",
                                                            units=nidaqmx.constants.FrequencyUnits.HZ,
                                                            idle_state=nidaqmx.constants.Level.LOW,
                                                            initial_delay=0.0,
                                                            freq=self.count_freq,
                                                            duty_cycle=0.5
                                                            )
        self.counter_out.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                    samps_per_chan=1000)
        # Input as counter
        self.counter_in = nidaqmx.Task()
        self.counter_in.ci_channels.add_ci_count_edges_chan(counter='Dev1/ctr0',
                                                            name_to_assign_to_channel="",
                                                            edge=nidaqmx.constants.Edge.RISING,
                                                            initial_count=0,
                                                            count_direction=nidaqmx.constants.CountDirection.COUNT_UP)
        self.counter_in.timing.cfg_samp_clk_timing(rate=1000,
                                                   source='Dev1/PFI14',
                                                   active_edge=nidaqmx.constants.Edge.RISING,
                                                   sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                   samps_per_chan=1000)

    def count_once(self):
        freq = self.count_freq
        self.counter_in.start()
        self.counter_out.start()
        self.counter_in.wait_until_done()
        c1, c2 = self.counter_in.read(number_of_samples_per_channel=2, timeout=10.0)
        self.counter_in.stop()
        self.counter_out.stop()
        if c1 > c2:
            return (c2 + 0xFFFFFFFF + 1 - c1) * freq
        else:
            return (c2 - c1) * freq

    def change_freq(self, new_freq):
        self.count_freq = new_freq
        self.counter_out.close()
        self.init_task()

    def close(self):
        self.counter_in.close()
        self.counter_out.close()


if __name__ == '__main__':
    daq = Nontrigger_location_sensor()
