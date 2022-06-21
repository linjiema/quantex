from pulsestreamer import *
import os
import re
import time
import math

# Define channel name
LASER = 0
MICROWAVE_SWITCH = 1
COUNTER_REFERENCE = 2
COUNTER_SIGNAL = 3
COUNTER_TRIGGER = 4


class PulseGenerator:

    def __init__(self, serial):
        self.device_serial = serial
        try:
            self.pulser = PulseStreamer(self.get_ip())
        except BaseException as e:
            print(e)
        else:
            self.pulser.setTrigger(start=TriggerStart.SOFTWARE)

    def get_ip(self):
        with os.popen('arp -a') as arp_table_file:
            arp_table = arp_table_file.read()
        for each_device in re.findall('([-.0-9]+)\s+([-0-9a-f]{17})\s+(\w+)', arp_table):
            if each_device[1] == self.device_serial:
                return each_device[0]
        raise ValueError('No Device!')

    def load_seq(self, pulse_seq, repeat_time):
        [ref_patten, sig_patten, laser_patten, microwave_patten, trigger_patten] = self.change_form(pulse_seq)
        seq = self.pulser.createSequence()
        seq.setDigital(COUNTER_REFERENCE, ref_patten)
        seq.setDigital(COUNTER_SIGNAL, sig_patten)
        seq.setDigital(LASER, laser_patten)
        seq.setDigital(MICROWAVE_SWITCH, microwave_patten)
        seq.setDigital(COUNTER_TRIGGER, trigger_patten)
        # create seq used to upload
        seq_upload = seq * 8
        print('Seq:', seq.getData(), 'duration:', seq.getDuration())
        print('Seq_upload:', seq_upload.getData(), 'duration:', seq_upload.getDuration())
        repeat = int(math.ceil(repeat_time/8) + 1)
        print('Total point:', repeat_time, 'repeat_time:', repeat)
        self.pulser.stream(seq=seq_upload, n_runs=repeat)
        # self.pulser.stream(seq=seq_upload)
    @staticmethod
    def change_form(pulse_seq):
        channels = [[], [], [], [], []]  # [ref, sig, laser, microwave, trigger]
        # split pulse into channel
        for each_pulse in pulse_seq:
            if each_pulse[0] == 'Ref':
                channels[0].append((int(each_pulse[1]), int(each_pulse[2])))
            elif each_pulse[0] == 'Sig':
                channels[1].append((int(each_pulse[1]), int(each_pulse[2])))
            elif each_pulse[0] == 'Laser':
                channels[2].append((int(each_pulse[1]), int(each_pulse[2])))
            elif each_pulse[0] == 'MicroWave':
                channels[3].append((int(each_pulse[1]), int(each_pulse[2])))
            elif each_pulse[0] == 'Trigger':
                channels[4].append((int(each_pulse[1]), int(each_pulse[2])))
        print('Sequence:', pulse_seq)
        print('Channels:', channels)
        # sort
        for each_channel in channels:
            if each_channel:
                # bubble sort
                for i in range(len(each_channel) - 1):
                    for j in range(len(each_channel) - i - 1):
                        if each_channel[j][0] > each_channel[j+1][0]:
                            each_channel[j], each_channel[j+1] = each_channel[j+1], each_channel[j]
        print('sort:', channels)
        # generate patten
        patten = []
        for each_channel in channels:
            if each_channel:
                # init patten for each channel
                patten_each_channel = []
                # init pulse length, interval and initial time
                pulse_length = []
                interval = []
                init_time = each_channel[0][0]
                # get pulse length
                for each_frag in each_channel:
                    pulse_length.append(each_frag[1]-each_frag[0])
                # get interval between pulse
                for i in range(len(each_channel) - 1):
                    interval.append(each_channel[i+1][0]-each_channel[i][1])
                if init_time != 0:
                    patten_each_channel.append((init_time, 0))
                patten_each_channel.append((pulse_length[0], 1))
                for i in range(len(interval)):
                    if interval[i] <= 0:
                        temp = patten_each_channel[-1][0] + interval[i] + pulse_length[i + 1]
                        if temp > patten_each_channel[-1][0]:
                            patten_each_channel[-1] = (temp, 1)
                    else:
                        patten_each_channel.append((interval[i], 0))
                        patten_each_channel.append((pulse_length[i+1], 1))
                patten.append(patten_each_channel)
            else:
                patten.append([])
        print('patten:[ref, sig, laser, microwave, trigger]', patten)
        return patten

    def start_output(self):
        self.pulser.startNow()

    def stop_output(self):
        self.pulser.forceFinal()

    def reset_pulse_generator(self):
        self.pulser.reset()

    def reboot_pulse_generator(self):
        self.pulser.reboot()
        time.sleep(30)

    def laser_on(self):
        self.pulser.constant(([LASER], 0.0, 0.0))

    def laser_off(self):
        self.pulser.constant()

    def mw_switch_on(self):
        self.pulser.constant(([MICROWAVE_SWITCH], 0.0, 0.0))

    def mw_switch_off(self):
        self.pulser.constant()

    def test(self):
        self.load_seq(pulse_seq=[['Sig', '710', '1010'], ['Laser', ' 500', ' 1000'], ['Ref', '1200', '1500'], ['Trigger', '1500', '1520']], repeat_time=10000)
        self.start_output()




if __name__ == '__main__':
    pulse_generator = PulseGenerator(serial='00-26-32-f0-92-26')
    # pulse_generator.laser_on()
    # time.sleep(30)
    # pulse_generator.laser_off()
    pulse_generator.test()
    time.sleep(2)
    pulse_generator.test()
    time.sleep(2)
    pulse_generator.stop_output()

    # pulse_generator.reset_pulse_generator()
    # pulse_generator = PulseGenerator(serial='00-26-32-f0-92-20')
    # a = pulse_generator.change_form([['Laser', '  200', '  600'], ['MicroWave', '  200', '  1000'], ['Ref', '  0', '  100'], ['Sig', '  0', '  100']])
    # print('Patten:', a)
