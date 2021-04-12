# coding=gbk
"""
This file is the functions for CoreTomorrow E70.4 4 channel controller

"""
import ctypes
import os
import sys
import time


class XMT():
    def __init__(self):

        dll = os.path.dirname(__file__) + '/DLL/XMT_DLL_USB.dll'  # Give the path of dll file
        path = os.path.dirname(__file__) + '/DLL'
        os.chdir(path)
        self.xmt_dll = ctypes.cdll.LoadLibrary(dll)

    def scan_devices(self):
        # Scan the devices before using it
        # Print the number of connected devices
        # Return the number of connected devices
        nmb_of_device = self.xmt_dll.ScanUsbDevice()
        print('%d device has connected.' % nmb_of_device)
        return nmb_of_device - 1

    def open_devices(self, nmb_of_device=0):
        # Open the device of nmb_of_device
        # If not open successfully, print 'Fail to open ...'
        # nmb_of_device start from 0
        if not self.xmt_dll.OpenUsbPython(ctypes.c_int(nmb_of_device)):
            print('Failed to open device %d.' % nmb_of_device)

    def close_devices(self, nmb_of_device=0):
        # Close the device of nmb_of_device
        # If not Close successfully, print 'Fail to open ...'
        # nmb_of_device start from 0
        if not self.xmt_dll.CloseUsbNumOfDevice(ctypes.c_int(nmb_of_device)):
            print('Failed to close device %d.' % nmb_of_device)

    def read_status(self, channel, nmb_of_device=0):
        # Read the status of the single channel
        # Return three values: Loop type, Signal Type, I/O type
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
        # Check if all the channel of device is close loop, digital and output
        # If every channel status is fine, nothing happens and return 0
        # Else, give a  warning and return 1
        for i in range(4):
            loop_status, signal_status, io_type = self.read_status(channel=(i + 1), nmb_of_device=num_of_device)
            if not i == 2:
                if not loop_status == 'C' and signal_status == 'D' and io_type == 'O':  # Check status
                    print('Please set the device status!')
                    return 0
            else:
                if not loop_status == 'O' and signal_status == 'D' and io_type == 'O':  # Check status
                    print('Please set the device status!')
                    return 0

        return 1

    def set_status(self, channel, nmb_of_device=0):
        # Set the status of the single channel
        # Set three values: Loop type, Signal Type, I/O type
        # The status will be set as Close Loop, Digital, Output
        command_b4 = 0  # Define command_b4(always 0, have no meaning)
        channel_num = channel - 1

        # The type of loop (Open loop or Close Loop)
        if channel == 3:
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_int(nmb_of_device),
                                                    ctypes.c_char(1),  # Address of controller(always 1)
                                                    ctypes.c_char(18),  # Command_b3, 18 for loop type
                                                    ctypes.c_char(command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char('O')
                                                    )
        else:
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_int(nmb_of_device),
                                                    ctypes.c_char(1),  # Address of controller(always 1)
                                                    ctypes.c_char(18),  # Command_b3, 18 for loop type
                                                    ctypes.c_char(command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char('C')
                                                    )

        # The type of signal (Digital or Analog)
        signal_type = self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_int(nmb_of_device),
                                                              ctypes.c_char(1),  # Address of controller(always 1)
                                                              ctypes.c_char(20),  # Command_b3, 20 for signal type
                                                              ctypes.c_char(command_b4),
                                                              ctypes.c_char(channel_num),
                                                              ctypes.c_char('D')
                                                              )

        # The type of I/O (Input or Output)
        io_type = self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_int(nmb_of_device),
                                                          ctypes.c_char(1),  # Address of controller(always 1)
                                                          ctypes.c_char(22),  # Command_b3, 22 for I/O type
                                                          ctypes.c_char(command_b4),
                                                          ctypes.c_char(channel_num),
                                                          ctypes.c_char('O')
                                                          )

    def set_all_status(self, num_of_device=0):
        # Set all the channel of device to close loop, digital and output
        for i in range(4):
            self.set_status(channel=(i + 1), nmb_of_device=num_of_device)

    def set_voltage(self, channel=3, voltage=150.0, num_of_device=0):
        # Set the voltage for single channel
        # Default voltage for channel 3 is 150V
        command_b4 = 0
        channel_nmm = channel - 1
        if channel_nmm == 2:
            if not voltage == 150.0:
                print('Channel 3 must be 150V.')
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
        # Read the position of Channel n
        # Channel 3 do not have location information
        # return the location of selected channel ()
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
            print('Channel 3 do not have location information, the Voltage is', voltage)
            return

        location = self.xmt_dll.XMT_COMMAND_ReadData(ctypes.c_int(num_of_device),
                                                     ctypes.c_char(1),  # Address of controller(always 1)
                                                     ctypes.c_char(6),  # Command_b3, 6 for return position
                                                     ctypes.c_char(command_b4),
                                                     ctypes.c_char(channel_num)
                                                     )
        return location

    def read_position_all(self):
        # Read the location of all 3 channels
        # Return an array of [x, y, z]
        location_x = self.read_position_single(channel=1)
        location_y = self.read_position_single(channel=2)
        location_z = self.read_position_single(channel=4)
        return [location_x, location_y, location_z]

    def move_position_single(self, channel, location=0.000, num_of_device=0):
        # Move the position for single channel
        # Channel 3 can not move location, must be 150V
        # The unit of position is um
        command_b4 = 0
        channel_num = channel - 1
        if channel_num == 2:
            print('Channel 3 must be 150V.')
            return 1
        self.xmt_dll.XMT_COMMAND_SinglePoint(ctypes.c_int(num_of_device),
                                             ctypes.c_char(1),  # Address of controller(always 1)
                                             ctypes.c_char(1),  # Command_b3, 1 for send position
                                             ctypes.c_char(command_b4),
                                             ctypes.c_char(channel_num),
                                             ctypes.c_double(location)  # Move to position
                                             )
        return 0

    def clear(self):
        # Move the position to [0,0,0]
        # Set Voltage of Channel 3 to 150V.
        self.set_voltage()
        self.move_position_single(channel=1)
        self.move_position_single(channel=2)
        self.move_position_single(channel=4)


if __name__ == '__main__':
    xmt = XMT()
    device = xmt.scan_devices()
    xmt.open_devices(nmb_of_device=device)
    xmt.check_all_status(num_of_device=device)
    xmt.move_position_single(channel=1, location=0.524621)
    xmt.move_position_single(channel=2, location=50.498746513)
    xmt.move_position_single(channel=4, location=30.14684135)
    time.sleep(0.1)
    old_location = xmt.read_position_all()
    print(old_location)
    xmt.clear()
    time.sleep(0.1)
    new_location = xmt.read_position_all()
    print(new_location)


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
