# coding=gbk
"""
This file is the functions for CoreTomorrow E70.4 4 channel controller

"""
import ctypes
import os
import time
import numpy as np


class XMT:
    def __init__(self):
        origin_path = os.getcwd()
        dll = os.path.dirname(__file__) + '/DLL_Ser/XMT_DLL_SER.dll'  # Give the path of dll file
        path = os.path.dirname(__file__) + '/DLL_Ser'
        os.chdir(path)
        self.xmt_dll = ctypes.cdll.LoadLibrary(dll)
        os.chdir(origin_path)

    def scan_devices(self, port_num='COM3'):
        """

        :param port_num: A string represents the COM port of the Controller, e.g. 'COM3'
        :return: 0 means connect to the device

        The EntryXMT() Function will return 3 when the assigned COM port has device.
        """

        status = self.xmt_dll.EntryXMT(ctypes.c_wchar_p(port_num), ctypes.c_long(9600), ctypes.c_int(0)) - 3
        return status

    def read_voltage_test(self, channel_num=2):

        command_b4 = 0
        self.xmt_dll.XMT_COMMAND_ReadData.restype = ctypes.c_double
        temp_data = self.xmt_dll.XMT_COMMAND_ReadData(ctypes.c_char(1),  # Address of controller(always 1)
                                                      ctypes.c_char(5),  # Command_b3, 33 for voltage limit
                                                      ctypes.c_char(0),
                                                      ctypes.c_char(channel_num)
                                                      )
        print('The voltage is:', temp_data)

    def open_devices(self, port_num='COM3', baud_rate=19200):
        """
        Open the device of given port_num and baud_rate

        If not open successfully, print 'Fail to open ...'

        nmb_of_device starts from 0

        Return 0 means fine

        Return 1 means fail to open the device
        """
        self.xmt_dll.EntryXMT(port_num, baud_rate, 'NULL')

        if not self.xmt_dll.OpenUsbPython(ctypes.c_int(nmb_of_device)):
            print('Warning: Failed to open device %d!' % nmb_of_device)
            return 1
        return 0

    def close_devices(self, nmb_of_device=0):
        """
        Close the device of nmb_of_device

        If not Close successfully, print 'Fail to open ...'

        nmb_of_device start from 0
        """

        if not self.xmt_dll.CloseUsbNumOfDevice(ctypes.c_int(nmb_of_device)):
            print('Warning: Failed to close device %d!' % nmb_of_device)

    def read_status(self, channel, nmb_of_device=0):
        """
        Read the status of the single channel

        Return three values: Loop type, Signal Type, I/O type
        """

        command_b4 = 0  # Define command_b4(always 0, have no meaning)
        channel_num = channel - 1

        # The type of loop (Open loop or Close Loop)
        loop_type = self.xmt_dll.XMT_COMMAND_Assist_ReadFlag(ctypes.c_int(nmb_of_device),
                                                             ctypes.c_char(1),  # Address of controller(always 1)
                                                             ctypes.c_char(19),  # Command_b3, 19 for loop type
                                                             ctypes.c_char(command_b4),
                                                             ctypes.c_char(channel_num)
                                                             )
        loop_type = chr(loop_type)  # Change the return value into unsigned_char

        # The type of signal (Digital or Analog)
        signal_type = self.xmt_dll.XMT_COMMAND_Assist_ReadFlag(ctypes.c_int(nmb_of_device),
                                                               ctypes.c_char(1),  # Address of controller(always 1)
                                                               ctypes.c_char(21),  # Command_b3, 21 for signal type
                                                               ctypes.c_char(command_b4),
                                                               ctypes.c_char(channel_num)
                                                               )
        signal_type = chr(signal_type)  # Change the return value into unsigned_char

        # The type of I/O (Input or Output)
        io_type = self.xmt_dll.XMT_COMMAND_Assist_ReadFlag(ctypes.c_int(nmb_of_device),
                                                           ctypes.c_char(1),  # Address of controller(always 1)
                                                           ctypes.c_char(23),  # Command_b3, 23 for I/O type
                                                           ctypes.c_char(command_b4),
                                                           ctypes.c_char(channel_num)
                                                           )
        io_type = chr(io_type)  # Change the return value into unsigned_char
        return loop_type, signal_type, io_type

    def check_all_status(self, num_of_device=0):
        """
        Check if all the channel of device is close loop, digital and output

        Return 0 means fine

        Return 1 means something is wrong
        """

        for i in range(4):
            loop_status, signal_status, io_type = self.read_status(channel=(i + 1), nmb_of_device=num_of_device)
            if not i == 2:  # Check the status of channel 1,2,4
                if not loop_status == 'C' and signal_status == 'D' and io_type == 'O':  # Check status
                    print('Warning: The status of Channel 1/2/4 is abnormal! Please set the device status!')
                    return 1
            else:  # Check the status of channel 3
                if not loop_status == 'O' and signal_status == 'D' and io_type == 'O':  # Check status
                    print('Warning: The status of Channel 3 is abnormal! Please set the device status!')
                    return 1

        return 0

    def set_status(self, channel, nmb_of_device=0):
        """
        Set the status of the single channel

        Set three values: Loop type, Signal Type, I/O type

        The status will be set as Close Loop, Digital, Output
        """

        command_b4 = 0  # Define command_b4(always 0, have no meaning)
        channel_num = channel - 1

        # The type of loop (Open loop or Close Loop)
        if channel == 3:
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_int(nmb_of_device),
                                                    ctypes.c_char(1),  # Address of controller(always 1)
                                                    ctypes.c_char(18),  # Command_b3, 18 for loop type
                                                    ctypes.c_char(command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char(ord('O'))
                                                    )
        else:
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_int(nmb_of_device),
                                                    ctypes.c_char(1),  # Address of controller(always 1)
                                                    ctypes.c_char(18),  # Command_b3, 18 for loop type
                                                    ctypes.c_char(command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char(ord('C'))
                                                    )

            # The type of signal (Digital or Analog)
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_int(nmb_of_device),
                                                    ctypes.c_char(1),  # Address of controller(always 1)
                                                    ctypes.c_char(20),  # Command_b3, 20 for signal type
                                                    ctypes.c_char(command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char(ord('D'))
                                                    )

            # The type of I/O (Input or Output)
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_int(nmb_of_device),
                                                    ctypes.c_char(1),  # Address of controller(always 1)
                                                    ctypes.c_char(22),  # Command_b3, 22 for I/O type
                                                    ctypes.c_char(command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char(ord('O'))
                                                    )

    def set_all_status(self, num_of_device=0):
        """
        Set all the channel of device to close loop, digital and output
        """

        for i in range(4):
            self.set_status(channel=(i + 1), nmb_of_device=num_of_device)

    def set_voltage(self, channel=3, voltage=100.0, num_of_device=0):
        """
        Set the voltage for single channel

        Default voltage for channel 3 is 100V

        Return 0 means fine

        Return 1 means try to give a non-100V voltage to Channel 3
        """

        command_b4 = 0
        channel_nmm = channel - 1
        if channel_nmm == 2:
            if not voltage == 100.0:
                print('Warning: Channel 3 must be 100V!')
                return 1

        self.xmt_dll.XMT_COMMAND_SinglePoint(ctypes.c_int(num_of_device),
                                             ctypes.c_char(1),  # Address of controller(always 1)
                                             ctypes.c_char(0),  # Command_b3, 0 for send voltage
                                             ctypes.c_char(command_b4),
                                             ctypes.c_char(channel_nmm),
                                             ctypes.c_double(voltage)  # Move to position
                                             )
        return 0

    def read_position_single(self, channel, num_of_device=0):
        """
        Read the position of Channel n

        Channel 3 do not have location information

        Return the location of selected channel ()

        Return 1 means try to return the location of channel 3 which only have constant 100 V Voltage
        """

        command_b4 = 0  # Define command_b4(always 0, have no meaning)
        channel_num = channel - 1
        self.xmt_dll.XMT_COMMAND_ReadData.restype = ctypes.c_double  # Reform the return value into c_double
        if channel_num == 2:
            voltage = self.xmt_dll.XMT_COMMAND_ReadData(ctypes.c_int(num_of_device),
                                                        ctypes.c_char(1),  # Address of controller(always 1)
                                                        ctypes.c_char(5),  # Command_b3, 5 for return voltage
                                                        ctypes.c_char(command_b4),
                                                        ctypes.c_char(channel_num)
                                                        )
            print('Warning: Channel 3 do not have location information! The Voltage is', voltage)
            return 1

        location = self.xmt_dll.XMT_COMMAND_ReadData(ctypes.c_int(num_of_device),
                                                     ctypes.c_char(1),  # Address of controller(always 1)
                                                     ctypes.c_char(6),  # Command_b3, 6 for return position
                                                     ctypes.c_char(command_b4),
                                                     ctypes.c_char(channel_num)
                                                     )
        return location

    def read_position_all(self):
        """
        Read the location of all 3 channels

        Return an array of [x, y, z]
        """

        location_x = self.read_position_single(channel=1)
        location_y = self.read_position_single(channel=2)
        location_z = self.read_position_single(channel=4)
        return location_x, location_y, location_z

    def move_position_single(self, channel, location=0.000, accuracy=0.005, check=True, num_of_device=0):
        """
        Move the position for single channel

        Channel 3 can not move location, must be 100V

        The unit of position is um

        The default accuracy is 5nm, check the accuracy by default setting.

        Return 0 means good

        Return 1 means try to send location to channel 3

        Return 2 means input out of range
        """

        command_b4 = 0
        channel_num = channel - 1

        # The channel 3 need to be given a 100V constant voltage, not position
        if channel == 3:
            print('Warning: Can not send position to channel 3! Channel 3 must be 100V.')
            return 1

        # Check the input range
        if channel == 1 or channel == 2:
            if location > 65.0 or location < 0.0:
                print('Warning: Input out of Range! The movement for X/Y axis is out of range(0.0~65.0um).')
                return 2
        else:
            if location > 35.0 or location < 0.0:
                print('Warning: Input out of Range! The movement for Z axis is out of range(0.0~35.0um).')
                return 2

        self.xmt_dll.XMT_COMMAND_SinglePoint(ctypes.c_int(num_of_device),
                                             ctypes.c_char(1),  # Address of controller(always 1)
                                             ctypes.c_char(1),  # Command_b3, 1 for send position
                                             ctypes.c_char(command_b4),
                                             ctypes.c_char(channel_num),
                                             ctypes.c_double(location)  # Move to position
                                             )
        while check:  # Check if the stage move to the target position
            temp_location = self.read_position_single(channel=channel)  # Get current location from the build-in sensor
            if abs(location - temp_location) < accuracy:  # Check if the current location satisfy the accuracy
                return 0  # If satisfy the requirement, end the function
            time.sleep(0.002)  # If it doesn't satisfy the requirement, wait for 2ms and check again
        return 0

    def clear(self, num_of_device=0):
        """
        Move the position to [0,0,0]

        Set Voltage of Channel 3 to 100V

        Wait for 0.1s

        Return 0 means fine
        """

        self.set_voltage(num_of_device=num_of_device)
        self.move_position_single(channel=1, num_of_device=num_of_device, check=False)
        self.move_position_single(channel=2, num_of_device=num_of_device, check=False)
        self.move_position_single(channel=4, num_of_device=num_of_device, check=False)

        time.sleep(0.1)

        return 0

    def move_position_all(self, location=(0.000, 0.000, 0.000), accuracy=0.005, check=True, num_of_device=0):
        """
        Move the stage to a new position(3 axis)

        The input should be in the form of (X, Y, Z)

        The input can not out of moving range

        Return 0 means fine

        Return -1 means input form is wrong

        Return 1 means input out of range
        """

        # Check if the input position data is in right form
        if not np.size(location) == 3:
            print('Warning: The form of the location data is wrong!')
            return -1

        # Check if the input is inside the moving range
        status_temp = 0
        status_temp += self.move_position_single(channel=1, location=location[0], check=False,
                                                 num_of_device=num_of_device)
        status_temp += self.move_position_single(channel=2, location=location[1], check=False,
                                                 num_of_device=num_of_device)
        status_temp += self.move_position_single(channel=4, location=location[2], check=False,
                                                 num_of_device=num_of_device)
        if not status_temp == 0:
            return 1

        # Check if the stage move to the target position
        while check:
            temp_location = self.read_position_all()  # Get current location from the build-in sensor
            for i in range(3):  # Check if all 3 channels move to target position
                if abs(location[i] - temp_location[i]) < accuracy:
                    if i == 2:
                        return 0  # When i == 2, all 3 channels have been tested and met the requirements
                    continue
                else:
                    break  # One of all 3 channels hasn't move to target, need to wait for more time
            time.sleep(0.002)  # If it doesn't satisfy the requirement, wait for 2ms and check again
        return 0

    def generating_scan_array(self, channel, start_point, end_point, line_rate=4):
        """
        This methods will generate the list that used for movement of the piezo_stage
        :param channel: The channel for scan. Used for prevent out of limit
        :param start_point: The start point of the movement (um)
        :param end_point: The end point of the movement (um)
        :param line_rate: The line rate of the scanning (Hz)
        :return: list for move forward, list for move back.
        Return 1 means scan size out of range.
        Return 2 means try to use channel 3 to scan.
        """
        # Set the scan limit based on channel
        min_limit = 0.0
        if channel == 4:
            max_limit = 35.0
        else:
            max_limit = 65.0

        if channel == 3:
            print('Warning: The channel 3 can not scan!')
            return 2

        # Check the scan size
        if start_point < min_limit or end_point > max_limit:
            print('Warning: Scan size out of range!')
            return 1

        # Create the wave form
        move_coefficient = int(7500 / line_rate)
        hold_coefficient = int(move_coefficient / 4)
        wave_forward_move = np.linspace(start_point, end_point, move_coefficient)
        wave_forward_hold = np.ones(hold_coefficient) * end_point
        wave_back_move = np.linspace(end_point, start_point, move_coefficient)
        wave_back_hold = np.ones(hold_coefficient) * start_point
        wave_forward = list(np.append(wave_forward_move, wave_forward_hold))
        wave_back = list(np.append(wave_back_move, wave_back_hold))
        return wave_forward, wave_back

    def scanning_single_line(self, channel, waveform, num_of_device=0):
        """
        This methods do the single line scanning based on the given waveform
        :param channel: The Channel used to scanning, 1, 2, 4
        :param waveform: The self_defined waveform for control piezo stage movement
        :param num_of_device: The number of the device( 0 for default)
        :return: Return 1 means try to scan on channel 3
        """
        # Check the channel number
        if channel == 3:
            print('Warning: Channel 3 can not scan!')
            return 1

        # Do the scanning
        for points in waveform:
            self.move_position_single(channel=channel, location=points, check=False, num_of_device=num_of_device)


if __name__ == '__main__':
    xmt = XMT()
    device = xmt.scan_devices()
    print(device)
    xmt.read_voltage_test()


    print(xmt.xmt_dll.CloseSer())
    # xmt.open_devices(nmb_of_device=device)
    # xmt.check_all_status(num_of_device=device)
