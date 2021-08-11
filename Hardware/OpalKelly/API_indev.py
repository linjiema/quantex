"""
Created on Jun 30, 2021

This file is the functions for OpalKelly Pulse Generator
Works under python3.7
Requirement: OpalKelly Package

@author: Linjie
"""

from OpalKelly_pypackage.pulsegenerator import PulseGenerator500
from collections import deque

import time
import numpy as np

from Hardware.NI_PCIe_6321.API import SampleTriggerOutput, GatedCounter


class PulseGenerator():

    def __init__(self):
        # The pulse generator need serial number of FPGA
        self.pulser = PulseGenerator500(serial='1541000CZ8')
        # Linjie serial = '1541000CZ8'
        # Lingzhi serial = '1914000P9X'

    def start_output(self):
        """
        This method start the output of the pulse
        :return: None
        """
        self.pulser.run()

    def stop_output(self):
        """
        This method stop the output of the pulse
        :return: None
        """
        self.pulser.halt()

    def load_seq(self, pulse_seq):
        """
        Load the Pulse Sequence into Pulse Generator.
        Input form: [['Name of the Channel', 'Start Time', 'End Time'], ['', '', ''], ...]
        :param pulse_seq: The pulse sequence as the input form
        :return: None
        """
        # change pulse sequence to the form convenient to write
        pulse_seq_reform = self.change_form(pulse_seq=pulse_seq)
        # upload sequence in pulse generator
        self.sequence = self.write_seq(pulse_seq_reform)
        print(self.sequence)
        self.pulser.download(self.sequence, loop=False, dump=False)

    def change_form(self, pulse_seq):
        pulse_snip = [0]
        # get sequence snippet
        for each1 in range(len(pulse_seq)):
            for each2 in range(2):
                i = True
                for each3 in pulse_snip:
                    if each3 == int(pulse_seq[each1][(each2 + 1)]):
                        i = False
                if i is True:
                    pulse_snip.append(int(pulse_seq[each1][(each2 + 1)]))
        pulse_snip.sort()

        # get channel condition in each snippet
        pulse_channel = np.zeros((len(pulse_seq), (len(pulse_snip) - 1)))
        pulse_channel = list(pulse_channel)
        print('pulse_snip', pulse_snip)
        print('pulse_seq', pulse_seq)
        for each1 in range(len(pulse_snip) - 1):
            for each2 in pulse_seq:
                if (each2[0] == 'Ref') and (int(each2[1]) <= pulse_snip[each1]) and (int(each2[2]) >= pulse_snip[each1+1]):
                    pulse_channel[0][each1] = 1
                if (each2[0] == 'Sig') and (int(each2[1]) <= pulse_snip[each1]) and (int(each2[2]) >= pulse_snip[each1+1]):
                    pulse_channel[1][each1] = 1
                if (each2[0] == 'Laser') and (int(each2[1]) <= pulse_snip[each1]) and (int(each2[2]) >= pulse_snip[each1+1]):
                    pulse_channel[2][each1] = 1
                if (each2[0] == 'MicroWave') and (int(each2[1]) <= pulse_snip[each1]) and (int(each2[2]) >= pulse_snip[each1+1]):
                    pulse_channel[3][each1] = 1
                if (each2[0] == 'Trigger') and (int(each2[1]) <= pulse_snip[each1]) and (
                        int(each2[2]) >= pulse_snip[each1 + 1]):
                    pulse_channel[4][each1] = 1

        # change the form of sequence snippet
        print('pulse channel', pulse_channel)
        pulse_snip2 = np.zeros(len(pulse_snip) - 1)
        pulse_snip2 = list(pulse_snip2)
        for each in range(len(pulse_snip2)):
            pulse_snip2[each] = pulse_snip[each + 1] - pulse_snip[each]

        # get the new pulse sequence
        pulse_newseq = []
        pulse_newseq.append(pulse_snip2)
        for each in range(len(pulse_channel)):
            pulse_newseq.append(pulse_channel[each])

        return pulse_newseq

    def write_seq(self, pulse_seq):
        sequence_temp = deque()
        print('pulse_seq', pulse_seq)
        for each1 in range(len(pulse_seq[0])):
            name = []
            for each2 in range(len(pulse_seq) - 1):
                if pulse_seq[(each2 + 1)][each1] == 1:
                    name.append('ch' + str(each2+0))
            sequence_temp.append((name, pulse_seq[0][each1]))
        return sequence_temp


if __name__ == '__main__':
    hardware = PulseGenerator()
    test_seq = [[100, 100, 100, 100, 100]]
    # test_seq.extend([[0.0, 1, 0.0, 0, 0, 0.0]] * 24)
    # hardware = PulseGenerator()
    # output = SampleTriggerOutput()
    # counter = GatedCounter()
    # output.init_task()
    # output.start_task()
    # counter.init_task()
    # counter.start_task()
    #
    # hardware.sequence = deque()
    # test_seq = [[100, 100, 100, 100, 100]]
    # test_seq.extend([[0.0, 1, 0.0, 0, 0, 0.0]] * 24)
    # hardware.write_seq(test_seq)
    # hardware.pulser.download(hardware.sequence, loop=False, dump=False)
    # hardware.start_output()
    # time.sleep(2)
    # hardware.stop_output()
    # output.close()
    # x = counter.get_counts()
    # print(x)
# num 8 19 channel is broken

