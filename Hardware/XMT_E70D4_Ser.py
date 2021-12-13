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
        # Load dll
        os.chdir(path)
        self.xmt_dll = ctypes.cdll.LoadLibrary(dll)
        os.chdir(origin_path)
        # Define command_b4(always 0) and address(always)
        self.command_b4 = 0
        self.address = 1

    def scan_devices(self, port_num='COM3'):
        """
        Connect to the device on given COM port with 9600 baud rate.

        :param port_num: string, device COM port. e.g.'COM3'
        :return: int, 0 for connect to device, else return -3.
        """
        # Define return data type
        self.xmt_dll.EntryXMT.restype = ctypes.c_int
        # Init the COM port
        status = self.xmt_dll.EntryXMT(ctypes.c_wchar_p(port_num),
                                       ctypes.c_long(9600),
                                       ctypes.c_int(0)
                                       ) - 3
        return status

    '''
    def open_devices(self, port_num='COM3', baud_rate=115200):
        """
        Change the baud rate to setting.(default: 115200)

        :param port_num: string, device COM port. e.g.'COM3'
        :param baud_rate: int, communicate baud rate(2400*n). default: 115200
        :return: bool, 0 for success.
        """
        # Init the COM port
        self.scan_devices(port_num=port_num)
        # Define return data type
        self.xmt_dll.setupdcb_BaudRate.restype = ctypes.c_bool

        # Set the Baud rate for MCU
        self.xmt_dll.XMT_COMMAND_SetMCUComBit(ctypes.c_char(self.address),
                                              ctypes.c_char(63),  # Command_b3, 63 for Baud rate
                                              ctypes.c_char(self.command_b4),
                                              ctypes.c_char(ord('F'))
                                              )
        # 'A'9600 'B'19200  'C'38400 'D'57600 'E'76800 'F'115200 'G'128000 'H'230400 'I'256000
        # Set the Baud rate for port
        state = self.xmt_dll.setupdcb_BaudRate(ctypes.c_int(baud_rate))
        if state:
            return 0
        else:
            return 1
        '''

    def open_devices(self, port_num='COM3', baud_rate=115200):
        return 0

    def close_devices(self, port_num='COM3'):
        """
        Reset the port baud rate to 9600 and close the port
        :param port_num: string, device COM port. e.g.'COM3'
        :return: None
        """
        # Define return data type
        self.xmt_dll.setupdcb_BaudRate.restype = ctypes.c_bool
        self.xmt_dll.CloseSer.restype = ctypes.c_bool
        # Set the baud rate of MCU to 9600
        self.xmt_dll.XMT_COMMAND_SetMCUComBit(ctypes.c_char(self.address),
                                              ctypes.c_char(63),  # Command_b3, 63 for Baud rate
                                              ctypes.c_char(self.command_b4),
                                              ctypes.c_char(ord('A'))
                                              )
        # 'A'9600 'B'19200  'C'38400 'D'57600 'E'76800 'F'115200 'G'128000 'H'230400 'I'256000
        # Set the baud rate of port to 9600
        state_1 = self.xmt_dll.setupdcb_BaudRate(ctypes.c_int(9600))
        # Close port and clear port
        state_2 = self.xmt_dll.CloseSer()
        self.xmt_dll.ClearSer()

    def read_status(self, channel, port_num='COM3'):
        """
        Read the status of the single channel
        :param channel: int, channel num
        :param port_num: string, device COM port. e.g.'COM3'
        :return: (char, char, char), Loop type, Signal Type, I/O type
        """
        channel_num = channel - 1
        # Define return data type
        self.xmt_dll.XMT_COMMAND_Assist_ReadFlag.restype = ctypes.c_char

        # The type of loop (Open loop or Close Loop)
        loop_type = self.xmt_dll.XMT_COMMAND_Assist_ReadFlag(ctypes.c_char(self.address),
                                                             ctypes.c_char(19),  # Command_b3, 19 for loop type
                                                             ctypes.c_char(self.command_b4),
                                                             ctypes.c_char(channel_num)
                                                             )

        # The type of signal (Digital or Analog)
        signal_type = self.xmt_dll.XMT_COMMAND_Assist_ReadFlag(ctypes.c_char(self.address),
                                                               ctypes.c_char(21),  # Command_b3, 21 for signal type
                                                               ctypes.c_char(self.command_b4),
                                                               ctypes.c_char(channel_num)
                                                               )

        # The type of I/O (Input or Output)
        io_type = self.xmt_dll.XMT_COMMAND_Assist_ReadFlag(ctypes.c_char(self.address),
                                                           ctypes.c_char(23),  # Command_b3, 23 for I/O type
                                                           ctypes.c_char(self.command_b4),
                                                           ctypes.c_char(channel_num)
                                                           )

        return loop_type, signal_type, io_type

    def check_all_status(self, port_num='COM3'):
        """
        Check if all the channel of device is close loop, digital and output
        :param port_num: string, device COM port. e.g.'COM3'
        :return: int, 0 means fine, 1 means something is wrong
        """
        for i in range(4):
            loop_status, signal_status, io_type = self.read_status(channel=(i + 1), port_num='COM3')
            if not i == 2:  # Check the status of channel 1,2,4
                if not loop_status == 'C' and signal_status == 'D' and io_type == 'O':  # Check status
                    print('Warning: The status of Channel 1/2/4 is abnormal! Please set the device status!')
                    return 1
            else:  # Check the status of channel 3
                if not loop_status == 'O' and signal_status == 'D' and io_type == 'O':  # Check status
                    print('Warning: The status of Channel 3 is abnormal! Please set the device status!')
                    return 1

        return 0

    def set_status(self, channel, port_num='COM3'):
        """
        Set the status of the single channel.
        Set three values: Loop type, Signal Type, I/O type.
        The status will be set as Close Loop, Digital, Output.
        :param channel: int, channel num
        :param port_num: string, device COM port. e.g.'COM3'
        :return: None
        """
        channel_num = channel - 1

        # The type of loop (Open loop or Close Loop)
        if channel == 3:
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_char(self.address),
                                                    ctypes.c_char(18),  # Command_b3, 18 for loop type
                                                    ctypes.c_char(self.command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char(ord('O'))
                                                    )
        else:
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_char(self.address),
                                                    ctypes.c_char(18),  # Command_b3, 18 for loop type
                                                    ctypes.c_char(self.command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char(ord('C'))
                                                    )

            # The type of signal (Digital or Analog)
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_char(self.address),
                                                    ctypes.c_char(20),  # Command_b3, 20 for signal type
                                                    ctypes.c_char(self.command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char(ord('D'))
                                                    )

            # The type of I/O (Input or Output)
            self.xmt_dll.XMT_COMMAND_Assist_SetFlag(ctypes.c_char(self.address),
                                                    ctypes.c_char(22),  # Command_b3, 22 for I/O type
                                                    ctypes.c_char(self.command_b4),
                                                    ctypes.c_char(channel_num),
                                                    ctypes.c_char(ord('O'))
                                                    )

    def set_all_status(self, port_num='COM3'):
        """
        Set all the channel of device to close loop, digital and output.
        :param port_num: string, device COM port. e.g.'COM3'
        :return: None
        """
        for i in range(4):
            self.set_status(channel=(i + 1), port_num='COM3')

    def set_voltage(self, channel=3, voltage=100.0, port_num='COM3'):
        """
        Set the voltage for single channel.(Default voltage for channel 3 is 100V)
        :param channel: int, channel num
        :param voltage: double, voltage in V
        :param port_num: string, device COM port. e.g.'COM3'
        :return: int, 0 means fine, 1 means try to give a non-100V voltage to Channel 3.
        """
        channel_nmm = channel - 1

        if channel_nmm == 2:
            if not voltage == 100.0:
                print('Warning: Channel 3 must be 100V!')
                return 1

        self.xmt_dll.XMT_COMMAND_SinglePoint(ctypes.c_char(self.address),
                                             ctypes.c_char(0),  # Command_b3, 0 for send voltage
                                             ctypes.c_char(self.command_b4),
                                             ctypes.c_char(channel_nmm),
                                             ctypes.c_double(voltage)  # Set voltage
                                             )
        return 0

    def read_position_single(self, channel, port_num='COM3'):
        """
        Read the position of channel.
        Return 1 means try to return the location of channel 3 which only have constant 100V Voltage.
        :param channel: int, channel num
        :param port_num: string, device COM port. e.g.'COM3'
        :return: double, location of selected channel.
        """
        channel_num = channel - 1

        # Define return data type
        self.xmt_dll.XMT_COMMAND_ReadData.restype = ctypes.c_double

        if channel_num == 2:
            voltage = self.xmt_dll.XMT_COMMAND_ReadData(ctypes.c_char(self.address),
                                                        ctypes.c_char(5),  # Command_b3, 5 for return voltage
                                                        ctypes.c_char(self.command_b4),
                                                        ctypes.c_char(channel_num)
                                                        )
            print('Warning: Channel 3 do not have location information! The Voltage is', voltage)
            return 1

        location = self.xmt_dll.XMT_COMMAND_ReadData(ctypes.c_char(self.address),
                                                     ctypes.c_char(6),  # Command_b3, 6 for return position
                                                     ctypes.c_char(self.command_b4),
                                                     ctypes.c_char(channel_num)
                                                     )
        return location

    def read_position_all(self, port_num='COM3'):
        """
        Read the location of all 3 channels
        :param port_num: tring, device COM port. e.g.'COM3'
        :return: array, [x, y, z]
        """
        location_x = self.read_position_single(channel=1)
        location_y = self.read_position_single(channel=2)
        location_z = self.read_position_single(channel=4)
        return location_x, location_y, location_z

    def move_position_single(self, channel, location=0.000, accuracy=0.005, check=True, port_num='COM3'):
        """
        Move the position(um) for single channel. The default accuracy is 5 nm.
        :param channel: int, channel num
        :param location: double, target location in um
        :param accuracy: double, location accuracy in um
        :param check: bool, decide weather check the accuracy
        :param port_num: string, device COM port. e.g.'COM3'
        :return: int, 0 means good, 1 means try to send location to channel 3, 2 means input out of range.
        """
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

        self.xmt_dll.XMT_COMMAND_SinglePoint(ctypes.c_char(self.address),
                                             ctypes.c_char(1),  # Command_b3, 1 for send position
                                             ctypes.c_char(self.command_b4),
                                             ctypes.c_char(channel_num),
                                             ctypes.c_double(location)  # Move to position
                                             )
        while check:  # Check if the stage move to the target position
            temp_location = self.read_position_single(channel=channel)  # Get current location from the build-in sensor
            if abs(location - temp_location) < accuracy:  # Check if the current location satisfy the accuracy
                return 0  # If satisfy the requirement, end the function
            time.sleep(0.002)  # If it doesn't satisfy the requirement, wait for 2ms and check again
        return 0

    def clear(self, port_num='COM3'):
        """
        Move the position to [0,0,0], set Voltage of Channel 3 to 100 V.
        Wait for 0.1s.
        :param port_num: string, device COM port. e.g.'COM3'
        :return: int, 0 means fine.
        """
        self.set_voltage(port_num='COM3')
        self.move_position_single(channel=1, port_num='COM3', check=False)
        self.move_position_single(channel=2, port_num='COM3', check=False)
        self.move_position_single(channel=4, port_num='COM3', check=False)

        time.sleep(0.1)

        return 0

    def move_position_all(self, location=(0.000, 0.000, 0.000), accuracy=0.005, check=True, port_num='COM3'):
        """
        Move the stage to a new position (X, Y, Z).
        :param location: arr, (X, Y, Z) target location in um
        :param accuracy: double, location accuracy in um
        :param check: bool, decide weather check the accuracy
        :param port_num: string, device COM port. e.g.'COM3'
        :return: int, 0 means fine, -1 means input form is wrong, 1 means input out of range.
        """
        # Check if the input position data is in right form
        if not np.size(location) == 3:
            print('Warning: The form of the location data is wrong!')
            return -1

        # Check if the input is inside the moving range
        status_temp = 0
        status_temp += self.move_position_single(channel=1, location=location[0], check=False, port_num='COM3')
        status_temp += self.move_position_single(channel=2, location=location[1], check=False, port_num='COM3')
        status_temp += self.move_position_single(channel=4, location=location[2], check=False, port_num='COM3')
        if not status_temp == 0:
            return 1

        # Check if the stage move to the target position
        while check:
            # Get current location from the build-in sensor
            temp_location = self.read_position_all()
            # Check if all 3 channels move to target position
            for i in range(3):
                if abs(location[i] - temp_location[i]) < accuracy:
                    if i == 2:
                        return 0  # When i == 2, all 3 channels have been tested and met the requirements
                    continue
                else:
                    break  # One of all 3 channels hasn't move to target, need to wait for more time
            # If it doesn't satisfy the requirement, wait for 2ms and check again
            time.sleep(0.002)
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
        move_coefficient = int(15000 / line_rate)
        hold_coefficient = int(move_coefficient / 4)
        wave_forward_move = np.linspace(start_point, end_point, move_coefficient)
        wave_forward_hold = np.ones(hold_coefficient) * end_point
        wave_back_move = np.linspace(end_point, start_point, move_coefficient)
        wave_back_hold = np.ones(hold_coefficient) * start_point
        wave_forward = list(np.append(wave_forward_move, wave_forward_hold))
        wave_back = list(np.append(wave_back_move, wave_back_hold))
        return wave_forward, wave_back

    def scanning_single_line(self, channel, waveform, port_num='COM3'):
        """
        Do the single line scanning based on the given waveform
        :param channel: int, the Channel used to scanning. e.g. 1, 2, 4
        :param waveform: list, self_defined waveform for control piezo stage movement
        :param port_num: string, device COM port. e.g.'COM3'
        :return: int, return 1 means try to scan on channel 3
        """
        # Check the channel number
        if channel == 3:
            print('Warning: Channel 3 can not scan!')
            return 1

        # Do the scanning
        for points in waveform:
            self.move_position_single(channel=channel, location=points, check=False, port_num='COM3')


if __name__ == '__main__':
    xmt = XMT()
    xmt.scan_devices()
    xmt.open_devices()
    print('position:', xmt.read_position_all())

    xmt.move_position_all(location=(20, 30, 20), check=False)
    time.sleep(1)
    print('position:', xmt.read_position_all())
    xmt.move_position_single(channel=1, location=10.0, check=False)
    time.sleep(0.5)
    print('position:', xmt.read_position_all())

    # print('Status of channel 1:', xmt.read_status(channel=1))
    # print('Status of channel 2:', xmt.read_status(channel=2))
    # print('Status of channel 3:', xmt.read_status(channel=3))
    # print('Status of channel 4:', xmt.read_status(channel=4))
    # xmt.move_position_single(channel=1, location=20, check=False)
    # time.sleep(1)
    # xmt.clear()
    xmt.clear()
    time.sleep(1)

    wave_forward, wave_back = xmt.generating_scan_array(channel=1, start_point=0, end_point=65)
    xmt.scanning_single_line(channel=1, waveform=wave_forward)
    time.sleep(1)
    xmt.clear()
    xmt.close_devices()

    # xmt.open_devices(nmb_of_device=device)
    # xmt.check_all_status(num_of_device=device)
