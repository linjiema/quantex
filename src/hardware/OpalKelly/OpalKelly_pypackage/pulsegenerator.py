# -*- coding:utf-8 -*-
import os.path

BITFILE_1000_INT = os.path.join(os.path.dirname(__file__), 'pg1000_int.bit')
BITFILE_1000_EXT = os.path.join(os.path.dirname(__file__), 'pg1000_ext.bit')

BITFILE_500_INT = os.path.join(os.path.dirname(__file__), 'Pulsegenerator24x4_intclk.bit')
BITFILE_500_EXT = os.path.join(os.path.dirname(__file__), 'pg500_ext.bit')

import time
import ok
import numpy as np
import struct
from copy import copy

class PulseGenerator500():
    """
    Represents an FPGA based Pulse Generator.
    """

    command_map = {'RUN': 0, 'LOAD': 1, 'RESET_READ': 2, 'RESET_SDRAM': 3, 'RESET_WRITE': 4, 'RETURN': 5}
    state_map = {0: 'IDLE', 1: 'RESET_READ', 2: 'RESET_SDRAM', 3: 'RESET_WRITE', 4: 'LOAD_0', 5: 'LOAD_1', 6: 'LOAD_2',
                 7: 'READ_0', 8: 'READ_1', 9: 'READ_2'}

    def __init__(self, serial='',
                 channel_map={'ch0': 0, 'ch1': 1, 'ch2': 2, 'ch3': 3, 'ch4': 4, 'ch5': 5, 'ch6': 6, 'ch7': 7, 'ch8': 8,
                              'ch9': 9, 'ch10': 10, 'ch11': 11, 'ch12': 12, 'ch13': 13, 'ch14': 14, 'ch15': 15,
                              'ch16': 16, 'ch17': 17, 'ch18': 18, 'ch19': 19, 'ch20': 20, 'ch21': 21, 'ch22': 22,
                              'ch23': 23},
                 core='12x8',
                 default_pattern=[]):
        self.serial = serial
        self.channel_map = channel_map
        self._core = core
        self.max_sequence_number = 1e6

        self.default_pattern = default_pattern
        self.reset()
        self.checkUnderflow()

    def reset(self):
        self.xem = ok.FrontPanel()

        # Open USB
        if (self.xem.OpenBySerial(self.serial) != 0):
            raise RuntimeError('failed to open USB connection.')

        # Load Core
        self.core = '24x4'
        self.n_channels = 24
        self.channel_width = 4
        self.dt = 2.
        self.set_frequency(250, 5)
        self.flash_fpga(BITFILE_500_INT)
        if self.getInfo() != (24, 4):
            raise RuntimeError('FPGA core does not match.')

        # Set Default
        self.setDefaultPattern(self.default_pattern)

        self.disableDecoder()

        self.ctrlPulser('RESET_WRITE')
        time.sleep(0.001)
        self.ctrlPulser('RESET_READ')
        time.sleep(0.001)
        self.ctrlPulser('RESET_SDRAM')
        time.sleep(0.01)

        self.last_download_sequence = None

    def set_frequency(self, vco, src):
        PLL = ok.PLL22150()
        self.xem.GetPLL22150Configuration(PLL)
        PLL.SetVCOParameters(vco, 48)
        PLL.SetOutputSource(0, src)
        PLL.SetOutputEnable(0, 1)
        self.xem.SetPLL22150Configuration(PLL)
        self.PLL = PLL

    def flash_fpga(self, bitfile):
        ret = self.xem.ConfigureFPGA(str(bitfile))
        if (ret != 0):
            raise RuntimeError('failed to upload bit file to fpga. Error code %i' % ret)

    

    def getInfo(self):
        """Returns the number of channels and channel width."""
        self.xem.UpdateWireOuts()
        ret = self.xem.GetWireOutValue(0x20)
        return ret & 0xff, ret >> 8

    def ctrlPulser(self, command):
        self.xem.ActivateTriggerIn(0x40, self.command_map[command])


    def getState(self):
        """
        Return the state of the FPGA core.

        The state is returned as a string out of the following list.

        'IDLE'
        'RESET_READ'
        'RESET_SDRAM'
        'RESET_WRITE'
        'LOAD_0'
        'LOAD_1'
        'LOAD_2'
        'READ_0'
        'READ_1'
        'READ_2'
        """
        self.xem.UpdateWireOuts()
        return self.state_map[self.xem.GetWireOutValue(0x21)]

    def checkState(self, wanted):
        """Raises a 'RuntimeError' if the FPGA state is not the 'wanted' state."""
        actual = self.getState()
        if actual != wanted:
            raise RuntimeError("FPGA State Error. Expected '" + wanted + "' state but got '" + actual + "' state.")

    def enableTrigger(self):
        self.xem.SetWireInValue(0x00, 0xFF, 2)
        self.xem.UpdateWireIns()

    def disableTrigger(self):
        self.xem.SetWireInValue(0x00, 0x00, 2)
        self.xem.UpdateWireIns()

    def enableDecoder(self):
        self.xem.SetWireInValue(0x00, 0x00, 1)
        self.xem.UpdateWireIns()

    def disableDecoder(self):
        self.xem.SetWireInValue(0x00, 0xFF, 1)
        self.xem.UpdateWireIns()

    def run(self, triggered=False):
        self.halt()
        if triggered:
            self.enableTrigger()
        else:
            self.disableTrigger()
        self.ctrlPulser('RESET_READ')
        time.sleep(0.01)
        self.ctrlPulser('RUN')
        time.sleep(0.01)
        self.enableDecoder()

    def halt(self):
        self.disableDecoder()
        time.sleep(0.02)
        self.ctrlPulser('RETURN')
        self.checkState('IDLE')

    def loadPages(self, buf):
        if len(buf) % 1024 != 0:
            raise RuntimeError(
                'Only full SDRAM pages supported. Pad your buffer with zeros such that its length is a multiple of 1024.')
        self.disableDecoder()
        self.ctrlPulser('RESET_WRITE')
        time.sleep(0.02)
        self.ctrlPulser('LOAD')
        self.checkState('LOAD_0')
        buf=bytearray(buf)
        bytes = self.xem.WriteToBlockPipeIn(0x80, 1024, buf)
        time.sleep(0.02)
        self.checkState('LOAD_0')
        self.ctrlPulser('RETURN')
        self.checkState('IDLE')
        return bytes

    def setResetValue(self, bits):
        self.xem.SetWireInValue(0x01, bits, 0xffff)
        if self.core == '24x4':
            self.xem.SetWireInValue(0x02, bits >> 16, 0xffff)
        self.xem.UpdateWireIns()

    def checkUnderflow(self):
        self.xem.UpdateTriggerOuts()
        return self.xem.IsTriggered(0x60, 1)

    def createBitsFromChannels(self, channels):
        """
        Convert a list of channel names into an array of bools of length N_CHANNELS,
        that specify the state (high or low) of each available channel.
        """
        bits = np.zeros(self.n_channels, dtype=bool)
        for channel in channels:
            bits[self.channel_map[channel]] = True
        return bits

    def setBits(self, integers, start, count, bits):
        """Sets the bits in the range start:start+count in integers[i] to bits[i]."""
        # ToDo: check bit order (depending on whether least significant or most significant bit is shifted out first from serializer)
        for i in range(self.n_channels):
            if bits[i]:
                integers[i] = integers[i] | (2 ** count - 1) << start


    def pack(self, mult, pattern):
        # ToDo: check whether max repetitions is exceeded, split into several commands if necessary
        pattern = [pattern[i] | pattern[i + 1] << 4 for i in range(0, len(pattern), 2)]
        s = struct.pack('>I%iB' % len(pattern), int(mult), *pattern[::-1])
        swap = b''
        for i in range(len(s)):
            swap += bytes([s[i - 1 if i % 2 else i + 1]])
        return swap

    def adjustSequenceWithDt(self, sequence):
        newsequence = []
        sequence.reverse()
        left = 0
        sum1 = 0
        sum2 = 0
        dt = self.dt
        while len(sequence):
            pul = sequence.pop()
            chs, dur = pul
            newdur1 = dur
            if left != 0:
                newdur1 += left
                pul = (chs, newdur1)
                left = 0
            if newdur1 % dt != 0:
                newdur2 = int(np.round(newdur1 / dt)) * dt
                pul = (chs, newdur2)
                left += (newdur1 - newdur2)
            newsequence.append(pul)
        if left != 0:
            print()
            'warning: there is %G ns left in the synthesis of sequence ' % left
        return newsequence

    def convertSequenceToBinary(self, sequence, loop=True):
        """
        Converts a pulse sequence (list of tuples (channels,time) )
        into a series of pulser instructions (128 bit words),
        and returns these in a binary buffer of length N*1024
        representing N SDRAM pages.

        A pulser instruction has the form

        command (1 bit) | repetition (31 bit) | ch0 pattern (8bit/4bit), ..., chN pattern (8bit/4bit)'

        The pulse sequence is split into a suitable series of
        such low level pulse commands taking into account the
        minimal 8 bit pattern length.

        input:

            sequence    list of tuples of the form (channels, time), where channels is
                        a list of strings corresponding to channel names and time is a float
                        specifying the time in ns.

            loop        if True, repeat the sequence indefinitely, if False, run the sequence once

        returns:

            buf         binary buffer containing N SDRAM pages that represent the sequence
        """

        sequence = copy(sequence)
        sequence = self.adjustSequenceWithDt(sequence)
        dt = self.dt
        N_CHANNELS, CHANNEL_WIDTH = self.n_channels, self.channel_width
        ONES = 2 ** CHANNEL_WIDTH - 1
        buf = []

        # we start with an integer zero for each channel.
        # In the following, we will start filling up the bits in each of these integers
        blank = np.zeros(N_CHANNELS, dtype=int)  # we will need this many times, so we create it once and copy from this
        pattern = blank.copy()
        index = 0
        for channels, time in sequence:
            ticks = int(round(time / dt))  # convert the time into an integer multiple of hardware time steps
            if ticks is 0:
                continue
            bits = self.createBitsFromChannels(channels)
            if index + ticks < CHANNEL_WIDTH:  # if pattern does not fill current block, insert into current block and continue
                self.setBits(pattern, index, ticks, bits)
                index += ticks
                continue
            if index > 0:  # else fill current block with pattern, reduce ticks accordingly, write block and start a new block
                self.setBits(pattern, index, CHANNEL_WIDTH - index, bits)
                buf.append(self.pack(0, pattern))
                ticks -= (CHANNEL_WIDTH - index)
                pattern = blank.copy()
            # split possible remaining ticks into a command with repetitions and a single block for the remainder
            repetitions = ticks / CHANNEL_WIDTH  # number of full blocks
            index = ticks % CHANNEL_WIDTH  # remainder will make the beginning of a new block
            if repetitions > 0:
                buf.append(self.pack(repetitions - 1, ONES * bits) )  # rep=0 means the block is executed once
            if index > 0:
                pattern = blank.copy()
                self.setBits(pattern, 0, index, bits)
        if loop:  # repeat the hole sequence
            if index > 0:  # fill up incomplete block with zeros and write it
                self.setBits(pattern, index, CHANNEL_WIDTH - index, np.zeros(N_CHANNELS, dtype=bool))
                buf.append(self.pack(0, pattern))
        else:  # stop after one execution
            if index > 0:  # fill up the incomplete block with the bits of the last step
                self.setBits(pattern, index, CHANNEL_WIDTH - index, bits)
                buf.append( self.pack(0, pattern))
            buf.append(self.pack(1 << 31, ONES * bits))
            buf.append(self.pack(1 << 31, ONES * bits))
        # print "buf has",len(buf)," bytes"
        buf = b''.join(buf)
        return b''.join([buf, ((1024 - len(buf)) % 1024) * b'\x00'])

    def Sequence(self, sequence, loop=True, triggered=False):
        """
        Output a pulse sequence.

        Input:
            sequence      List of tuples (channels, time) specifying the pulse sequence.
                          'channels' is a list of strings specifying the channels that
                          should be high and 'time' is a float specifying the time in ns.

        Optional arguments:
            loop          bool, defaults to True, specifying whether the sequence should be
                          excecuted once or repeated indefinitely.
            triggered     bool, defaults to False, specifies whether the execution
                          should be delayed until an external trigger is received
        """
        self.download(sequence, loop)
        self.run(triggered)

    def download(self, sequence, loop=True, dump=True):
        """
        Download a pulse sequence but not run immediately.

        Input:
            sequence      List of tuples (channels, time) specifying the pulse sequence.
                          'channels' is a list of strings specifying the channels that
                          should be high and 'time' is a float specifying the time in ns.

        Optional arguments:
            loop          bool, defaults to True, specifying whether the sequence should be
                          excecuted once or repeated indefinitely.
        """
        if len(sequence) > self.max_sequence_number:
            raise Exception('Sequence Too Large!')
        loaded = False
        tried_times = 0
        while not loaded:
            try:
                if self.last_download_sequence == None or self.last_download_sequence != sequence:
                    self.halt()
                    if dump:
                        print()
                        'downloading sequence'
                    self.loadPages(self.convertSequenceToBinary(sequence, loop))
                    self.last_download_sequence = copy(sequence)
                else:
                    if dump:
                        print()
                        'sequence unchaned,skipping download'
                loaded = True
            except Exception as e:
                self.reset()
                raise e

    def setDefaultPattern(self, channels):
        """
        Set the outputs continuously high or low.

        Input:
            channels    can be an integer or a list of channel names (strings).
                        If 'channels' is an integer, each bit corresponds to a channel.
                        A channel is set to low/high when the bit is 0/1, respectively.
                        If 'channels' is a list of strings, the specified channels
                        are set high, while all others are set low.

        note that there's a but not fixed, which need to divide channel_number by 2
        """
        try:
            iterator = iter(channels)
        except:
            self.setResetValue(channels)
        else:
            bits = 0
            for channel in channels:
                bits = bits | (1 << (self.channel_map[channel] >> 1))
            self.setResetValue(bits)
        self.halt()

    def High(self, channels):
        self.setDefaultPattern(channels)

    def Light(self):
        self.High(['laser', 'aom'])
        pass

    def Night(self):
        self.High([])

    def Open(self, mwpatt=['mw']):
        self.High(['laser', 'aom'] + mwpatt)

    def clear(self):
        self.last_download_sequence = None

if __name__ == '__main__':
    pg = PulseGenerator500(serial='', core='int')
    pg.halt()


    def test_laser():
        pg.High(['ch0'])


    def test_freq():
        pg.checkUnderflow()
        sequence = [(['ch0'], 1000), ([], 1000)] * 100000
        pg.Sequence(sequence, loop=True)


    def test_channels():
        sequence = []
        sequence.append(([], 10000))


        sequence.append((['ch4', 'ch6', 'ch7'], 1))
        sequence.append((['ch6', 'ch17'], 1))
        sequence.append((['ch0'], 100))
        sequence.append(([], 10000))

        #pg.Sequence(sequence, loop=True)
        pg.download(sequence, loop=True)
        pg.run(triggered=False)

        
        time.sleep(5)
        pg.halt()

    #test_channels()
