"""
Created on Sep 27, 2023

This File is the dialog of Rotation Stage Settings. Including the connection of the methods and the function.
This work need the pyUI file of RotationStageSetting

@author: Linjie
"""

import sys
import os
from pathlib import Path

from ui.uipy.pulse_ESR_polarization.RotationStageSettings import Ui_Settings
from PyQt5 import QtCore, QtWidgets


def find_project_root(current_path, marker_files=("README.md", ".git")):
    for parent in current_path.parents:
        if any((parent / marker).exists() for marker in marker_files):
            print(parent)
            return parent
    return current_path


class RotationStageSetting_GUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.project_dir = find_project_root(current_path=Path(__file__).resolve())

        self.ui.buttonBox.accepted.connect(self.save_and_accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.load_settings()

    def load_settings(self):
        """
        Load the settings stored in './Cache/Settings,rotation_settings.txt'.
        """
        # Load rotation stage settings
        dir_rotation_settings = os.path.join(self.project_dir,
                                             'config\\config_pulse_ESR_polarization\\Settings\\rotation_settings.txt')
        with open(dir_rotation_settings, 'r') as f_rotation_settings:
            file_read = f_rotation_settings.readlines()
            dic_rotation_settings = {}

            for line in file_read[:4]:
                if line[-1] == '\n':
                    line = line[:-1]
                [key, value] = line.split('=')
                dic_rotation_settings[key] = value

            dic_rotation_ttl_settings = {}
            for line in file_read[4:6]:
                if line[-1] == '\n':
                    line = line[:-1]
                [key, value] = line.split('=')
                if value == 'ENABLED':
                    dic_rotation_ttl_settings[key] = bool(True)
                elif value == 'DISABLED':
                    dic_rotation_ttl_settings[key] = bool(False)

        dic_rotation_set = {
            'MOVE_SPEED': self.ui.leMovingSpeed,
            'MOVE_ACCELERATION': self.ui.leMovingAcceleration,
            'SCAN_SPEED': self.ui.leScanningSpeed,
            'SCAN_ACCELERATION': self.ui.leScanningAcceleration,
        }
        dic_rotation_ttl_set = {
            'TTL_INPUT': self.ui.cbTTLInput,
            'TTL_OUTPUT': self.ui.cbTTLOutput,
        }
        for key, value in dic_rotation_settings.items():
            dic_rotation_set.get(key).setText(value)
        for key, value in dic_rotation_ttl_settings.items():
            dic_rotation_ttl_set.get(key).setCheckState(value)

    def save_and_accept(self):
        dir_rotation_settings = os.path.join(self.project_dir,
                                             'config\\config_pulse_ESR_polarization\\Settings\\rotation_settings.txt')
        rotation_settings_list = [
            ('MOVE_SPEED', self.ui.leMovingSpeed.text()),
            ('MOVE_ACCELERATION', self.ui.leMovingAcceleration.text()),
            ('SCAN_SPEED', self.ui.leScanningSpeed.text()),
            ('SCAN_ACCELERATION', self.ui.leScanningAcceleration.text())
        ]
        rotation_ttl_settings_list = [
            ('TTL_INPUT', self.ui.cbTTLInput.isChecked()),
            ('TTL_OUTPUT', self.ui.cbTTLOutput.isChecked())
        ]
        with open(dir_rotation_settings, 'w') as f_rotation_settings:
            for rotation_settings in rotation_settings_list:
                f_rotation_settings.write(rotation_settings[0] + '=' + rotation_settings[1] + '\n')
            for rotation_ttl_settings in rotation_ttl_settings_list:
                if rotation_ttl_settings[1] is True:
                    f_rotation_settings.write(rotation_ttl_settings[0] + '=' + 'ENABLED' + '\n')
                elif rotation_ttl_settings[1] is False:
                    f_rotation_settings.write(rotation_ttl_settings[0] + '=' + 'DISABLED' + '\n')

        # accept function
        self.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    myWindow = RotationStageSetting_GUI()
    myWindow.show()

    sys.exit(app.exec_())
