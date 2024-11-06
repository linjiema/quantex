"""
Created on Jun 30, 2021

This File is the dialog of Settings Dialog. Including the connect of the methods and the function.
This file need the pyUI file of Settings_dialog.
This file need the settings txt file saved in 'Cache/Settings'

@author: Linjie
"""

import sys
import os

from ui.uipy.pulse_ESR_polarization.Settings import Ui_Settings
from PyQt5 import QtCore, QtWidgets


class Setting_GUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        os.chdir(os.path.dirname(__file__))

        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.save_and_accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.load_settings()

    def load_settings(self):
        """
        Call this method when need to load the settings from the file.
        """
        # Load Frequency Sweep Settings
        dir_freq_sweep_settings = os.path.abspath(
            os.path.join(os.path.dirname("__file__"), os.path.pardir, 'Cache/Settings/freq_sweep_settings.txt')
        )
        with open(dir_freq_sweep_settings, 'r') as f_freq_sweep_settings:
            dic_freq_sweep_settings = {}
            for line in f_freq_sweep_settings.readlines():
                if line[-1] == '\n':
                    line = line[:-1]
                [key, value] = line.split('=')
                dic_freq_sweep_settings[key] = value
        dic_freq_sweep_set = {
            'LOOP_NUM': self.ui.lineEditFreqSetNumOfLoop,
            'AVERAGE_NUM': self.ui.lineEditFreqSetNumOfAverage,
        }
        for key, value in dic_freq_sweep_settings.items():
            dic_freq_sweep_set.get(key).setText(value)

        # Load Time Sweep Settings
        dir_time_sweep_settings = os.path.abspath(
            os.path.join(os.path.dirname("__file__"), os.path.pardir, 'Cache/Settings/time_sweep_settings.txt')
        )
        with open(dir_time_sweep_settings, 'r') as f_time_sweep_settings:
            dic_time_sweep_settings = {}
            for line in f_time_sweep_settings.readlines():
                if line[-1] == '\n':
                    line = line[:-1]
                [key, value] = line.split('=')
                dic_time_sweep_settings[key] = value
        dic_time_sweep_set = {
            'LOOP_NUM': self.ui.lineEditTimeSetNumOfLoop,
            'AVERAGE_NUM': self.ui.lineEditTimeSetNumOfAverage,
        }
        for key, value in dic_time_sweep_settings.items():
            dic_time_sweep_set.get(key).setText(value)

        # Load Delay Settings
        dir_delay_settings = os.path.abspath(
            os.path.join(os.path.dirname("__file__"), os.path.pardir, 'Cache/Settings/delay_settings.txt')
        )
        with open(dir_delay_settings, 'r') as f_delay_settings:
            dic_delay_settings = {}
            for line in f_delay_settings.readlines():
                if line[-1] == '\n':
                    line = line[:-1]
                [key, value] = line.split('=')
                dic_delay_settings[key] = value
        dic_delay_set = {
            'AOM': self.ui.lineEditAOMDelayTime,
            'MW': self.ui.lineEditMWDelayTime,
        }
        for key, value in dic_delay_settings.items():
            dic_delay_set.get(key).setText(value)

    def save_and_accept(self):
        """
        Call this method when need to save the settings from the file.
        """
        # Save Frequency Sweep Settings
        dir_freq_sweep_settings = os.path.abspath(
            os.path.join(os.path.dirname("__file__"), os.path.pardir, 'Cache/Settings/freq_sweep_settings.txt')
        )
        freq_sweep_settings_list = [
            ('LOOP_NUM', self.ui.lineEditFreqSetNumOfLoop.text()),
            ('AVERAGE_NUM', self.ui.lineEditFreqSetNumOfAverage.text())
        ]
        with open(dir_freq_sweep_settings, 'w') as f_freq_sweep_settings:
            for freq_sweep_settings in freq_sweep_settings_list:
                f_freq_sweep_settings.write(freq_sweep_settings[0] + '=' + freq_sweep_settings[1] + '\n')

        # Save Time Sweep Settings
        dir_time_sweep_settings = os.path.abspath(
            os.path.join(os.path.dirname("__file__"), os.path.pardir, 'Cache/Settings/time_sweep_settings.txt')
        )
        time_sweep_settings_list = [
            ('LOOP_NUM', self.ui.lineEditTimeSetNumOfLoop.text()),
            ('AVERAGE_NUM', self.ui.lineEditTimeSetNumOfAverage.text())
        ]
        with open(dir_time_sweep_settings, 'w') as f_time_sweep_settings:
            for time_sweep_settings in time_sweep_settings_list:
                f_time_sweep_settings.write(time_sweep_settings[0] + '=' + time_sweep_settings[1] + '\n')

        # Save Delay Settings
        dir_delay_settings = os.path.abspath(
            os.path.join(os.path.dirname("__file__"), os.path.pardir, 'Cache/Settings/delay_settings.txt')
        )
        delay_settings_list = [
            ('AOM', self.ui.lineEditAOMDelayTime.text()),
            ('MW', self.ui.lineEditMWDelayTime.text())
        ]
        with open(dir_delay_settings, 'w') as f_delay_settings:
            for delay_settings in delay_settings_list:
                f_delay_settings.write(delay_settings[0] + '=' + delay_settings[1] + '\n')

        # Accept Function
        self.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    myWindow = Setting_GUI()
    myWindow.show()

    sys.exit(app.exec_())
