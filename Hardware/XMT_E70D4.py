# coding=gbk
"""
This file is the functions for CoreTomorrow E70.4 4 channel controller

"""
import ctypes
import os, sys, time
import numpy as np


class XMT:
    def __init__(self):

        dll = os.path.dirname(__file__) + '/DLL/XMT_DLL_USB.dll'  # Give the path of dll file
        path = os.path.dirname(__file__) + '/DLL'
        os.chdir(path)
        self.xmt_dll = ctypes.cdll.LoadLibrary(dll)

    def scan_devices(self):
        """
        Scan the devices before using it

        Print the number of connected devices

        Return the number of connected devices
        """

        nmb_of_device = self.xmt_dll.ScanUsbDevice()
        print('%d device has connected.' % nmb_of_device)
        return nmb_of_device - 1

    def open_devices(self, nmb_of_device=0):
        """
        Open the device of nmb_of_device

        If not open successfully, print 'Fail to open ...'

        nmb_of_device starts from 0

        Return 0 means fine

        Return 1 means fail to open the device
        """

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

    def set_voltage(self, channel=3, voltage=150.0, num_of_device=0):
        """
        Set the voltage for single channel

        Default voltage for channel 3 is 150V

        Return 0 means fine

        Return 1 means try to give a non-150V voltage to Channel 3
        """

        command_b4 = 0
        channel_nmm = channel - 1
        if channel_nmm == 2:
            if not voltage == 150.0:
                print('Warning: Channel 3 must be 150V!')
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

        Return 1 means try to return the location of channel 3 which only have constant 150 V Voltage
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

        Channel 3 can not move location, must be 150V

        The unit of position is um

        The default accuracy is 5nm, check the accuracy by default setting.

        Return 0 means good

        Return 1 means try to send location to channel 3

        Return 2 means input out of range
        """

        command_b4 = 0
        channel_num = channel - 1

        # The channel 3 need to be given a 150V constant voltage, not position
        if channel == 3:
            print('Warning: Can not send position to channel 3! Channel 3 must be 150V.')
            return 1

        # Check the input range
        if channel == 1 or channel == 2:
            if location > 100.0 or location < 0.0:
                print('Warning: Input out of Range! The movement for X/Y axis is out of range(0.0~100.0um).')
                return 2
        else:
            if location > 50.0 or location < 0.0:
                print('Warning: Input out of Range! The movement for Z axis is out of range(0.0~50.0um).')
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

        Set Voltage of Channel 3 to 150V

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

    def scanning_setting(self, channel, start_point, end_point, line_rate=4, num_of_device=0):
        """
        :param channel: channel of the scanning, can be 1,2,4
        :param start_point: the start of the scanning (um)
        :param end_point: the end of the scanning (um)
        :param line_rate: the scan rage for line, default 4
        :param num_of_device: 0
        :return: 0 means fine, 1 means scan size out of range, 2 means try to use channel 3 to scan
        """

        # command_b4 = 0
        # channel_num = channel - 1
        #
        # # Set the scan limit based on channel
        # min_limit = 0.0
        # if channel == 4:
        #     max_limit = 50.0
        # else:
        #     max_limit = 100.0
        #
        # if channel == 3:
        #     print('Warning: The channel 3 can not scan!')
        #     return 2
        #
        # # Check the scan size
        # if start_point < min_limit or end_point > max_limit:
        #     print('Warning: Scan size out of range!')
        #     return 1
        pass

    def scanning_single_line(self, channel, start_point, end_point, accuracy=0.005, line_rate=4, num_of_device=0):
        command_b4 = 0
        channel_num = channel - 1

        if channel == 3:
            print('Warning: Channel 3 can not scan!')
            return 1

        pp_value = end_point - start_point
        offset = (start_point + end_point) / 2

        self.xmt_dll.XMT_COMMAND_WaveSetHighSingle(ctypes.c_int(num_of_device),
                                                   ctypes.c_char(1),  # Address of controller(always 1)
                                                   ctypes.c_char(12),  # Command_b3, 72 for start/stop scan
                                                   ctypes.c_char(command_b4),
                                                   ctypes.c_char(channel_num),
                                                   ctypes.c_char(ord('Z')),
                                                   ctypes.c_double(pp_value),
                                                   ctypes.c_double(line_rate),
                                                   ctypes.c_double(offset)
                                                   )

        time.sleep(9 / (10 * line_rate))  # Wait for 0.9 T

        # If move to the target position, stop scanning
        self.xmt_dll.XMT_COMMAND_WaveSetHighSingleStop(ctypes.c_int(num_of_device),
                                                       ctypes.c_char(1),  # Address of controller(always 1)
                                                       ctypes.c_char(14),  # Command_b3, 72 for start/stop scan
                                                       ctypes.c_char(command_b4)
                                                       )

        # Move back to the start point
        self.move_position_single(channel=channel, location=start_point, accuracy=accuracy, num_of_device=num_of_device)
        return 0

    '''
    def scanning_setting(self, channel, start_point, end_point, line_rate=4, num_of_device=0):
        """
        Scan one line

        48 points. First 40 define a line, last 8 stay at endpoint to make sure it reach the set point

        Unit is um and ms

        The maximum for channel 1 and 2 is 100um, for channel 4 is 50um

        Return 0 means fine

        Return 1 means scan size out of range

        Return 2 means try to use channel 3 to scan
        """

        command_b4 = 0
        channel_num = channel - 1

        # Set the scan limit based on channel
        min_limit = 0.0
        if channel == 4:
            max_limit = 50.0
        else:
            max_limit = 100.0

        if channel == 3:
            print('Warning: The channel 3 can not scan!')
            return 2

        # Check the scan size
        if start_point < min_limit or end_point > max_limit:
            print('Warning: Scan size out of range!')
            return 1

        # Create the wave form array
        wave_temp = np.linspace(start_point, end_point, 40)
        wave = wave_temp.tolist()
        for i in range(8):
            wave.append(end_point)

        # Define the 'point' of the array
        type_def = ctypes.c_float * 48
        waveform = type_def(*wave)

        # Send the wave form data to controller
        self.xmt_dll.XMT_COMMAND_SaveDataArrToMCU(ctypes.c_int(num_of_device),
                                                  ctypes.c_char(1),  # Address of controller(always 1)
                                                  ctypes.c_char(70),  # Command_b3, 70 for send custom wave form data
                                                  ctypes.c_char(command_b4),
                                                  ctypes.c_char(channel_num),
                                                  ctypes.c_char(0),  # 0 for forward, 1 for back
                                                  ctypes.byref(waveform),  # The self_defined wave form
                                                  ctypes.c_char(47),  # Send 48 points
                                                  ctypes.c_float(max_limit),  # The limit for the maximum input
                                                  ctypes.c_float(min_limit)  # The limit for the minimum input
                                                  )

        # Define the scanning time for single line
        time_interval = 1000.0 / (line_rate * 48.0)

        # Send the time setting to controller
        self.xmt_dll.XMT_COMMAND_SetMCUSendDataTimer(ctypes.c_int(num_of_device),
                                                     ctypes.c_char(1),  # Address of controller(always 1)
                                                     ctypes.c_char(71),  # Command_b3, 71 for send time setting
                                                     ctypes.c_char(command_b4),
                                                     ctypes.c_char(channel_num),
                                                     ctypes.c_float(time_interval)  # The time interval between 2
                                                     # locations
                                                     )
        return 0
    '''

    '''
    def scanning_single_line(self, channel, start_point, end_point, accuracy=0.005, line_rate=4, num_of_device=0):
        """
        Do a single line scan for channel

        Return to the start point when finish a single line scanning

        'S' for start, 'T' for stop, 'P' for pause

        Return 0 means fine

        Return 1 means try to scan on channel 3
        """

        command_b4 = 0
        channel_num = channel - 1

        if channel == 3:
            print('Warning: Channel 3 can not scan!')
            return 1

        self.xmt_dll.XMT_COMMAND_SetMCU_BeginSend(ctypes.c_int(num_of_device),
                                                  ctypes.c_char(1),  # Address of controller(always 1)
                                                  ctypes.c_char(72),  # Command_b3, 72 for start/stop scan
                                                  ctypes.c_char(command_b4),
                                                  ctypes.c_char(channel_num),
                                                  ctypes.c_char(ord('S'))  # Start to scan
                                                  )

        time.sleep(9 / (10 * line_rate))  # Wait for 0.9 T

        # If move to the target position, stop scanning
        self.xmt_dll.XMT_COMMAND_SetMCU_BeginSend(ctypes.c_int(num_of_device),
                                                  ctypes.c_char(1),  # Address of controller(always 1)
                                                  ctypes.c_char(72),  # Command_b3, 72 for start/stop scan
                                                  ctypes.c_char(command_b4),
                                                  ctypes.c_char(channel_num),
                                                  ctypes.c_char(ord('T'))  # Stop scan
                                                  )

        # Move back to the start point
        self.move_position_single(channel=channel, location=start_point, accuracy=accuracy, num_of_device=num_of_device)
        return 0
    '''

    '''
    def scanning_single_line(self, channel, start_point, end_point, accuracy=0.005, num_of_device=0):
        """
        Do a single line scan for channel

        Return to the start point when finish a single line scanning

        'S' for start, 'T' for stop, 'P' for pause

        Return 0 means fine

        Return 1 means try to scan on channel 3
        """

        command_b4 = 0
        channel_num = channel - 1

        if channel == 3:
            print('Warning: Channel 3 can not scan!')
            return 1

        self.xmt_dll.XMT_COMMAND_SetMCU_BeginSend(ctypes.c_int(num_of_device),
                                                  ctypes.c_char(1),  # Address of controller(always 1)
                                                  ctypes.c_char(72),  # Command_b3, 72 for start/stop scan
                                                  ctypes.c_char(command_b4),
                                                  ctypes.c_char(channel_num),
                                                  ctypes.c_char(ord('S'))  # Start to scan
                                                  )

        # Check if the stage move to the target position
        while True:
            temp_location = self.read_position_single(channel=channel)  # Get current location from the build-in sensor
            if abs(end_point - temp_location) < accuracy:  # Check if the current location satisfy the accuracy
                break  # If satisfy the requirement, end the function
            time.sleep(0.002)  # If it doesn't satisfy the requirement, wait for 2ms and check again

        # If move to the target position, stop scanning
        self.xmt_dll.XMT_COMMAND_SetMCU_BeginSend(ctypes.c_int(num_of_device),
                                                  ctypes.c_char(1),  # Address of controller(always 1)
                                                  ctypes.c_char(72),  # Command_b3, 72 for start/stop scan
                                                  ctypes.c_char(command_b4),
                                                  ctypes.c_char(channel_num),
                                                  ctypes.c_char(ord('T'))  # Stop scan
                                                  )

        # Move back to the start point
        self.move_position_single(channel=channel, location=start_point, accuracy=accuracy, num_of_device=num_of_device)
        return 0
    '''

    '''
    def scan_set_test(self, waveforminput):
        a = ctypes.c_float * 5
        waveform = a(*waveforminput)
        self.xmt_dll.XMT_COMMAND_SaveDataArrToMCU(ctypes.c_int(0),
                                                  ctypes.c_char(1),
                                                  ctypes.c_char(70),  # command b3
                                                  ctypes.c_char(0),  # command b4
                                                  ctypes.c_char(3),  # channel
                                                  ctypes.c_char(0),  # f/B
                                                  ctypes.byref(waveform),
                                                  ctypes.c_char(5),
                                                  ctypes.c_float(50.0),
                                                  ctypes.c_float(0.0)
                                                  )
        self.xmt_dll.XMT_COMMAND_SetMCUSendDataTimer(ctypes.c_int(0),
                                                     ctypes.c_char(1),
                                                     ctypes.c_char(71),
                                                     ctypes.c_char(0),
                                                     ctypes.c_char(3),
                                                     ctypes.c_float(20)
                                                     )

    def scan_state_test(self, state):
        self.xmt_dll.XMT_COMMAND_SetMCU_BeginSend(ctypes.c_int(0),
                                                  ctypes.c_char(1),
                                                  ctypes.c_char(72),
                                                  ctypes.c_char(0),
                                                  ctypes.c_char(3),
                                                  ctypes.c_char(state)
                                                  )
        for i in range(100):
            location = self.read_position_single(channel=4)
            print('test time', i + 1, ':', location)
            time.sleep(0.001)
    '''


if __name__ == '__main__':
    xmt = XMT()
    device = xmt.scan_devices()
    xmt.open_devices(nmb_of_device=device)
    xmt.check_all_status(num_of_device=device)

    '''
    xmt.send()
    time.sleep(1)
    xmt.sendstop()
    time.sleep(1)
    new_location = xmt.read_position_all()
    print(new_location)
    '''

'''
    xmt.move_position_all(location=(80, 80, 50))
    old_location = xmt.read_position_all()
    print(old_location)
    time.sleep(2)
    xmt.clear()
    new_location = xmt.read_position_all()
    print(new_location)
'''

'''
    xmt.move_position_single(channel=1, location=0.524621)
    xmt.move_position_single(channel=2, location=50.498746513)
    xmt.move_position_single(channel=4, location=30.14684135)
    time.sleep(0.005)
    position1 = xmt.read_position(channel=1)
    print('X = ', position1)
    position2 = xmt.read_position(channel=2)
    print('Y = ', position2)
    position3 = xmt.read_position(channel=4)
    print('Z = ', position3)
'''
