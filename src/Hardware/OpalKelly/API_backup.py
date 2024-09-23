from OpalKelly_pypackage.pulsegenerator import PulseGenerator500
from collections import deque

import time
import numpy as np

from src.hardware.NI_PCIe_6321.API import SampleTriggerOutput, GatedCounter


class PulseGenerator():

    def __init__(self):
        # The pulse generator need to pass the serial number of FPGA
        self.pulser = PulseGenerator500(serial='1541000CZ8')
        # print(self.pulser.xem.GetSerialNumber())
        # serial = '1541000CZ8'

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

    def setup(self, pulse_seq):
        self.sequence = deque()
        # add delay to pulse sequence
        pulse_seq = self.add_delay(pulse_seq)
        # change pulse sequence to the form convenient to write
        pulse_seq = self.change_form(pulse_seq)
        # upload sequence in pulse generator
        self.write_seq(pulse_seq)
        self.pulser.download(self.sequence, loop=False, dump=False)

    # Need to be modified because the delay only need to
    def add_delay(self, pulse_seq):
        t1 = 100
        t2 = 200
        t_green = 300
        t_measure = 400
        for each in range(len(pulse_seq)):
            if pulse_seq[each][0] == 'S1':
                pulse_seq[each][1] = str(int(pulse_seq[each][1]) + t1)
                pulse_seq[each][2] = str(int(pulse_seq[each][2]) + t1)
            if pulse_seq[each][0] == 'S2':
                pulse_seq[each][1] = str(int(pulse_seq[each][1]) + t2)
                pulse_seq[each][2] = str(int(pulse_seq[each][2]) + t2)
            if pulse_seq[each][0] == 'Green':
                pulse_seq[each][1] = str(int(pulse_seq[each][1]) + t_green)
                pulse_seq[each][2] = str(int(pulse_seq[each][2]) + t_green)
            if pulse_seq[each][0] == 'Measure':
                pulse_seq[each][1] = str(int(pulse_seq[each][1]) + t_measure)
                pulse_seq[each][2] = str(int(pulse_seq[each][2]) + t_measure)
        return pulse_seq

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
        pulse_channel = np.zeros((4, (len(pulse_snip) - 1)))
        pulse_channel = pulse_channel.tolist()
        for each1 in range(len(pulse_snip) - 1):
            for each2 in pulse_seq:
                if (each2[0] == 'S1') and (int(each2[1]) <= pulse_snip[each1]) and (int(each2[2]) >= pulse_snip[each1+1]):
                    pulse_channel[0][each1] = 1
                if (each2[0] == 'S2') and (int(each2[1]) <= pulse_snip[each1]) and (int(each2[2]) >= pulse_snip[each1+1]):
                    pulse_channel[1][each1] = 1
                if (each2[0] == 'Green') and (int(each2[1]) <= pulse_snip[each1]) and (int(each2[2]) >= pulse_snip[each1+1]):
                    pulse_channel[2][each1] = 1
                if (each2[0] == 'Measure') and (int(each2[1]) <= pulse_snip[each1]) and (int(each2[2]) >= pulse_snip[each1+1]):
                    pulse_channel[3][each1] = 1

        # change the form of sequence snippet
        pulse_snip2 = np.zeros(len(pulse_snip) - 1)
        pulse_snip2 = pulse_snip2.tolist()
        for each in range(len(pulse_snip2)):
            pulse_snip2[each] = pulse_snip[each + 1] - pulse_snip[each]

        # get the new pulse sequence
        pulse_newseq = []
        pulse_newseq.append(pulse_snip2)
        for each in range(4):
            pulse_newseq.append(pulse_channel[each])

        return pulse_newseq

    def write_seq(self, pulse_seq):
        for each1 in range(len(pulse_seq[0])):
            name = []
            for each2 in range(len(pulse_seq) - 1):
                if pulse_seq[(each2 + 1)][each1] == 1:
                    name.append('ch' + str(each2+0))
            # print(name)
            # print(pulse_seq[0][each1])
            self.sequence.append((name, pulse_seq[0][each1]))


if __name__ == '__main__':
    hardware = PulseGenerator()
    output = SampleTriggerOutput()
    counter = GatedCounter()
    output.init_task()
    output.start_task()
    counter.init_task()
    counter.start_task()

    # test_dir = 'C:\\WorkSpace\\pulse_odmr\\Cache\\PulseSeq\\test_pulse_multi_channel.txt'
    # with open(test_dir, 'r') as f_seq:
    #     test_seq = []
    #     # Load into self.seq
    #     for line in f_seq.readlines():
    #         line = line.replace('\n', '').replace('[', '').replace(']', '').replace("'", '')
    #         test_seq.append(line.split(','))
    #
    # hardware.sequence = deque()
    # print('test seq: ', test_seq)
    # test_seq = hardware.add_delay(test_seq)
    # print('test seq with delay: ', test_seq)
    # test_seq = hardware.change_form(test_seq)
    # print('test seq with delay after change form: ', test_seq)
    # hardware.write_seq(test_seq)
    # print(hardware.sequence)
    hardware.sequence = deque()
    test_seq = [[100, 100, 100, 100, 100]]
    test_seq.extend([[0.0, 1, 0.0, 0, 0, 0.0]] * 24)
    hardware.write_seq(test_seq)
    hardware.pulser.download(hardware.sequence, loop=False, dump=False)
    hardware.start_output()
    time.sleep(2)
    hardware.stop_output()
    output.close()
    x = counter.get_counts()
    print(x)
# num 8 19 channel is broken

