"""
This file is the functions for NI PCIe-6321 DAQ
"""
import collections
import ctypes
import os
import sys
import time
import numpy as np
import nidaqmx
import nidaqmx.constants


class TriggeredLocationSensor():
    def __init__(self):
        connection_check()

    def init_task(self):
        self.location_sensor = nidaqmx.Task()
        self.is_closed = False
        self.location_sensor.ai_channels.add_ai_voltage_chan(physical_channel='Dev1/ai5',
                                                             name_to_assign_to_channel="",
                                                             terminal_config=nidaqmx.constants.TerminalConfiguration.DIFF,
                                                             min_val=-10.0,
                                                             max_val=10.0,
                                                             units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                             custom_scale_name=""
                                                             )

        self.location_sensor.timing.cfg_samp_clk_timing(rate=200,
                                                        source='/Dev1/PFI13',  # need to set the terminal
                                                        active_edge=nidaqmx.constants.Edge.RISING,
                                                        sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                        samps_per_chan=200)
        self.location_sensor.start()

    def get_location_raw_data(self):
        self.location_sensor.wait_until_done()
        location_raw = self.location_sensor.read(number_of_samples_per_channel=200)
        self.location_sensor.close()
        self.is_closed = True
        return location_raw

    def get_location_data(self):
        raw_location_data = self.get_location_raw_data()
        # Transform voltage data to position data
        location_data = np.asarray(raw_location_data) * 6.69280347 + 0.54780765
        location_data = list(location_data)
        return location_data

    def close(self):
        if hasattr(self, 'location_sensor') and not self.is_closed:
            self.location_sensor.close()
            self.is_closed = True


class TriggeredCounter():
    """
    This class defined a triggered counter used to get the pulse from APD.
    Use the pulses generated by DAQ to trigger the counter and sync with location sensor
    """

    def __init__(self):
        connection_check()

    def init_task(self):
        self.counter = nidaqmx.Task()
        self.is_closed = False
        self.counter.ci_channels.add_ci_count_edges_chan(counter='Dev1/ctr2',
                                                         name_to_assign_to_channel="",
                                                         edge=nidaqmx.constants.Edge.RISING,
                                                         initial_count=0,
                                                         count_direction=nidaqmx.constants.CountDirection.COUNT_UP)
        self.counter.timing.cfg_samp_clk_timing(rate=400,
                                                source='/Dev1/PFI13',
                                                active_edge=nidaqmx.constants.Edge.RISING,
                                                sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                samps_per_chan=200)
        self.counter.start()

    def get_counts_array(self):
        self.counter.wait_until_done()
        cts_arr_raw = self.counter.read(number_of_samples_per_channel=200)
        self.counter.close()
        self.is_closed = True

        deq = collections.deque(cts_arr_raw)
        deq.pop()
        deq.appendleft(0)
        cts_arr = np.asarray(cts_arr_raw) - np.asarray(deq)

        return cts_arr.tolist()[1:]
        # The processing will decrease the size by 1)

    def close(self):
        if hasattr(self, 'counter') and not self.is_closed:
            self.counter.close()
            self.is_closed = True


class HardwareTimer():
    def __init__(self):
        connection_check()
        self.count_freq = 200

    def init_task(self):
        self.counter_out = nidaqmx.Task()
        self.is_closed = False
        self.counter_out.co_channels.add_co_pulse_chan_freq(counter='Dev1/ctr1',
                                                            name_to_assign_to_channel="",
                                                            units=nidaqmx.constants.FrequencyUnits.HZ,
                                                            idle_state=nidaqmx.constants.Level.LOW,
                                                            initial_delay=0.0,
                                                            freq=self.count_freq,
                                                            duty_cycle=0.5
                                                            )
        self.counter_out.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                    samps_per_chan=200)

    def change_freq(self, new_freq):
        self.count_freq = new_freq
        self.counter_out.close()
        self.init_task()

    def start_timer(self):
        self.counter_out.start()

    def recycle_timer(self):
        self.counter_out.wait_until_done()
        self.counter_out.close()
        self.is_closed = True

    def close(self):
        if hasattr(self, 'counter_out') and not self.is_closed:
            self.counter_out.close()
            self.is_closed = True


class OneTimeCounter_HardwareTimer():
    """
    This class define a counter that counts incoming pulse at a fixe count frequency
    When finished, call self.close() to clean up.
    """

    def __init__(self):
        connection_check()
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
                                                    samps_per_chan=2)
        # Input as counter
        self.counter_in = nidaqmx.Task()
        self.is_closed = False
        self.counter_in.ci_channels.add_ci_count_edges_chan(counter='Dev1/ctr2',
                                                            name_to_assign_to_channel="",
                                                            edge=nidaqmx.constants.Edge.RISING,
                                                            initial_count=0,
                                                            count_direction=nidaqmx.constants.CountDirection.COUNT_UP)
        self.counter_in.timing.cfg_samp_clk_timing(rate=self.count_freq * 3,
                                                   source='/Dev1/PFI13',
                                                   active_edge=nidaqmx.constants.Edge.RISING,
                                                   sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                   samps_per_chan=2)

    def count_once(self) -> int:
        freq = self.count_freq
        self.counter_in.start()
        self.counter_out.start()
        self.counter_in.wait_until_done()
        self.counter_out.wait_until_done()
        cts_arr = self.counter_in.read(number_of_samples_per_channel=2, timeout=10.0)
        self.counter_in.stop()
        self.counter_out.stop()
        if cts_arr[0] > cts_arr[1]:
            return int((cts_arr[1] + 0xFFFFFFFF + 1 - cts_arr[0]) * freq)
        else:
            return int((cts_arr[1] - cts_arr[0]) * freq)

    def change_freq(self, new_freq):
        self.count_freq = new_freq
        self.counter_out.close()
        self.init_task()

    def close(self):
        if hasattr(self, 'counter_in') and not self.is_closed:
            self.counter_in.close()
            self.counter_out.close()
            self.is_closed = True


def connection_check():
    local_system = nidaqmx.system.System.local()
    status = 0
    try:
        for each_device in local_system.devices:
            if each_device.name == 'Dev1':
                status = 1
        if status == 0:
            raise ValueError('Check NI Device Index!')
    except BaseException as e:
        raise e


class GScanner():
    SCAN_MODE_SINGLE_POINT = 0
    SCAN_MODE_SCANNING = 1

    def __init__(self):
        connection_check()
        self.wave_form_x = []
        self.wave_form_y = []
        self.sample_number = 200
        self.timing_rate = 1000
        self.init_scanner()
        self.scan_mode_x = self.SCAN_MODE_SINGLE_POINT
        self.scan_mode_y = self.SCAN_MODE_SINGLE_POINT

    def init_scanner(self):
        self.x_scanner = nidaqmx.Task(new_task_name='x_scanner')
        self.x_scanner.ao_channels.add_ao_voltage_chan(physical_channel='Dev1/ao0',
                                                       name_to_assign_to_channel="",
                                                       min_val=-5.0,
                                                       max_val=5.0,
                                                       units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                       custom_scale_name=""
                                                       )
        self.is_closed_x = False
        self.y_scanner = nidaqmx.Task(new_task_name='y_scanner')
        self.y_scanner.ao_channels.add_ao_voltage_chan(physical_channel='Dev1/ao1',
                                                       name_to_assign_to_channel="",
                                                       min_val=-5.0,
                                                       max_val=5.0,
                                                       units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                       custom_scale_name=""
                                                       )
        self.is_closed_y = False

    def go_to_x(self, position):
        self.x_scanner.stop()
        if self.scan_mode_x == self.SCAN_MODE_SCANNING:
            self.x_scanner.close()
            self.x_scanner = nidaqmx.Task(new_task_name='x_scanner')
            self.x_scanner.ao_channels.add_ao_voltage_chan(physical_channel='Dev1/ao0',
                                                           name_to_assign_to_channel="",
                                                           min_val=-5.0,
                                                           max_val=5.0,
                                                           units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                           custom_scale_name=""
                                                           )
            self.scan_mode_x = self.SCAN_MODE_SINGLE_POINT
        self.x_scanner.write(self.pos_to_volt_x(position), auto_start=True, timeout=10.0)
        self.x_scanner.wait_until_done()
        self.x_scanner.stop()

    def go_to_y(self, position):
        self.y_scanner.stop()
        if self.scan_mode_y == self.SCAN_MODE_SCANNING:
            self.y_scanner.close()
            self.y_scanner = nidaqmx.Task(new_task_name='y_scanner')
            self.y_scanner.ao_channels.add_ao_voltage_chan(physical_channel='Dev1/ao1',
                                                           name_to_assign_to_channel="",
                                                           min_val=-5.0,
                                                           max_val=5.0,
                                                           units=nidaqmx.constants.VoltageUnits.VOLTS,
                                                           custom_scale_name=""
                                                           )
            self.scan_mode_y = self.SCAN_MODE_SINGLE_POINT
        self.y_scanner.write(self.pos_to_volt_y(position), auto_start=True, timeout=10.0)
        self.y_scanner.wait_until_done()
        self.y_scanner.stop()

    def set_x_scan_param(self):
        self.x_scanner.timing.cfg_samp_clk_timing(rate=self.timing_rate,
                                                  source='/Dev1/PFI13',
                                                  active_edge=nidaqmx.constants.Edge.RISING,
                                                  sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                  samps_per_chan=int(self.sample_number))
        self.x_scanner.write(self.wave_form_x, auto_start=False)
        self.scan_mode_x = self.SCAN_MODE_SCANNING

    def set_y_scan_param(self):
        self.y_scanner.timing.cfg_samp_clk_timing(rate=self.timing_rate,
                                                  source='/Dev1/PFI13',
                                                  active_edge=nidaqmx.constants.Edge.RISING,
                                                  sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                  samps_per_chan=int(self.sample_number))
        self.y_scanner.write(self.wave_form_y, auto_start=False)
        self.scan_mode_y = self.SCAN_MODE_SCANNING

    def start_scan_x(self):
        self.x_scanner.start()

    def wait_x_scan_finished(self):
        self.x_scanner.wait_until_done()
        self.x_scanner.stop()

    def stop_scan_x(self):
        self.x_scanner.stop()

    def start_scan_y(self):
        self.y_scanner.start()

    def wait_y_scan_finished(self):
        self.y_scanner.wait_until_done()

    def stop_scan_y(self):
        self.y_scanner.stop()

    def pos_to_volt_x(self, position):
        # load a stored table to convert position to voltage
        pass
        return position

    def pos_to_volt_y(self, position):
        # load a stored table to convert position to voltage
        pass
        return position

    def vol_to_position(self, xy_voltage: np.ndarray) -> np.ndarray:
        """

        :param xy_voltage:
        :return:
        """
        return xy_voltage

    def read_current_position(self) -> np.ndarray:
        with nidaqmx.Task() as voltage_read:
            voltage_read.ai_channels.add_ai_voltage_chan("Dev1/_ao0_vs_aognd")
            voltage_read.ai_channels.add_ai_voltage_chan("Dev1/_ao1_vs_aognd")
            voltage_read.timing.cfg_samp_clk_timing(rate=10000, sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                                    samps_per_chan=5)
            voltage_temp = np.average(voltage_read.read(number_of_samples_per_channel=5), axis=1)
        position_temp = self.vol_to_position(voltage_temp)
        return position_temp

    def close(self):
        if hasattr(self, 'x_scanner') and not self.is_closed_x:
            self.x_scanner.close()
            self.is_closed_x = True
        if hasattr(self, 'y_scanner') and not self.is_closed_y:
            self.y_scanner.close()
            self.is_closed_y = True


if __name__ == '__main__':
    scanner = GScanner()

    scanner.go_to_x(position=0.1)
    time.sleep(0.1)
    print(scanner.read_current_position())
    scanner.go_to_x(position=0.2)
    time.sleep(0.1)
    print(scanner.read_current_position())
    scanner.go_to_x(position=0.1)
    time.sleep(0.1)
    print(scanner.read_current_position())
    scanner.go_to_x(position=0.2)
    time.sleep(0.1)
    print(scanner.read_current_position())
    scanner.go_to_x(position=0.1)
    time.sleep(0.1)
    print(scanner.read_current_position())
    scanner.go_to_x(position=0.2)
    time.sleep(0.1)
    print(scanner.read_current_position())

    time.sleep(0.1)

    scanner.close()
    # with nidaqmx.Task() as task:
    #     task.ai_channels.add_ai_voltage_chan("Dev1/_ao0_vs_aognd")
    #     task.ai_channels.add_ai_voltage_chan("Dev1/_ao1_vs_aognd")
    #     task.timing.cfg_samp_clk_timing(rate=1000, sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
    #                                     samps_per_chan=5)
    #     data = task.read(number_of_samples_per_channel=5)
    #     print(data)
    #     print(np.round(np.average(data, axis=1), 4))
    #     [a, b] = np.average(data, axis=1)
    #     print(a)
    #     print(b)
    #     print(type(np.average(data, axis=1)))
    #     print(type(a))
