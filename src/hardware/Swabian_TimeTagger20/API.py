"""
Created on Apr 19th, 2023

This file is the functions for Time Tagger 20, Swabian Instrument
Works under python3
Requirement: Timetagger

@author: Linjie
"""
import TimeTagger
import numpy as np
import collections
import time


# Channel assignment
SPCM_1 = 1
SPCM_2 = 2
GATE_REF = 3
GATE_SIG = 4
SYNC_TRIGGER = 3


def logger_func(level, message):
    print(level, message)


class TimeTagger20:
    """
    Define the class of TimeTagger20, contains the function for measurement.
    The class will create a Timetagger when first init.
    """

    def __init__(self, serial="2208000ZCM"):
        """
        Create tagger for timetagger.
        Set Trigger level to 1.0V.
        """
        self.tagger = TimeTagger.createTimeTagger(serial=serial)
        self.tagger.setTriggerLevel(channel=SPCM_1, voltage=1.0)
        self.tagger.setTriggerLevel(channel=SPCM_2, voltage=1.0)
        self.tagger.setTriggerLevel(channel=GATE_REF, voltage=1.0)
        self.tagger.setTriggerLevel(channel=GATE_SIG, voltage=1.0)

        # TimeTagger.setLogger(logger_func)

    def reset_tt(self):
        """
        Reset the time tagger.
        """
        self.tagger.reset()

    def free_tt(self):
        """
        Free Time tagger. Need to reconnect the device after calling this function.
        """
        TimeTagger.freeTimeTagger(self.tagger)

    def reconnect_tt(self, serial="2208000ZCM"):
        """
        Reconnect the free timetagger and set the trigger level.
        :param serial: str, Serial of time tagger
        """
        self.tagger = TimeTagger.createTimeTagger(serial=serial)
        self.tagger.setTriggerLevel(channel=1, voltage=1.0)
        self.tagger.setTriggerLevel(channel=2, voltage=1.0)
        self.tagger.setTriggerLevel(channel=3, voltage=1.0)
        self.tagger.setTriggerLevel(channel=4, voltage=1.0)

    # Gated Counter
    def arm_gated_counter(self, repeat_num: "int"):
        """
        Arm gated counter for measurement
        :param repeat_num: int, how many gate it will record.
        """
        # combine the channel of two SPCM input
        self.combined_channel = TimeTagger.Combiner(tagger=self.tagger, channels=[SPCM_1, SPCM_2])
        # add synchronized measurement for ref and sig
        self.synchronized_gated_counter = TimeTagger.SynchronizedMeasurements(tagger=self.tagger)
        # Set ref and sig counter
        self.gated_counter_ref = TimeTagger.CountBetweenMarkers(tagger=self.synchronized_gated_counter.getTagger(),
                                                                click_channel=self.combined_channel.getChannel(),
                                                                begin_channel=GATE_REF,
                                                                end_channel=self.tagger.getInvertedChannel(GATE_REF),
                                                                n_values=repeat_num)
        self.gated_counter_sig = TimeTagger.CountBetweenMarkers(tagger=self.synchronized_gated_counter.getTagger(),
                                                                click_channel=self.combined_channel.getChannel(),
                                                                begin_channel=GATE_SIG,
                                                                end_channel=self.tagger.getInvertedChannel(GATE_SIG),
                                                                n_values=repeat_num)

    def start_gated_counter(self):
        """
        Start Gated Counter
        """
        self.synchronized_gated_counter.start()
        # while True:
        #     # print('not running')
        #     if self.synchronized_gated_counter.isRunning():
        #         # print('is running')
        #         break

    def get_counts_from_gated_counter(self):
        """
        Read data from gated counter.
        :return: ref, sig
        """
        # wait for measurement finish
        while True:
            # print('not ready')
            if self.gated_counter_sig.ready():
                # print('ready')
                break
        # self.synchronized_gated_counter.waitUntilFinished(timeout=60e3)
        # get data from ref and signal counter
        ref = np.sum(self.gated_counter_ref.getData())
        # print(self.gated_counter_ref.getData())
        sig = np.sum(self.gated_counter_sig.getData())
        return ref, sig

    def clear_gated_counter(self):
        # clean the buffer
        self.synchronized_gated_counter.clear()

    # One time Counter
    def arm_one_time_counter(self, freq=1):
        self.combined_channel = TimeTagger.Combiner(tagger=self.tagger, channels=[SPCM_1, SPCM_2])
        self.one_time_counter = TimeTagger.Counter(tagger=self.tagger,
                                                   channels=[self.combined_channel.getChannel()],
                                                   binwidth=int(1e10),
                                                   n_values=int(100 / freq))
        # stop and clean the buffer for future measurement
        self.one_time_counter.stop()
        self.one_time_counter.clear()

    def one_time_counter_count_once(self, freq=1):
        """
        Count once based on the given frequency.
        :param freq: Counting frequency
        :return counts per second
        """
        self.one_time_counter.startFor(int(1e12 / freq))
        self.one_time_counter.waitUntilFinished()
        cts = np.sum(self.one_time_counter.getData()) * freq
        self.one_time_counter.clear()
        return cts

    def count_once(self, freq=1):
        """
        Count once based on the given frequency.
        :param freq: Counting frequency
        :return counts per second
        """
        self.combined_channel = TimeTagger.Combiner(tagger=self.tagger, channels=[SPCM_1, SPCM_2])
        self.one_time_counter = TimeTagger.Counter(tagger=self.tagger,
                                                   channels=[self.combined_channel.getChannel()],
                                                   binwidth=int(1e10),
                                                   n_values=int(100 / freq))
        self.one_time_counter.startFor(int(1e12 / freq))
        self.one_time_counter.waitUntilFinished()
        cts = np.sum(self.one_time_counter.getData()) * freq
        self.reset_tt()
        return cts

    # Triggered Counter

    def arm_triggered_counter(self):
        """
        Arm triggered counter, stop ot and clean the buffer.
        The counter is mainly for Confocal Scanning
        """
        # combine the channel of two SPCM input
        self.combined_channel = TimeTagger.Combiner(tagger=self.tagger, channels=[SPCM_1, SPCM_2])
        # set triggered counter
        self.triggered_counter = TimeTagger.CountBetweenMarkers(tagger=self.tagger,
                                                                click_channel=self.combined_channel.getChannel(),
                                                                begin_channel=SYNC_TRIGGER,
                                                                n_values=200)
        # stop and clean the buffer for future measurement
        self.triggered_counter.stop()
        self.triggered_counter.clear()

    def start_triggered_counter(self):
        """
        Start the triggered counter.
        """
        self.triggered_counter.start()

    def get_triggered_counter_counts_array(self):
        """
        Get counts array from triggered counter.
        :return: counts array.
        """
        self.triggered_counter.waitUntilFinished(timeout=60e3)
        cts_arr_raw = self.triggered_counter.getData()
        self.triggered_counter.clear()
        return cts_arr_raw.tolist()


if __name__ == '__main__':
    a = TimeTagger20()

    a.free_tt()
