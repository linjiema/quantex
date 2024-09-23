"""
Created on Apr 19th, 2023

This file is the functions for Time Tagger 20, Swabian Instrument
Works under python3
Requirement: Timetagger

@author: Linjie
"""
import TimeTagger


def logger_func(level, message):
    print(level, message)


class TimeTagger20:
    """

    """
    def __init__(self, serial="2208000ZCM"):
        """

        """
        self.tagger = TimeTagger.createTimeTagger(serial=serial)
        self.tagger.setTriggerLevel(channel=1, voltage=0.9)
        # TimeTagger.setLogger(logger_func)

    def reset_tt(self):
        self.tagger.reset()

    def free_tt(self):
        TimeTagger.freeTimeTagger(self.tagger)

    def test_func(self):
        print('This is the test.')
        # self.tagger.setTestSignal([1, 2], True)
        # print('The Test signal has been turned on!')
        print(self.tagger.autoCalibration())
        self.reset_tt()




if __name__ == '__main__':
    a = TimeTagger20()
    a.test_func()
