"""
Created on Jun 6, 2021

@author: Linjie

This File is used for control of SynthUSB3
Works under python3
Need the pyserial package
"""

import serial
import time


class SynthUSB3():
    """
    This class contain the methods for control the Microwave Source
    """
    def __init__(self):
        """
        Define an empty port with default setting:
            basudrate = 115200
            timeout = 0.1
        """
        self.mw_source = serial.Serial(baudrate=115200, timeout=0.1)

    def init_port(self, port_num='COM4', baudrate_setting=115200, timeout_setting=0.1):
        """
        Init and open the microwave source with the setting
        :param port_num: The COM port number of the SynthUSB3
        :param baudrate_setting: The baudrate of the device, can be 1200, 2400, 4800, 9600, 14400, 19200,
        28800, 38400, 57600, 115200, 230400
        :param timeout_setting: Timeout for the device
        :return: None
        """
        self.mw_source.baudrate = baudrate_setting
        self.mw_source.timeout = timeout_setting
        self.mw_source.port = port_num
        self.mw_source.open()

    def get_status(self):
        """
        Get all status and setting of the device
        :return: NOne
        """
        self.mw_source.write(b'?')
        self.read_all()

    def switch(self, state=True):
        """
        Turn on/off the Microwave Source
        :param state: State of the source, True for On, False for Off
        :return: None
        """
        if state:
            self.mw_source.write(b'E1')
            time.sleep(0.02)
        else:
            self.mw_source.write(b'E0')

    def set_power(self, power):
        """
        Set the Microwave Source Power
        :param power: The Output Power of the device, in dBm unit. Range from -50.0 dBm to +10 dBm
        :return: None
        """
        if power < -50.0:
            print('Warning: Power too Low!')
            return
        if power > 10.0:
            print('Warning: Power too High!')
            return
        self.mw_source.write(str.encode('W' + str(power)))

    def set_freq(self, freq):
        """
        Set the Microwave Source Frequency
        :param freq: The Frequency of the output Microwave, in MHz unit. Range from 12.5 MHz to 6,400.0 MHz
        :return:
        """
        if freq < 12.5:
            print('Warning: Frequency too Low!')
            return
        if freq > 6400.0:
            print('Warning: Frequency too High!')
            return
        self.mw_source.write(str.encode('f' + str(freq)))

    def set_sweep(self, start_freq, stop_freq, step, step_time):
        """
        Set the sweep parameters
        :param start_freq: Start Frequency of the output Microwave, in MHz unit. Range from 12.5 MHz to 6,400.0 MHz
        :param stop_freq: Start Frequency of the output Microwave, in MHz unit. Range from 12.5 MHz to 6,400.0 MHz
        :param step: Step of the sweep Frequency, in MHz unit.
        :param step_time: Time of one Frequency in sweep, in ms unit. Range from 0.25 ms to 60,000 ms
        :return: None
        """
        if start_freq < 12.5:
            print('Warning: Start Frequency too low!')
            return
        if stop_freq > 6400.0:
            print('Warning: Stop Frequency too high!')
            return
        if start_freq >= stop_freq:
            print('Warning: Start Frequency is higher than Stop Frequency!')
            return
        if step > stop_freq - start_freq:
            print('Warning: Less than 1 step!')
            return
        if step_time < 0.25:
            print('Warning: Step time too short!')
            return
        if step_time > 60000.0:
            print('Warning: Step time too long!')
            return

        self.mw_source.write(str.encode('l' + str(start_freq)))
        self.mw_source.write(str.encode('u' + str(stop_freq)))
        self.mw_source.write(str.encode('s' + str(step)))
        self.mw_source.write(str.encode('t' + str(step_time)))

    def start_sweep(self):
        """
        Start Frequency Sweep
        :return: None
        """
        self.mw_source.write(b'g1')

    def stop_sweep(self):
        """
        Stop Frequency Sweep
        :return: None
        """
        self.mw_source.write(b'g0')

    def clean_up(self):
        """
        Close the COM port
        :return: None
        """
        self.mw_source.close()

    def read_all(self):
        """
        Print all the information get from the device, end when get all the data
        :return: None
        """
        while True:
            bytes_data = self.mw_source.readline()
            try:
                output(bytes_data)
            except ValueError:
                break


def output(bytes_data_raw):
    """
    Change the output bytes into string(encoding: utf-8).
    :raise ValueError: When meet timeout
    :param bytes_data_raw: The input data, in bytes type
    :return:
    """
    if bytes_data_raw == b'':
        raise ValueError("NA")
    bytes_new = bytes_data_raw.replace(b'\n', b'')
    print(bytes_new.decode('utf-8'))
