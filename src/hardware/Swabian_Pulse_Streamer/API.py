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
    """
    Contain selected manipulation for Pulse Generator,
    func list:
    get_ip(), load_seq()
    """

    def __init__(self, serial):
        """
        Connect to the device and set the SOFTWARE_TRIGGER mode
        :param serial: MAC Address of the device(xx-xx-xx-xx-xx-xx), all in lower case
        """
        self.device_serial = serial
        try:
            # try to connect to the device
            self.pulser = PulseStreamer(self.get_ip())
        except BaseException as e:
            raise
        else:
            # set trigger
            self.pulser.setTrigger(start=TriggerStart.SOFTWARE)

    def get_ip(self):
        """
        Get the ip of the device based on MAC address by search the arp table
        :return: device ip(str)
        """
        # get arp table
        with os.popen('arp -a') as arp_table_file:
            arp_table = arp_table_file.read()
        # search for the IP address based on the MAC address
        for each_device in re.findall('([-.0-9]+)\s+([-0-9a-f]{17})\s+(\w+)', arp_table):
            if each_device[1] == self.device_serial:
                return each_device[0]
        raise ValueError('PulseGenerator hasn\'t been connected!')

    def load_rotation_gate_seq(self):
        microwave_patten = [(200000, 0), (200000, 1)]
        rotation_gate_ref_patten = [(20000, 0), (180000, 1), (200000, 0)]
        rotation_gate_sig_patten = [(200000, 0), (20000, 0), (180000, 1)]
        rotation_seq = self.pulser.createSequence()
        rotation_seq.setDigital(COUNTER_REFERENCE, rotation_gate_ref_patten)
        rotation_seq.setDigital(COUNTER_SIGNAL, rotation_gate_sig_patten)
        rotation_seq.setDigital(MICROWAVE_SWITCH, microwave_patten)
        rotation_seq.setDigital(LASER, [(8, 1)])
        rotation_seq_upload = rotation_seq * 8
        self.pulser.stream(seq=rotation_seq_upload, n_runs=-1)



    def load_seq(self, pulse_seq, repeat_time):
        """
        Load sequence into the device buffer
        :param pulse_seq: pulse sequence in the form of [['Channel_name', 'start_time', 'end_time'], [], ...]
        :param repeat_time: how many times this sequence need to repeat(int)
        :return: None
        """
        [ref_patten, sig_patten, laser_patten, microwave_patten, trigger_patten] = self.change_form(pulse_seq)
        # print('patten:[ref, sig, laser, microwave, trigger]', [ref_patten, sig_patten, laser_patten, microwave_patten, trigger_patten])
        seq = self.pulser.createSequence()
        seq.setDigital(COUNTER_REFERENCE, ref_patten)
        seq.setDigital(COUNTER_SIGNAL, sig_patten)
        seq.setDigital(LASER, laser_patten)
        seq.setDigital(MICROWAVE_SWITCH, microwave_patten)
        seq.setDigital(COUNTER_TRIGGER, trigger_patten)
        # create seq used to upload
        seq_upload = seq * 8
        # print('Seq:', seq.getData(), 'duration:', seq.getDuration())
        # print('Seq_upload:', seq_upload.getData(), 'duration:', seq_upload.getDuration())
        # set repeat time
        if repeat_time == -1:
            self.pulser.stream(seq=seq_upload, n_runs=-1)
        else:
            repeat = int(math.ceil(repeat_time / 8) + 2)
            # print('Total point:', repeat_time, 'repeat_time:', repeat)
            # set stream parameters
            self.pulser.stream(seq=seq_upload, n_runs=repeat)
            # self.pulser.stream(seq=seq_upload)

    @staticmethod
    def change_form(pulse_seq):
        """
        Change the pulse sequence into the form that can be sent to the device
        :param pulse_seq:  pulse sequence in the form of [['Channel_name', 'start_time', 'end_time'], [], ...]
        :return: sequence list that fit the device
        """
        # init list for store the final patten that sent to the device
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
        # print('Sequence:', pulse_seq)
        # print('Channels:', channels)
        # sort
        for each_channel in channels:
            if each_channel:
                # bubble sort
                for i in range(len(each_channel) - 1):
                    for j in range(len(each_channel) - i - 1):
                        if each_channel[j][0] > each_channel[j + 1][0]:
                            each_channel[j], each_channel[j + 1] = each_channel[j + 1], each_channel[j]
        # print('sort:', channels)
        # find the end time of the sequence
        end_time = channels[-1][-1][-1]
        # print('end_time:', end_time)
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
                    pulse_length.append(each_frag[1] - each_frag[0])
                # get interval between pulse
                for i in range(len(each_channel) - 1):
                    interval.append(each_channel[i + 1][0] - each_channel[i][1])
                # check how long is the last blank
                last_blank = end_time - each_channel[-1][-1]
                # print('last_pulse_end:', last_blank)
                # add first term if the first high voltage pulse is not start form 0
                if init_time != 0:
                    patten_each_channel.append((init_time, 0))
                # add first high voltage clip
                patten_each_channel.append((pulse_length[0], 1))
                # add more clips
                for i in range(len(interval)):
                    if interval[i] <= 0:
                        temp = patten_each_channel[-1][0] + interval[i] + pulse_length[i + 1]
                        if temp > patten_each_channel[-1][0]:
                            patten_each_channel[-1] = (temp, 1)
                    else:
                        patten_each_channel.append((interval[i], 0))
                        patten_each_channel.append((pulse_length[i + 1], 1))
                # fill the last blank
                if last_blank != 0:
                    patten_each_channel.append((last_blank, 0))
                patten.append(patten_each_channel)
            else:
                patten.append([])
        # print('patten:[ref, sig, laser, microwave, trigger]', patten)
        return patten

    def start_output(self):
        """
        Start output
        :return: None
        """
        self.pulser.startNow()

    def stop_output(self):
        """
        Force to stop all output
        :return: None
        """
        self.pulser.forceFinal()

    def reset_pulse_generator(self):
        """
        Reset the pulse generator
        :return: None
        """
        self.pulser.reset()

    def reboot_pulse_generator(self):
        """
        Reboot the device
        :return: None
        """
        self.pulser.reboot()
        time.sleep(30)

    def laser_on(self):
        """
        Turn on the laser by set the laser channel voltage to high
        :return: None
        """
        self.pulser.constant(([LASER], 0.0, 0.0))

    def laser_off(self):
        """
        Turn off the laser by set the laser channel voltage to low
        :return: None
        """
        self.pulser.constant()

    def mw_switch_on(self):
        """
        Turn on the microwave switch by set the microwave switch channel voltage to high
        :return: None
        """
        self.pulser.constant(([MICROWAVE_SWITCH], 0.0, 0.0))

    def mw_switch_off(self):
        """
        Turn off the microwave switch by set the microwave switch channel voltage to low
        :return: None
        """
        self.pulser.constant()

    def test(self):
        [ref_patten, sig_patten, laser_patten, microwave_patten, trigger_patten] = [[(1853, 0), (300, 1), (50, 0)], [(1853, 0), (300, 1), (50, 0)], [(1500, 0), (500, 1), (203, 0)], [], [(2153, 0), (50, 1)]]
        seq1 = self.pulser.createSequence()
        seq1.setDigital(COUNTER_REFERENCE, ref_patten)
        seq1.setDigital(COUNTER_SIGNAL, sig_patten)
        seq1.setDigital(LASER, laser_patten)
        seq1.setDigital(MICROWAVE_SWITCH, microwave_patten)
        seq1.setDigital(COUNTER_TRIGGER, trigger_patten)
        # create seq used to upload
        seq_upload = seq1 * 8
        # print('Seq:', seq.getData(), 'duration:', seq.getDuration())
        # print('Seq_upload:', seq_upload.getData(), 'duration:', seq_upload.getDuration())
        # set repeat time
        # print('Total point:', repeat_time, 'repeat_time:', repeat)
        # set stream parameters
        # self.pulser.stream(seq=seq_upload)
        seq2 = self.pulser.createSequence()
        seq2.setDigital(7, [(10, 1), (300, 0)])
        seq_upload2 = seq2 * 8
        self.pulser.stream(seq=seq_upload2, n_runs=500000)


if __name__ == '__main__':
    pulse_generator = PulseGenerator(serial='00-26-32-f0-92-26')
    # pulse_generator.laser_on()
    # time.sleep(30)
    # pulse_generator.laser_off()
    pulse_generator.test()
    pulse_generator.start_output()
    time.sleep(2)
    pulse_generator.stop_output()


    # pulse_generator.reset_pulse_generator()
    # pulse_generator = PulseGenerator(serial='00-26-32-f0-92-20')
    # a = pulse_generator.change_form([['Laser', '  200', '  600'], ['MicroWave', '  200', '  1000'], ['Ref', '  0', '  100'], ['Sig', '  0', '  100']])
    # print('Patten:', a)
