import ctypes
import os
import time
import numpy as np


class RotationStage:
    PORT_NUM = 'COM4'

    def __init__(self):
        origin_path = os.getcwd()
        dll = os.path.dirname(__file__) + '/DLL/moverLibrary_x64.dll'  # Give the path of dll file
        path = os.path.dirname(__file__) + '/DLL'
        # Load dll
        os.chdir(path)
        self.stage_dll = ctypes.cdll.LoadLibrary(dll)
        os.chdir(origin_path)
        self.device = None
        self.axis = 1
        # init data
        # int setting value
        self.speed = None
        self.acceleration = None
        self.abs_disp = None
        self.rel_disp = None
        self.jog_time = None
        self.jog_step = None
        self.jog_delay = None
        self.position = None
        # init setting state
        self.input_state = None
        self.output_state = None
        self.axis_motor = None
        self.quant_rel_move = None

    def open(self, port_num=PORT_NUM):
        """
        Connect the device and init the axis.
        :param port_num: Serial port of the device.
        """
        self.device = self.stage_dll.open(ctypes.c_char_p(bytes(port_num, "utf8")))
        self.stage_dll.initAxis(ctypes.c_int(self.device),
                                ctypes.c_int(1),
                                ctypes.c_char_p(bytes("EM-RP60", "utf-8")),
                                ctypes.c_int(1))
        return self.device

    def set_ttl_input(self, enable=0):
        """
        Set TTL input.
        :param enable: 0/1
        """
        self.stage_dll.setInputEnable(ctypes.c_int(self.device),
                                      ctypes.c_int(self.axis),
                                      ctypes.c_int(enable))

    def set_ttl_output(self, enable=0):
        """
        Set TTL output.
        :param enable: 0/1
        """
        self.stage_dll.setOutputEnable(ctypes.c_int(self.device),
                                       ctypes.c_int(self.axis),
                                       ctypes.c_int(enable))

    def set_axis_motor(self, enable=1):
        """
        Set axis motor state.
        When enable=1, the motor is on and can not be changed manually.
        :param enable: 0/1
        """
        self.stage_dll.setAxisEnable(ctypes.c_int(self.device),
                                     ctypes.c_int(self.axis),
                                     ctypes.c_int(enable))

    def set_quant_relative(self, enable=1):
        """
        Set quantitative relative movement.
        When enable=0, the stage will move continuously.
        :param enable: 0/1
        """
        self.stage_dll.setRelativePosEnable(ctypes.c_int(self.device),
                                            ctypes.c_int(self.axis),
                                            ctypes.c_int(enable))

    def set_move_param(self, speed=10.0, acc=200.0):
        """
        Set speed and acceleration of the motor.
        :param speed: speed of the motor, degree per second
        :param acc: acceleration of the motor, degree square per second
        """
        self.stage_dll.setSpeed(ctypes.c_int(self.device),
                                ctypes.c_int(self.axis),
                                ctypes.c_float(speed))
        self.stage_dll.setAcceleration(ctypes.c_int(self.device),
                                       ctypes.c_int(self.axis),
                                       ctypes.c_float(acc))

    def read_state_settings(self, axis_num=1) -> [int, int, int, int]:
        """
        Read the TTL input and output state, axis motor enable state and relative position state.
        :returns: [getInputEnable, getOutputEnable, getAxisEnable, getRelativePosEnable]
        """
        # define return data
        self.stage_dll.getInputEnable.restype = ctypes.c_int
        self.stage_dll.getOutputEnable.restype = ctypes.c_int
        self.stage_dll.getAxisEnable.restype = ctypes.c_int
        self.stage_dll.getRelativePosEnable.restype = ctypes.c_int
        # get data
        self.input_state = self.stage_dll.getInputEnable(ctypes.c_int(self.device),
                                                         ctypes.c_int(self.axis))
        self.output_state = self.stage_dll.getOutputEnable(ctypes.c_int(self.device),
                                                           ctypes.c_int(self.axis))
        self.axis_motor = self.stage_dll.getAxisEnable(ctypes.c_int(self.device),
                                                       ctypes.c_int(self.axis))
        self.quant_rel_move = self.stage_dll.getRelativePosEnable(ctypes.c_int(self.device),
                                                                  ctypes.c_int(self.axis))
        return [self.input_state, self.output_state, self.axis_motor, self.quant_rel_move]

    def read_value_settings(self, axis_num=1) -> [float, float, float, float, int, float, int]:
        """
        Read the setting value of speed, acceleration, absolute displacement, relative displacement, jog time, jog step and jog delay.
        :param axis_num: Axis ID
        :returns: [self.speed, self.acceleration, self.abs_disp, self.rel_disp, self.jog_time, self.jog_step, self.jog_delay]
        """
        # define return data
        self.stage_dll.getSpeed.restype = ctypes.c_float
        self.stage_dll.getAcceleration.restype = ctypes.c_float
        self.stage_dll.getAbsoluteDisp.restype = ctypes.c_float
        self.stage_dll.getRelativeDisp.restype = ctypes.c_float
        self.stage_dll.getJogTime.restype = ctypes.c_int
        self.stage_dll.getJogStep.restype = ctypes.c_float
        self.stage_dll.getJogDelay.restype = ctypes.c_int
        #  get data
        self.speed = self.stage_dll.getSpeed(ctypes.c_int(self.device),
                                             ctypes.c_int(self.axis))
        self.acceleration = self.stage_dll.getAcceleration(ctypes.c_int(self.device),
                                                           ctypes.c_int(self.axis))
        self.abs_disp = self.stage_dll.getAbsoluteDisp(ctypes.c_int(self.device),
                                                       ctypes.c_int(self.axis))
        self.rel_disp = self.stage_dll.getRelativeDisp(ctypes.c_int(self.device),
                                                       ctypes.c_int(self.axis))
        self.jog_time = self.stage_dll.getJogTime(ctypes.c_int(self.device),
                                                  ctypes.c_int(self.axis))
        self.jog_step = self.stage_dll.getJogStep(ctypes.c_int(self.device),
                                                  ctypes.c_int(self.axis))
        self.jog_delay = self.stage_dll.getJogDelay(ctypes.c_int(self.device),
                                                    ctypes.c_int(self.axis))
        return [self.speed, self.acceleration, self.abs_disp, self.rel_disp, self.jog_time, self.jog_step,
                self.jog_delay]

    def read_position(self, axis_num=1) -> float:
        """
        Read the current position of the motor.
        :return: current position.
        """
        self.stage_dll.GetCurrentPos.restype = ctypes.c_float
        self.position = self.stage_dll.GetCurrentPos(ctypes.c_int(self.device),
                                                     ctypes.c_int(self.axis),
                                                     ctypes.c_int(0))
        return self.position

    def move_abs(self, angle: float = 0.0, axis_num=1):
        """
        Move to absolute position.
        :param angle: absolute position.
        :param axis_num:
        """
        # set target position
        self.stage_dll.setAbsoluteDisp(ctypes.c_int(self.device),
                                       ctypes.c_int(self.axis),
                                       ctypes.c_float(angle))
        # move
        self.stage_dll.move(ctypes.c_int(self.device),
                            ctypes.c_int(self.axis),
                            ctypes.c_int(6))

    def move_relative(self, angle=0.0, direction='C', axis_num=1):
        """
        Move to relative position.
        :param angle: relative displacement
        :param direction: 'C' for clockwise, 'AC' for anticlockwise.
        :param axis_num:
        """
        self.stage_dll.setRelativeDisp(ctypes.c_int(self.device),
                                       ctypes.c_int(self.axis),
                                       ctypes.c_float(angle))
        if direction == 'C':
            self.stage_dll.move(ctypes.c_int(self.device),
                                ctypes.c_int(self.axis),
                                ctypes.c_int(4))
        else:
            self.stage_dll.move(ctypes.c_int(self.device),
                                ctypes.c_int(self.axis),
                                ctypes.c_int(5))

    def move_jog(self, num=1, step=0.0, delay=0, direction='C', axis_num=1):
        """
        Jog move.
        :param num: jog number
        :param step: jog angle
        :param delay: jog delay, micro second
        :param direction: 'C' for clockwise, 'AC' for anticlockwise.
        :param axis_num:
        """
        self.stage_dll.setJogTime(ctypes.c_int(self.device),
                                  ctypes.c_int(self.axis),
                                  ctypes.c_int(num))
        self.stage_dll.setJogStep(ctypes.c_int(self.device),
                                  ctypes.c_int(self.axis),
                                  ctypes.c_float(step))
        self.stage_dll.setJogDelay(ctypes.c_int(self.device),
                                   ctypes.c_int(self.axis),
                                   ctypes.c_int(delay))
        if direction == 'C':
            self.stage_dll.move(ctypes.c_int(self.device),
                                ctypes.c_int(self.axis),
                                ctypes.c_int(7))
        else:
            self.stage_dll.move(ctypes.c_int(self.device),
                                ctypes.c_int(self.axis),
                                ctypes.c_int(8))

    def return_to_origin(self, axis_num=1):
        """
        Return to origin point.
        :param axis_num: Axis ID
        """
        self.stage_dll.move(ctypes.c_int(self.device),
                            ctypes.c_int(self.axis),
                            ctypes.c_int(2))

    def stop(self, axis_num=1):
        """
        Stop moving.
        :param axis_num: Axis ID
        """
        self.stage_dll.move(ctypes.c_int(self.device),
                            ctypes.c_int(self.axis),
                            ctypes.c_int(1))

    def close(self):
        """
        Close the device.
        """
        self.stage_dll.close(ctypes.c_int(self.device))

    def is_running(self) -> int:
        """
        Check the moving state of the stage.
        :return: running state
        """
        state = self.stage_dll.getDoingState(ctypes.c_int(self.device),
                                             ctypes.c_int(self.axis))
        return state

    def wait_until_finish(self):
        """
        Hold until the stage stop running.
        """
        while True:
            if not self.is_running():
                break

    '''def test(self):
        self.open()
        a = self.read_state_settings()
        print(a)
        b = self.read_value_settings()
        print(b)
        # c = self.stage_dll.getErrorCode(ctypes.c_int(self.device), ctypes.c_int(1))
        # print(c)
        # self.stage_dll.GetCurrentPos.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
        print('location:', self.read_position())
        self.return_to_origin()
        self.wait_until_finish()
        self.move_abs(angle=90.5)
        self.wait_until_finish()
        print('location:', self.read_position())
        self.return_to_origin()
        self.wait_until_finish()
        self.close()'''

    def test(self):
        self.open()
        self.set_move_param(speed=20)
        # self.return_to_origin()
        # self.wait_until_finish()
        self.set_quant_relative()
        self.move_relative(angle=3, direction='AC')
        self.wait_until_finish()
        self.set_ttl_output(1)
        self.move_jog(num=121, step=3, delay=0, direction='C')
        self.wait_until_finish()
        self.close()


if __name__ == '__main__':
    stage = RotationStage()
    stage.test()
