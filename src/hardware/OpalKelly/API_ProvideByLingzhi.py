from OpalKelly_pypackage.pulsegenerator import PulseGenerator500
from collections import deque

import time
import numpy as np


class PulseGenerator():

    def __init__(self):
        self.pulser = PulseGenerator500(serial='1541000CZ8')
        print(self.pulser.xem.GetSerialNumber())

    def setup(self, pulse_seq):
        self.sequence = deque()
        # add delay to pulse sequence
        pulse_seq = self.add_delay(pulse_seq)
        # change pulse sequence to the form convenient to write
        pulse_seq = self.change_form(pulse_seq)
        # upload sequence in pulse generator
        self.write_seq(pulse_seq)
        self.pulser.download(self.sequence, loop=False, dump=False)

    def output(self):
        # pulse output mode is always the infinite loop mode
        self.pulser.run(triggered=False)

    def stop_output(self):
        # stop output pulse sequence
        self.pulser.halt()

    # Need to be modified because the delay only need to
    def add_delay(self, pulse_seq):
        t1 = 0
        t2 = 0
        t_green = 0
        t_measure = 0
        for each in range(len(pulse_seq)):
            if pulse_seq[each, 0] == 'S1':
                pulse_seq[each, 1] = str(int(pulse_seq[each, 1]) + t1)
                pulse_seq[each, 2] = str(int(pulse_seq[each, 2]) + t1)
            if pulse_seq[each, 0] == 'S2':
                pulse_seq[each, 1] = str(int(pulse_seq[each, 1]) + t2)
                pulse_seq[each, 2] = str(int(pulse_seq[each, 2]) + t2)
            if pulse_seq[each, 0] == 'Green':
                pulse_seq[each, 1] = str(int(pulse_seq[each, 1]) + t_green)
                pulse_seq[each, 2] = str(int(pulse_seq[each, 2]) + t_green)
            if pulse_seq[each, 0] == 'Measure':
                pulse_seq[each, 1] = str(int(pulse_seq[each, 1]) + t_measure)
                pulse_seq[each, 2] = str(int(pulse_seq[each, 2]) + t_measure)
        return pulse_seq

    def change_form(self, pulse_seq):
        pulse_snip = []
        # get sequence snippet
        for each1 in range(len(pulse_seq)):
            for each2 in range(2):
                for each3 in pulse_snip:
                    i = True
                    if each3 == pulse_seq[each1, (each2 + 1)]:
                        i = False
                if i is True:
                    pulse_snip.append(int(pulse_seq[each1, (each2 + 1)]))
        pulse_snip.sort()

        # get channel condition in each snippet
        pulse_channel = np.zeros((4, (len(pulse_snip) - 1)))
        pulse_channel = pulse_channel.tolist()
        for each1 in range(len(pulse_snip) - 1):
            for each2 in pulse_seq:
                if (each2[0] == 'S1') and (int(each2[1]) <= each1) and (int(each2[2]) >= (each1 + 1)):
                    pulse_channel[0, each1] = 1
                if (each2[0] == 'S2') and (int(each2[1]) <= each1) and (int(each2[2]) >= (each1 + 1)):
                    pulse_channel[1, each1] = 1
                if (each2[0] == 'Green') and (int(each2[1]) <= each1) and (int(each2[2]) >= (each1 + 1)):
                    pulse_channel[2, each1] = 1
                if (each2[0] == 'Measure') and (int(each2[1]) <= each1) and (int(each2[2]) >= (each1 + 1)):
                    pulse_channel[3, each1] = 1

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
            for each2 in range(4):
                if pulse_seq[(each2 + 1), each1] == 1:
                    name.append('ch' + str(channel))
            self.sequence.append((name, pulse_seq[0, each1]))


if __name__ == '__main__':
    hardware = PulseGenerator()
    hardware.setup()
    instrument = PulseGenerator()
    instrument.setup()
    instrument.run_once()
    time.sleep(1)
    tagger = createTimeTagger("1948000SAE")
    tagger.reset()
    count = Counter(tagger, channels=[4], binwidth=int(1000000000000), n_values=int(10))
    time.sleep(10)
    data = count.getData()
    print(data)
