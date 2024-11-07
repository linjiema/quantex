"""
Created on Jun 30, 2021

This File is the Main Thread for Pulse ODMR

@author: Linjie
"""
import math
import sys
import os
import time
from pathlib import Path

from ui.uipy.pulse_ESR.MainWindow import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore

from src.interface.pulse_ESR.qt_dialog.Settings_dialog import Setting_GUI as SettingsDialog
from src.interface.pulse_ESR.qt_dialog.SeqEditor_dialog import SeqEditor_GUI as SeqEditorDialog

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation

from src.threads.pulse_ESR_threads import FrequencySweepThread, TimeSweepThread, DataThread, TrackThread


def find_project_root(current_path, marker_files=("README.md", ".git")):
    for parent in current_path.parents:
        if any((parent / marker).exists() for marker in marker_files):
            print(parent)
            return parent
    return current_path


class mainGUI(QtWidgets.QMainWindow):
    SIGNAL_ExpESRClose = QtCore.pyqtSignal(name='ExpESRClose')

    def __init__(self, parent=None, hardware=None):
        QtWidgets.QWidget.__init__(self, parent)
        # Setup GUI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Define some parameters need to be used in the program
        self.project_dir = find_project_root(current_path=Path(__file__).resolve())
        self.seq_dir = None  # The directory of the pulse sequence txt file
        self.pulse_seq = None  # The pulse sequence (list) that using for generate and using in the main thread
        self.pulse_name = None  # The name of the pulse sequence
        self.pause_status = False  # The parameter to show if the state is pause. Important for the pulse function
        # Process for initialization
        self.load_defaults()  # Load defaults
        self.connect_methods()  # Connect methods to slots
        self.init_button_status()  # Init the state of buttons and textbox
        self.init_data_plot()  # Init the plot for Data
        self.init_seq_plot()  # Init the plot for Pulse Sequence
        self.init_track_plot()  # Init the plot for Tracking
        # Hardware
        self.hardware = hardware

    # Methods for initialization
    def connect_methods(self):
        """
        This method connects methods to the slots
        :return: None
        """
        # Menu Bar
        self.ui.actionSettings.triggered.connect(self.open_setting_dialog)
        self.ui.actionSave_Defaults.triggered.connect(self.save_defaults)
        self.ui.actionLoad_Defaults.triggered.connect(self.load_defaults)
        # Data Group
        self.ui.pbSaveData.clicked.connect(self.save_data)
        # Track Group
        self.ui.leTrackingThreshold.editingFinished.connect(self.change_auto_track_status)
        self.ui.checkBoxAutoTrack.stateChanged.connect(self.change_auto_track_status)
        self.ui.pbTrack.clicked.connect(self.manual_track)
        # Scan Status Group
        self.ui.pbSetScanningStatus.clicked.connect(self.set_scanning_status)
        # Pulse Group
        self.ui.pbNewPulseSeq.clicked.connect(self.new_pulse_seq)
        self.ui.pbLoadPulseSeq.clicked.connect(self.load_pulse_seq)
        self.ui.pbAnimateSeq.clicked.connect(self.animate_seq_start)
        self.ui.pbEditPulseSeq.clicked.connect(self.edit_pulse_seq)
        # Microwave Group
        self.ui.pbMWPowerOn.clicked.connect(self.open_microwave)
        self.ui.pbMWPowerOff.clicked.connect(self.close_microwave)
        self.ui.checkBoxUseScan.stateChanged.connect(self.change_scan_mode)
        self.ui.leStartFreqSetting.editingFinished.connect(self.generate_sweep_points_and_replot)
        self.ui.leEndFreqSetting.editingFinished.connect(self.generate_sweep_points_and_replot)
        self.ui.leStepSetting.editingFinished.connect(self.generate_sweep_points_and_replot)
        # Time Group
        # Linear
        self.ui.leTimeStart.editingFinished.connect(self.update_time_step_num)
        self.ui.leTimeEnd.editingFinished.connect(self.update_time_step_num)
        self.ui.leTimeStep.editingFinished.connect(self.update_time_step_num)
        self.ui.leNumberOfStep.editingFinished.connect(self.update_time_step)
        # Exponential
        self.ui.tabWidget.currentChanged.connect(self.check_and_update_plot)
        self.ui.leTimeStart_exp.editingFinished.connect(self.check_and_update_plot)
        self.ui.leTimeEnd_exp.editingFinished.connect(self.check_and_update_plot)
        self.ui.leNumberOfStep_exp.editingFinished.connect(self.check_and_update_plot)

        # Hardware Group
        self.ui.pbInit.clicked.connect(self.init_hardware)
        self.ui.pbReset.clicked.connect(self.reset_hardware)
        # Experiment Group
        self.ui.pbExpStart.clicked.connect(self.start_scan)
        self.ui.pbExpStop.clicked.connect(self.stop_scan)

    def init_button_status(self):
        """
        This method set the state of buttons and textbox to initial state.
        :return: None
        """
        # Data Group
        self.ui.pbSaveData.setEnabled(False)
        self.ui.checkBoxAutoSave.setEnabled(False)
        # Experiment Group
        self.ui.pbExpStart.setEnabled(False)
        self.ui.pbExpStop.setEnabled(False)
        # Hardware Group
        self.ui.pbInit.setEnabled(True)
        self.ui.pbReset.setEnabled(False)
        # Microwave Group
        self.ui.pbMWPowerOn.setEnabled(False)
        self.ui.pbMWPowerOff.setEnabled(False)
        self.ui.checkBoxUseScan.setEnabled(False)
        # Scanning Status Group
        self.ui.pbSetScanningStatus.setEnabled(False)
        self.ui.leTotalPointNum.setEnabled(False)
        # Tracking Group
        self.ui.pbTrack.setEnabled(False)
        self.ui.checkBoxAutoTrack.setEnabled(False)
        self.ui.leTrackingThreshold.setEnabled(False)
        # Pulse Group
        self.ui.pbAnimateSeq.setEnabled(False)
        self.ui.pbEditPulseSeq.setEnabled(False)

    def init_data_plot(self):
        """
        Init the plot for Data.
        :return: None
        """
        # Set canvas
        fig1 = Figure()
        self.ui.data_fig = FigureCanvas(fig1)
        self.ui.data_fig.setParent(self.ui.widgetScanData)
        self.ui.data_fig.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), self.ui.widgetScanData.size()))
        self.ui.data_fig.axes = fig1.add_subplot(111)
        self.ui.data_fig.figure.subplots_adjust(top=0.95, bottom=0.15, right=0.95)
        # Init plot
        self.ref_plot, = self.ui.data_fig.axes.plot(self.time_sweep, self.ref_ave, 'r')
        self.sig_plot, = self.ui.data_fig.axes.plot(self.time_sweep, self.sig_ave, 'b')
        # Set fig parameters
        self.ui.data_fig.axes.set_xlabel('Time (ns)')
        self.ui.data_fig.axes.set_ylabel('Counts')
        self.ui.data_fig.axes.set_xlim(0, np.max(self.time_sweep) * 1.01)
        self.ui.data_fig.draw()

    def init_seq_plot(self):
        """
        Init the plot for Pulse Sequence.
        :return: None
        """
        fig2 = Figure()
        self.ui.seq_fig = FigureCanvas(fig2)
        self.ui.seq_fig.setParent(self.ui.widgetPulseSeqDisplay)
        self.ui.seq_fig.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), self.ui.widgetPulseSeqDisplay.size()))
        self.ui.seq_fig.axes = fig2.add_subplot(111)

    def init_track_plot(self):
        """
        Init the plot for Tracking.
        :return: None
        """
        fig3 = Figure()
        self.ui.track_fig = FigureCanvas(fig3)
        self.ui.track_fig.setParent(self.ui.widgetTrackingPlot)
        self.ui.track_fig.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), self.ui.widgetTrackingPlot.size()))
        # init x_plot
        self.ui.track_fig.x_plot = fig3.add_subplot(131)
        self.ui.track_fig.x_plot.set_title('X Axis')
        # init y_plot
        self.ui.track_fig.y_plot = fig3.add_subplot(132)
        self.ui.track_fig.y_plot.set_title('Y Axis')
        # init z_plot
        self.ui.track_fig.z_plot = fig3.add_subplot(133)
        self.ui.track_fig.z_plot.set_title('Z Axis')

    # Methods for Menu Bar
    def open_setting_dialog(self):
        """
        Methods for run the Setting Dialog
        :return: None
        """
        setting_dialog = SettingsDialog()
        # Get the exit state
        val = setting_dialog.exec_()
        # Reload the Settings again if click 'OK' in Setting Dialog
        if val == 1:
            self.load_delay_settings()
            self.load_scanning_settings(state=self.ui.checkBoxUseScan.isChecked())
            self.ui.statusbar.showMessage('Settings saved.')
        elif val == 0:
            self.ui.statusbar.showMessage('Settings withdraw.')

    def load_defaults(self):
        """
        This methods load the defaults of Microwave and Time Scan.
        This methods also call the methods that load the delay settings and Scanning Settings.
        :return: None
        """
        # Load Microwave Defaults
        # Get the absolute path of the Microwave Defaults
        dir_mw_defaults = os.path.join(self.project_dir,
                                       'config\\config_pulse_ESR\\Defaults\\microwave_defaults.txt')

        # Read the Microwave Defaults
        with open(dir_mw_defaults, 'r') as f_mw_defaults:
            dic_mw_defaults = {}
            for line in f_mw_defaults.readlines():
                if line[-1] == '\n':
                    line = line[:-1]
                [key, value] = line.split('=')
                dic_mw_defaults[key] = value
        # Pass the Microwave Defaults into the GUI
        dic_mw_set = {
            'FREQUENCY': self.ui.leFixedFreqSetting,
            'POWER': self.ui.leMWPowerSetting,
            'START': self.ui.leStartFreqSetting,
            'END': self.ui.leEndFreqSetting,
            'STEP': self.ui.leStepSetting
        }
        for key, value in dic_mw_defaults.items():
            dic_mw_set.get(key).setText(value)

        # Load Time Defaults
        # Get the absolute path of the Time Defaults
        dir_time_defaults = os.path.join(self.project_dir,
                                         'config\\config_pulse_ESR\\Defaults\\time_defaults.txt')
        # Read the Time Defaults
        with open(dir_time_defaults, 'r') as f_time_defaults:
            dic_time_defaults = {}
            for line in f_time_defaults.readlines():
                if line[-1] == '\n':
                    line = line[:-1]
                [key, value] = line.split('=')
                dic_time_defaults[key] = value
        # Pass the Time Defaults into the GUI
        dic_time_set = {
            'START': self.ui.leTimeStart,
            'END': self.ui.leTimeEnd,
            'STEP': self.ui.leTimeStep,
            'STEP_NUM': self.ui.leNumberOfStep,
            'START_EXP': self.ui.leTimeStart_exp,
            'END_EXP': self.ui.leTimeEnd_exp,
            'STEP_NUM_EXP': self.ui.leNumberOfStep_exp
        }
        for key, value in dic_time_defaults.items():
            dic_time_set.get(key).setText(value)
        # Load delay Settings
        self.load_delay_settings()
        # Load scanning settings
        self.load_scanning_settings(state=self.ui.checkBoxUseScan.isChecked())

    def save_defaults(self):
        """
        This methods save the defaults of Microwave and Time Scan.
        This methods also call the methods that save the Scanning Settings.
        :return: None
        """
        # Save Microwave Defaults
        # Get the absolute path of the Microwave Defaults File
        dir_mw_defaults = os.path.join(self.project_dir,
                                       'config\\config_pulse_ESR\\Defaults\\microwave_defaults.txt')
        # Read the Microwave Defaults from the GUI
        mw_defaults_list = [
            ('FREQUENCY', self.ui.leFixedFreqSetting.text()),
            ('POWER', self.ui.leMWPowerSetting.text()),
            ('START', self.ui.leStartFreqSetting.text()),
            ('END', self.ui.leEndFreqSetting.text()),
            ('STEP', self.ui.leStepSetting.text())
        ]
        # Write the Microwave Defaults into the txt file
        with open(dir_mw_defaults, 'w') as f_mw_defaults:
            for mw_defaults in mw_defaults_list:
                f_mw_defaults.write(mw_defaults[0] + '=' + mw_defaults[1] + '\n')

        # Save Time Defaults
        # Get the absolute path of the Time Defaults File
        dir_time_defaults = os.path.join(self.project_dir,
                                         'config\\config_pulse_ESR\\Defaults\\time_defaults.txt')
        # Read the Time Defaults from the GUI
        time_defaults_list = [
            ('START', self.ui.leTimeStart.text()),
            ('END', self.ui.leTimeEnd.text()),
            ('STEP', self.ui.leTimeStep.text()),
            ('STEP_NUM', self.ui.leNumberOfStep.text()),
            ('START_EXP', self.ui.leTimeStart_exp.text()),
            ('END_EXP', self.ui.leTimeEnd_exp.text()),
            ('STEP_NUM_EXP', self.ui.leNumberOfStep_exp.text())
        ]
        # Write the Time Defaults into the txt file
        with open(dir_time_defaults, 'w') as f_time_defaults:
            for time_defaults in time_defaults_list:
                f_time_defaults.write(time_defaults[0] + '=' + time_defaults[1] + '\n')
        # Save scanning settings
        self.save_scanning_settings(state=self.ui.checkBoxUseScan.isChecked())

    # Methods for Settings
    def load_delay_settings(self):
        """
        This methods load the Delay Settings.
        :return: None
        """
        # Get the absolute path of the delay settings
        dir_delay = os.path.join(self.project_dir,
                                 'config\\config_pulse_ESR\\Settings\\delay_settings.txt')
        # Read the Time Defaults into dir
        with open(dir_delay, 'r') as f_delay:
            self.dic_delay = {}
            for line in f_delay.readlines():
                if line[-1] == '\n':
                    line = line[:-1]
                [key, value] = line.split('=')
                self.dic_delay[key] = value

    def load_scanning_settings(self, state=True):
        """
        This methods load the Scanning Settings based on state.
        This methods also call the methods to generate sweep points.
        :param state: bool.
            True for Frequency Sweep
            False for Time Sweep
        :return: None
        """
        # Load Frequency Sweep Settings if do Frequency Sweep
        if state is True:
            # Get the absolute path of the Frequency Sweep Settings
            dir_freq_sweep_settings = os.path.join(self.project_dir,
                                                   'config\\config_pulse_ESR\\Settings\\freq_sweep_settings.txt')
            # Read the Frequency Sweep Settings
            with open(dir_freq_sweep_settings, 'r') as f_freq_sweep_settings:
                dic_freq_sweep_settings = {}
                for line in f_freq_sweep_settings.readlines():
                    if line[-1] == '\n':
                        line = line[:-1]
                    [key, value] = line.split('=')
                    dic_freq_sweep_settings[key] = value

            dic_freq_sweep_set = {
                'LOOP_NUM': self.ui.leTotalLoopNum,
                'AVERAGE_NUM': self.ui.leTotalAverageNum,
            }
            # Pass the Frequency Sweep Settings into the GUI
            for key, value in dic_freq_sweep_settings.items():
                dic_freq_sweep_set.get(key).setText(value)

        # Load Time Sweep Settings if do Time Sweep
        else:
            # Get the absolute path of the Time Sweep Settings
            dir_time_sweep_settings = os.path.join(self.project_dir,
                                                   'config\\config_pulse_ESR\\Settings\\time_sweep_settings.txt')
            # Read the Time Sweep Settings
            with open(dir_time_sweep_settings, 'r') as f_time_sweep_settings:
                dic_time_sweep_settings = {}
                for line in f_time_sweep_settings.readlines():
                    if line[-1] == '\n':
                        line = line[:-1]
                    [key, value] = line.split('=')
                    dic_time_sweep_settings[key] = value
            dic_time_sweep_set = {
                'LOOP_NUM': self.ui.leTotalLoopNum,
                'AVERAGE_NUM': self.ui.leTotalAverageNum,
            }
            # Pass the Time Sweep Settings into the GUI
            for key, value in dic_time_sweep_settings.items():
                dic_time_sweep_set.get(key).setText(value)

        # Update point
        self.generate_sweep_points()

    def save_scanning_settings(self, state=True):
        """
        This methods save the Scanning Settings based on state.
        :param state: bool.
            True for Frequency Sweep
            False for Time Sweep
        :return: None
        """
        # Save Frequency Sweep Settings if do Frequency Sweep
        if state is True:
            # Get the absolute path of the Frequency Sweep Settings
            dir_freq_sweep_settings = os.path.join(self.project_dir,
                                                   'config\\config_pulse_ESR\\Settings\\freq_sweep_settings.txt')
            # Read the Frequency Sweep Settings from the GUI
            freq_sweep_settings_list = [
                ('LOOP_NUM', self.ui.leTotalLoopNum.text()),
                ('AVERAGE_NUM', self.ui.leTotalAverageNum.text())
            ]
            # Write the Frequency Sweep Settings into txt file
            with open(dir_freq_sweep_settings, 'w') as f_freq_sweep_settings:
                for freq_sweep_settings in freq_sweep_settings_list:
                    f_freq_sweep_settings.write(freq_sweep_settings[0] + '=' + freq_sweep_settings[1] + '\n')

        # Save Time Sweep Settings if do Time Sweep
        else:
            # Get the absolute path of the Time Sweep Settings
            dir_time_sweep_settings = os.path.join(self.project_dir,
                                                   'config\\config_pulse_ESR\\Settings\\time_sweep_settings.txt')
            # Read the Time Sweep Settings from the GUI
            time_sweep_settings_list = [
                ('LOOP_NUM', self.ui.leTotalLoopNum.text()),
                ('AVERAGE_NUM', self.ui.leTotalAverageNum.text())
            ]
            # Write the Time Sweep Settings into txt file
            with open(dir_time_sweep_settings, 'w') as f_time_sweep_settings:
                for time_sweep_settings in time_sweep_settings_list:
                    f_time_sweep_settings.write(time_sweep_settings[0] + '=' + time_sweep_settings[1] + '\n')

    # Methods for Data Group
    def save_data(self):
        """
        This methods save let the user choose the location, and save the data
        :return: None
        """
        # Get the Raw Data from DataThread
        try:
            self.saved_data = self.dThread.raw
            if self.saved_data is None:
                raise BaseException
        except BaseException:
            sys.stderr.write('No data to be saved!\n')
            return

        # Get saving file path
        dir_data = os.path.join(self.project_dir,
                                'data\\data_pulse_ESR')
        file_name = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        file_path = os.path.join(dir_data, file_name)
        # Call the dialog for saving data, get dir from it
        dir_save_data = QtWidgets.QFileDialog.getSaveFileName(self, 'Enter save file',
                                                              file_path, 'Text (*.txt)')

        self.saved_data[4][1] = self.ui.leCurrentLoopNum.text()
        self.saved_data[4][3] = self.ui.leCurrentPointNum.text()
        # Reshape the dir
        dir_save_data = str(dir_save_data[0].replace('/', '\\'))
        # Save Data
        if dir_save_data != '':
            # Write data into txt file
            with open(dir_save_data, 'w') as f_save_data:
                # Write Data Version, Pulse Sequence, Experiment time, Scanning Mode, Total Loop Number, Point per
                # loop, Seq repeat time and tittle of the data at the beginning of the data file.
                for each_description in self.saved_data[:7]:
                    for i in range(len(each_description)):
                        f_save_data.write(str(each_description[i]))
                        f_save_data.write('\t')
                    f_save_data.write('\n')
                # Write Data into the txt file
                for each_dataloop in self.saved_data[7]:
                    for each_datapoint in each_dataloop:
                        f_save_data.write(str(each_datapoint[0]) + '\t' + str(each_datapoint[1]) + '\t' +
                                          str(each_datapoint[2]) + '\t' + str(each_datapoint[3]) + '\n')
        else:
            sys.stderr.write('No File is saved!\n')

    def init_raw_data(self, state):
        """
        Init the raw data for the scan.
        This method will also write the scanning parameters at the beginning of the data
        :param state: bool.
            True for Frequency Sweep
            False for Time Sweep
        :return: None
        """
        # Init a new list fpr raw data
        self.dThread.raw = []
        # Create raw data list for Frequency Sweep Settings
        if state is True:
            self.dThread.raw.append(['DATA_VERSION:', '2.1'])
            self.dThread.raw.append(['Pulse_sequence:', self.pulse_seq])
            self.dThread.raw.append(['Experiment time:', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                     'Scanning Mode:', 'Frequency Sweep'])
            self.dThread.raw.append(['Total Loop:', self.ui.leTotalLoopNum.text(),
                                     'Point per loop:', self.ui.leTotalPointNum.text(),
                                     'Seq Repeat time:', self.ui.leTotalAverageNum.text()])
            self.dThread.raw.append(['Loop:', '0', 'Point:', '0'])
            if self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Linear':
                self.dThread.raw.append(['Data Mode:', 'Linear'])
            elif self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Exponential':
                self.dThread.raw.append(['Data Mode:', 'Exponential'])
            self.dThread.raw.append(['Signal', 'Reference', 'Frequency(MHz)', 'Loop Num'])
            self.dThread.raw.append(np.zeros((int(self.ui.leTotalLoopNum.text()),
                                              int(self.ui.leTotalPointNum.text()),
                                              int(4)),
                                             dtype=float).tolist()
                                    )
        # Create raw data list for Time Sweep Settings
        else:
            self.dThread.raw.append(['DATA_VERSION:', '2.1'])
            self.dThread.raw.append(['Pulse_sequence:', self.pulse_seq])
            self.dThread.raw.append(['Experiment time:', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                     'Scanning Mode:', 'Time Sweep'])
            self.dThread.raw.append(['Total Loop:', self.ui.leTotalLoopNum.text(),
                                     'Point per loop:', self.ui.leTotalPointNum.text(),
                                     'Seq Repeat time:', self.ui.leTotalAverageNum.text()])
            self.dThread.raw.append(['Loop:', '0', 'Point:', '0'])
            if self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Linear':
                self.dThread.raw.append(['Data Mode:', 'Linear'])
            elif self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Exponential':
                self.dThread.raw.append(['Data Mode:', 'Exponential'])
            self.dThread.raw.append(['Signal', 'Reference', 'Time(ns)', 'Loop Num'])
            self.dThread.raw.append(np.zeros((int(self.ui.leTotalLoopNum.text()),
                                              int(self.ui.leTotalPointNum.text()),
                                              int(4)),
                                             dtype=float).tolist()
                                    )

    # Methods for Track Group
    @QtCore.pyqtSlot()
    def change_auto_track_status(self):
        """
        Call this method when Auto_Track checkbox check status changes
        :return: None
        """
        if self.ui.checkBoxUseScan.isChecked() is True:
            self.fsThread.auto_track = self.ui.checkBoxAutoTrack.isChecked()
            self.fsThread.threshold = int(self.ui.leTrackingThreshold.text())
        else:
            self.tsThread.auto_track = self.ui.checkBoxAutoTrack.isChecked()
            self.tsThread.threshold = int(self.ui.leTrackingThreshold.text())

    def manual_track(self):
        """
        Run the Track Thread
        :return: None
        """
        self.tThread.start()
        if self.ui.checkBoxUseScan.isChecked() is True:
            self.fsThread.pulse_init_status = False

    # Methods for Scanning Status Group
    @QtCore.pyqtSlot()
    def set_scanning_status(self):
        """
        Call this Method when push the set_status buttons
        Set the location of the temp scanning
        :return: None
        """
        if self.ui.checkBoxUseScan.isChecked() is True:
            self.fsThread.loop_num[0] = int(self.ui.leCurrentLoopNum.text()) - 1
            self.fsThread.point_num[0] = int(self.ui.leCurrentPointNum.text()) - 1
        else:
            self.tsThread.loop_num[0] = int(self.ui.leCurrentLoopNum.text()) - 1
            self.tsThread.point_num[0] = int(self.ui.leCurrentPointNum.text()) - 1

    # Methods for Pulse Group
    def new_pulse_seq(self):
        """
        This method run the SeqEditor and create a blank sequence.
        If click 'OK' in SeqEditor Dialog, call the method to load the new seq.
        :return: None
        """
        seq_dir_temp = os.path.join(self.project_dir,
                                    'cache\\cache_pulse_ESR\\temp\\Untitled.txt')
        # New a file for saving the seq
        with open(seq_dir_temp, 'w') as f_new:
            pass
        # Open the SeqEditor Dialog
        seq_editor_dialog = SeqEditorDialog(seq_dir=seq_dir_temp, parent=self)
        # Get the exit status
        val = seq_editor_dialog.exec_()
        # Load the new seq if click 'OK' in SeqEditor Dialog
        if val == 1:
            self.seq_dir = seq_editor_dialog.seq_dir
            self.load_pulse_seq(seq_dir=self.seq_dir)

    def edit_pulse_seq(self):
        """
        This method run the SeqEditor and edit the Pulse Sequence.
        :return: None
        """
        # Open the SeqEditor Dialog and pass the Pulse Sequence into it
        seq_editor_dialog = SeqEditorDialog(seq_dir=self.seq_dir, parent=self)
        val = seq_editor_dialog.exec_()
        # Load the new seq if click 'OK' in SeqEditor Dialog
        if val == 1:
            self.seq_dir = seq_editor_dialog.seq_dir
            self.load_pulse_seq(seq_dir=self.seq_dir)

    def load_pulse_seq(self, seq_dir):
        """
        This method load the Pulse Seq, change the name display in textbox.
        This method will also update the plot for Pulse Sequence.
        :param seq_dir: The absolute dir of the Pulse Sequence txt file
        :return: None
        """
        if seq_dir is False:
            # Get seq file dir
            default_path = os.path.join(self.project_dir,
                                        'config\\config_pulse_ESR\\PulseSeq')
            # Get the directory
            dir_pulse_seq_load = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Sequence',
                                                                       default_path,
                                                                       'Text files(*.txt)')
            dir_pulse_seq_load = str(dir_pulse_seq_load[0].replace('/', '\\'))
            # Move back to file dir
        else:
            dir_pulse_seq_load = seq_dir
        # Load Sequence
        if dir_pulse_seq_load != '':
            # Record the dir
            self.seq_dir = dir_pulse_seq_load
            with open(dir_pulse_seq_load, 'r') as f_pulse_seq_load:
                self.pulse_seq = []
                for each_pulse in f_pulse_seq_load.readlines():
                    each_pulse = each_pulse.replace('\n', '').replace('[', '').replace(']', '').replace("'", '')
                    self.pulse_seq.append(each_pulse.split(','))
            # Load the name of seq
            self.pulse_name = dir_pulse_seq_load.split('\\')[-1].replace('.txt', '')
            self.ui.lePulseSeqName.setText(self.pulse_name)
            # Update the plot
            self.update_pulse_seq_plot()
            # Enable Animate Pushbutton
            self.ui.pbAnimateSeq.setEnabled(True)
            self.ui.pbEditPulseSeq.setEnabled(True)
            self.animate_seq_stop()

    def update_pulse_seq_plot(self):
        """
        This Method update the plot for Pulse Sequence
        :return: None
        """
        # Process sequence data
        end_max = 0
        for each_pulse in self.pulse_seq:
            end = int(each_pulse[-1].split('+')[0])
            if end > end_max:
                end_max = end
        x_arr_plot = range(end_max + 1)
        # Init the y lists
        y_arrs_plot = [[0] * (end_max + 1), [2] * (end_max + 1), [4] * (end_max + 1), [6] * (end_max + 1)]
        dic_channel = {
            'Ref': y_arrs_plot[0],
            'Sig': y_arrs_plot[1],
            'Laser': y_arrs_plot[2],
            'MicroWave': y_arrs_plot[3],
        }
        # Adjust the y value for each channel based on each seq store in the self.seq
        for each_pulse in self.pulse_seq:
            channel_seq = dic_channel.get(each_pulse[0])
            start = int(each_pulse[1].split('+')[0])
            stop = int(each_pulse[2].split('+')[0])
            # Define the Open time of each Channel
            for i in range(start, stop):
                # Prevent add multi pulse at same time point
                if channel_seq[i] % 2 == 0:
                    channel_seq[i] += 1
        # paint sequence
        self.ui.seq_fig.figure.clear()
        self.ui.seq_fig.axes = self.ui.seq_fig.figure.add_subplot(111)
        self.ui.seq_fig.axes.plot(x_arr_plot, y_arrs_plot[0], 'b-',
                                  x_arr_plot, y_arrs_plot[1], 'k-',
                                  x_arr_plot, y_arrs_plot[2], 'g-',
                                  x_arr_plot, y_arrs_plot[3], 'r-')
        self.ui.seq_fig.axes.set_ylim(-0.5, 7.5)
        self.ui.seq_fig.draw()

    def animate_seq_start(self):
        """
        Animate the Pulse Sequence plot.
        :return: None
        """
        # Change button status
        self.ui.pbAnimateSeq.clicked.disconnect()
        self.ui.pbAnimateSeq.clicked.connect(self.animate_seq_stop)
        self.ui.pbAnimateSeq.setText('Stop Animate')
        # Make preparation
        self.ui.seq_fig.figure.clear()
        start_time = int(self.ui.leTimeStart.text())
        step_time = int(self.ui.leTimeStep.text())
        stop_time = int(self.ui.leTimeEnd.text())
        step_num = int((stop_time - start_time) / step_time) + 1
        end_max = 0
        # get data for animation
        for each_pulse in self.pulse_seq:
            if '+' in each_pulse[-1]:
                s1, s2 = each_pulse[-1].split('+')
            else:
                s1 = each_pulse[-1]
                s2 = '0'

            if s2 == 't':
                t = int(s1) + stop_time
            else:
                t = int(s1) + stop_time * int(s2.replace('t', ''))
            # Update end_max
            if t > end_max:
                end_max = t
        seq_animate_arr = np.zeros((4, step_num, end_max), dtype=int)
        dic_channel = {'Ref': seq_animate_arr[0],
                       'Sig': seq_animate_arr[1],
                       'Laser': seq_animate_arr[2],
                       'MicroWave': seq_animate_arr[3],
                       }

        for pulse in self.pulse_seq:
            channel = dic_channel.get(pulse[0])
            for n in range(step_num):
                if '+' in pulse[1]:
                    s1, s2 = pulse[1].split('+')
                    if s2 == 't':
                        start = int(s1) + start_time + step_time * n
                    else:
                        start = int(s1) + (start_time + step_time * n) * int(s2.replace('t', ''))
                else:
                    start = int(pulse[1])

                if '+' in pulse[2]:
                    s1, s2 = pulse[2].split('+')
                    if s2 == 't':
                        stop = int(s1) + start_time + step_time * n
                    else:
                        stop = int(s1) + (start_time + step_time * n) * int(s2.replace('t', ''))
                else:
                    stop = int(pulse[2])
                for i in range(start - 1, stop - 1):
                    if channel[n][i] == 0:
                        channel[n][i] = 1

        rise = np.ones((step_num, end_max), dtype=int) * 2
        seq_animate_arr[1] += rise
        seq_animate_arr[2] += rise * 2
        seq_animate_arr[3] += rise * 3
        # paint picture
        animate_fig = self.ui.seq_fig.figure
        self.animate_ax = animate_fig.gca()
        self.animate_ax.set_xlim(0, end_max)
        self.animate_ax.set_ylim(-0.5, 7.5)
        l1, l2, l3, l4, = self.animate_ax.plot([], [], 'b-',
                                               [], [], 'k-',
                                               [], [], 'g-',
                                               [], [], 'r-')
        self.ani = FuncAnimation(animate_fig, self.animate_seq_update,
                                 frames=step_num, init_func=self.animate_seq_init,
                                 fargs=(seq_animate_arr, l1, l2, l3, l4),
                                 interval=50, repeat_delay=1000, blit=True)
        self.ui.seq_fig.draw()

    def animate_seq_stop(self):
        """
        Stop the Animate.
        :return: None
        """
        # Stop animate
        try:
            self.ui.seq_fig.close_event()
        except BaseException as e:
            pass
        else:
            self.update_pulse_seq_plot()

        # Reset the button
        self.ui.pbAnimateSeq.clicked.disconnect()
        self.ui.pbAnimateSeq.clicked.connect(self.animate_seq_start)
        self.ui.pbAnimateSeq.setText('Animate')

    def animate_seq_update(self, num, seq_data, c1, c2, c3, c4):
        """
        Function inside the animate.
        :param num:
        :param seq_data:
        :param c1:
        :param c2:
        :param c3:
        :param c4:
        :return: c1, c2, c3, c4,
        """
        # update data for painting
        c1.set_ydata(seq_data[0][num])
        c2.set_ydata(seq_data[1][num])
        c3.set_ydata(seq_data[2][num])
        c4.set_ydata(seq_data[3][num])
        c1.set_xdata(range(len(seq_data[0][num])))
        c2.set_xdata(range(len(seq_data[1][num])))
        c3.set_xdata(range(len(seq_data[2][num])))
        c4.set_xdata(range(len(seq_data[3][num])))
        return c1, c2, c3, c4,

    def animate_seq_init(self):
        """
        Function inside the animate.
        :return: initial_data
        """
        # Initial animate data
        initial_data = self.animate_ax.plot([], [], 'b-',
                                            [], [], 'k-',
                                            [], [], 'g-',
                                            [], [], 'r-')
        return initial_data

    # Methods for Microwave Group
    @QtCore.pyqtSlot()
    def open_microwave(self):
        """
        Turn on the Microwave Source
        :return: None
        """
        # self.hardware.mw_source.init_port()
        self.hardware.mw_source.set_power(power=float(self.ui.leMWPowerSetting.text()))
        self.hardware.mw_source.switch(state=True)
        self.hardware.pulser.mw_switch_off()
        # Set the Button
        # Microwave Group
        self.ui.pbMWPowerOn.setEnabled(False)
        self.ui.pbMWPowerOff.setEnabled(True)
        self.ui.leMWPowerSetting.setEnabled(False)
        self.ui.leFixedFreqSetting.setEnabled(False)
        # Experiment Group
        # self.ui.pbExpStart.setEnabled(True)

    @QtCore.pyqtSlot()
    def close_microwave(self):
        """
        Turn off the Microwave Source
        :return: None
        """
        self.hardware.mw_source.switch(state=False)
        # Set the Button
        # Microwave Group
        self.ui.pbMWPowerOn.setEnabled(True)
        self.ui.pbMWPowerOff.setEnabled(False)
        self.ui.leMWPowerSetting.setEnabled(True)
        self.ui.leFixedFreqSetting.setEnabled(True)
        # Experiment Group
        # self.ui.pbExpStart.setEnabled(False)
        # self.ui.pbExpStop.setEnabled(False)

    @QtCore.pyqtSlot()
    def change_scan_mode(self):
        """
        Call this method when the scanning mode is changed.
        This method will replot the Data Plot
        :return: None
        """
        self.save_scanning_settings(state=bool(1 - self.ui.checkBoxUseScan.isChecked()))
        self.load_scanning_settings(state=self.ui.checkBoxUseScan.isChecked())
        self.replot_data()

    def set_power(self):
        """
        Try to set Microwave output power
        :return: None
        """
        power = float(self.ui.leMWPowerSetting.text())
        try:
            self.hardware.mw_source.set_power(power=power)
        except BaseException as e:
            print(e)
            return

    def set_fix_freq(self):
        """
        Try to set Microwave output Frequency
        :return:
        """
        freq = float(self.ui.leFixedFreqSetting.text())
        try:
            self.hardware.mw_source.set_freq(freq=freq)
        except BaseException as e:
            print(e)
            return

    # Methods for Time Group
    def update_time_step_num(self):
        """
        Call this Method to update the time step Number based on other data.
        :return: None
        """
        # Read StartPoint, EndPoint, Step from the GUI
        start = int(self.ui.leTimeStart.text())
        end = int(self.ui.leTimeEnd.text())
        step = int(self.ui.leTimeStep.text())
        # Calculate and set the Step Number based on other data
        if step == 0 or (end - start) < 0:
            self.ui.leNumberOfStep.setText('NA')
        else:
            step_num = int((end - start) / step)
            self.ui.leNumberOfStep.setText(str(step_num))
            self.generate_sweep_points_and_replot()

    def update_time_step(self):
        """
        Call this Method to update the time step based on other data.
        :return: None
        """
        # Read StartPoint, EndPoint, Step Number from the GUI
        start = int(self.ui.leTimeStart.text())
        end = int(self.ui.leTimeEnd.text())
        step_num = int(self.ui.leNumberOfStep.text())
        # Calculate and set the Time Step based on other data
        if step_num == 0 or (end - start) < 0:
            self.ui.leTimeStep.setText('NA')
        else:
            step = int((end - start) / step_num)
            self.ui.leTimeStep.setText(str(step))
            self.generate_sweep_points_and_replot()

    # Methods for Hardware Group
    @QtCore.pyqtSlot()
    def init_hardware(self):
        """
        Init all hardware and pass them to Threads
        :return:
        """
        self.ui.statusbar.showMessage('Initializing Hardware...')
        try:
            self.hardware.init_pulser()
            self.hardware.init_counter()
            self.hardware.init_ni()
            self.hardware.init_mw_source()
            self.hardware.init_scanner()
            # Init microwave source
            self.hardware.init_mw_source()
            self.hardware.mw_source.switch(state=False)
            # Initialize Threads
            # Pass hardware to Threads and connect the function
            # Tracking Thread
            self.tThread = TrackThread(self.hardware)
            self.tThread.tracking_data.connect(self.update_tracking_result)
            # Frequency Sweep Thread
            self.fsThread = FrequencySweepThread(self.hardware)
            self.fsThread.update.connect(self.exp_data_back)
            self.fsThread.finished.connect(self.scan_stop)
            # Time Sweep Thread
            self.tsThread = TimeSweepThread(self.hardware)
            self.tsThread.update.connect(self.exp_data_back)
            self.tsThread.finished.connect(self.scan_stop)
            # Data Thread
            self.dThread = DataThread(self.hardware)
            self.dThread.update.connect(self.update_base_on_data)
        except BaseException as e:
            print(e)
            self.ui.statusbar.showMessage('Hardware Initialization Failed')
            return
        try:
            self.hardware.init_mover()
        except BaseException as e:
            self.ui.statusbar.showMessage('Piezo Stage Initialization Failed')

        # Enable Buttons
        # Data Group
        self.ui.pbSaveData.setEnabled(True)
        self.ui.checkBoxAutoSave.setEnabled(True)
        # Experiment Group
        self.ui.pbExpStart.setEnabled(True)
        self.ui.pbExpStop.setEnabled(False)
        # Hardware Group
        self.ui.pbInit.setEnabled(False)
        self.ui.pbReset.setEnabled(True)
        # Microwave Group
        self.ui.pbMWPowerOn.setEnabled(True)
        self.ui.pbMWPowerOff.setEnabled(False)
        self.ui.checkBoxUseScan.setEnabled(True)
        # Tracking Group
        self.ui.pbTrack.setEnabled(True)
        self.ui.checkBoxAutoTrack.setEnabled(True)
        self.ui.leTrackingThreshold.setEnabled(True)

        # Set textbox
        self.ui.leTrackingThreshold.setText('0')

        # Change the Status Bar Message
        self.ui.statusbar.showMessage('Hardware Initialized Successfully')

    @QtCore.pyqtSlot()
    def reset_hardware(self):
        """
        This Method set the status of all the push button to init status.
        :return: None
        """
        # Reset all the hardware: Microwave Source
        self.ui.statusbar.showMessage('Reset Hardware...')
        self.hardware.reset_pulser()
        self.hardware.reset_counter()
        self.hardware.reset_ni()
        self.hardware.reset_mw_source()
        self.hardware.reset_scanner()
        self.hardware.reset_mover()

        __status = max(self.hardware.mover_status, self.hardware.scanner_status, self.hardware.pulser_status,
                       self.hardware.counter_status, self.hardware.triggered_location_sensor_status,
                       self.hardware.timer_status, self.hardware.one_time_counter_status,
                       self.hardware.mw_source_status)
        if __status == 0:
            self.ui.statusbar.showMessage('Hardware Reset Successfully.')
        # Enable Buttons
        # Data Group
        self.ui.pbSaveData.setEnabled(False)
        self.ui.checkBoxAutoSave.setEnabled(False)
        # Experiment Group
        self.ui.pbExpStart.setEnabled(False)
        self.ui.pbExpStop.setEnabled(False)
        # Hardware Group
        self.ui.pbInit.setEnabled(True)
        self.ui.pbReset.setEnabled(False)
        # Microwave Group
        self.ui.pbMWPowerOn.setEnabled(False)
        self.ui.pbMWPowerOff.setEnabled(False)
        self.ui.checkBoxUseScan.setEnabled(False)
        # Tracking Group
        self.ui.pbTrack.setEnabled(False)
        self.ui.checkBoxAutoTrack.setEnabled(False)
        self.ui.leTrackingThreshold.setEnabled(False)

        self.ui.statusbar.showMessage('Hardware Reset Succeed!')

    # Methods for Experiment Group
    def start_scan(self):
        """
        This Method Start the Scan.
        :return: None
        """
        self.pause_status = False  # Set the pause state
        self.generate_sweep_points_and_replot()
        # Set the Daq based on the average number
        self.hardware.sample_trigger.average = int(self.ui.leTotalAverageNum.text())
        # Init all the data
        self.init_raw_data(state=self.ui.checkBoxUseScan.isChecked())
        self.dThread.sig_all = []
        self.dThread.ref_all = []
        self.dThread.sig_curve_all = []
        # set old loop num
        self.dThread.loop_old = -1
        # Set Microwave Source
        self.set_power()
        # Set parameters based on scan mode
        if self.ui.checkBoxUseScan.isChecked() is True:
            # Set scan parameters
            # These will not change in one experiment
            self.fsThread.delay = self.dic_delay
            self.fsThread.freq_arr = self.freq_sweep
            self.fsThread.pulse_form = self.pulse_seq
            # These can be changed when pause/resume the experiment
            self.fsThread.loop_num = [0, int(self.ui.leTotalLoopNum.text())]
            self.fsThread.point_num = [0, np.size(self.freq_sweep)]
            # These can be changed during the experiment
            self.fsThread.threshold = int(self.ui.leTrackingThreshold.text())
            self.fsThread.auto_track = self.ui.checkBoxAutoTrack.isChecked()
            # Mark Pulse Init state
            self.fsThread.pulse_init_status = False
            # Start fsThread
            self.fsThread.start()
        else:
            # Set Microwave Source
            self.set_fix_freq()
            # Set scan parameters
            # These will not change in one experiment
            self.tsThread.delay = self.dic_delay
            self.tsThread.time_arr = self.time_sweep
            self.tsThread.pulse_form = self.pulse_seq
            # These can be changed when pause/resume the experiment
            self.tsThread.loop_num = [0, int(self.ui.leTotalLoopNum.text())]
            self.tsThread.point_num = [0, np.size(self.time_sweep)]
            # These can be changed during the experiment
            self.tsThread.threshold = int(self.ui.leTrackingThreshold.text())
            self.tsThread.auto_track = self.ui.checkBoxAutoTrack.isChecked()
            # Start tsThread
            self.tsThread.start()

        # Change the text and function of Start Button
        self.ui.pbExpStart.setText('Pause')
        self.ui.pbExpStart.clicked.disconnect()
        self.ui.pbExpStart.clicked.connect(self.pause_exp)
        # Set Button enable state
        self.ui.pbExpStop.setEnabled(True)
        self.ui.pbReset.setEnabled(False)
        # Init current state display
        self.ui.leCurrentLoopNum.setText('0')
        self.ui.leCurrentPointNum.setText('0')
        self.ui.leCurrentAverageNum.setText('0')
        # Disable text box
        # Track Group
        self.ui.pbTrack.setEnabled(False)
        self.ui.leTrackingThreshold.setEnabled(False)
        # Microwave Group
        self.ui.checkBoxUseScan.setEnabled(False)
        self.ui.leFixedFreqSetting.setEnabled(False)
        self.ui.leMWPowerSetting.setEnabled(False)
        self.ui.leStartFreqSetting.setEnabled(False)
        self.ui.leEndFreqSetting.setEnabled(False)
        self.ui.leStepSetting.setEnabled(False)
        self.ui.pbMWPowerOff.setEnabled(False)
        # Time Group
        self.ui.leTimeStart.setEnabled(False)
        self.ui.leTimeEnd.setEnabled(False)
        self.ui.leTimeStep.setEnabled(False)
        self.ui.leNumberOfStep.setEnabled(False)
        self.ui.tabWidget.setEnabled(False)
        # Scanning Status
        self.ui.leCurrentLoopNum.setEnabled(False)
        self.ui.leCurrentPointNum.setEnabled(False)
        self.ui.leCurrentAverageNum.setEnabled(False)
        self.ui.leTotalLoopNum.setEnabled(False)
        self.ui.leTotalAverageNum.setEnabled(False)

    @QtCore.pyqtSlot()
    def pause_exp(self):
        """
        Pause the experiment.
        :return: None
        """
        # Set the status to 'pulse'
        self.pause_status = True
        # Set running Status in Threads to be 'False'
        if self.ui.checkBoxUseScan.isChecked() is True:
            self.fsThread.running_status = False
        else:
            self.tsThread.running_status = False
        self.ui.pbExpStart.setText('Resume')
        self.ui.pbExpStart.clicked.disconnect()
        self.ui.pbExpStart.clicked.connect(self.resume_exp)

        self.ui.pbSetScanningStatus.setEnabled(True)
        # Scanning Status
        self.ui.leCurrentLoopNum.setEnabled(True)
        self.ui.leCurrentPointNum.setEnabled(True)
        self.ui.leCurrentAverageNum.setEnabled(True)
        # Set track status
        self.ui.pbTrack.setEnabled(True)
        self.ui.leTrackingThreshold.setEnabled(True)

    @QtCore.pyqtSlot()
    def resume_exp(self):
        """
        Resume the experiment.
        :return: None
        """
        self.pause_status = False
        if self.ui.checkBoxUseScan.isChecked() is True:
            self.fsThread.start()
        else:
            self.tsThread.start()
        self.ui.pbExpStart.setText('Pause')
        self.ui.pbExpStart.clicked.disconnect()
        self.ui.pbExpStart.clicked.connect(self.pause_exp)

        self.ui.pbSetScanningStatus.setEnabled(False)
        # Scanning Status
        self.ui.leCurrentLoopNum.setEnabled(False)
        self.ui.leCurrentPointNum.setEnabled(False)
        self.ui.leCurrentAverageNum.setEnabled(False)
        # Set track status
        self.ui.pbTrack.setEnabled(False)
        self.ui.leTrackingThreshold.setEnabled(False)

    @QtCore.pyqtSlot()
    def stop_scan(self):
        """
        Call this method when push the stop button.
        If the Scan Thread is in pause status, the methods will change the status first,
        then call self.scan_stop() to initial the button status.
        :return: None
        """
        if self.pause_status is True:
            self.pause_status = False
        self.scan_stop()

    # Methods connect to Thread
    # Methods for Track Thread
    @QtCore.pyqtSlot(list, list, list, list)
    def update_tracking_result(self, pos_list, cts_list, pos_origin, pos_final):
        """
        Update the tracking plot based on tracking data
        :param pos_list: [list, list, list], [[x_pos list], [y_pos list], [z_pos list]]
        :param cts_list: [list, list, list], [[x_cts list], [y_cts list], [z_cts list]]
        :param pos_origin: list, [x_origin_pos, y_origin_pos, z_origin_pos]
        :param pos_final: list,  [x_final_pos, y_final_pos, z_final_pos]
        :return: None
        """
        self.ui.track_fig.figure.clear()
        # update X axis data
        self.ui.track_fig.x_plot = self.ui.track_fig.figure.add_subplot(131)
        self.ui.track_fig.x_plot.set_title('X Axis')
        self.ui.track_fig.x_plot.plot(pos_list[0], cts_list[0], "r")
        self.ui.track_fig.x_plot.vlines(pos_origin[0], min(cts_list[0]), max(cts_list[0]), colors="r",
                                        linestyles="dashed")
        self.ui.track_fig.x_plot.vlines(pos_final[0], min(cts_list[0]), max(cts_list[0]), colors="b",
                                        linestyles="dashed")
        # update X axis data
        self.ui.track_fig.y_plot = self.ui.track_fig.figure.add_subplot(132)
        self.ui.track_fig.y_plot.set_title('Y Axis')
        self.ui.track_fig.y_plot.plot(pos_list[1], cts_list[1], "r")
        self.ui.track_fig.y_plot.vlines(pos_origin[1], min(cts_list[1]), max(cts_list[1]), colors="r",
                                        linestyles="dashed")
        self.ui.track_fig.y_plot.vlines(pos_final[1], min(cts_list[1]), max(cts_list[1]), colors="b",
                                        linestyles="dashed")
        # update X axis data
        self.ui.track_fig.z_plot = self.ui.track_fig.figure.add_subplot(133)
        self.ui.track_fig.z_plot.set_title('Z Axis')
        self.ui.track_fig.z_plot.plot(pos_list[2], cts_list[2], "r")
        self.ui.track_fig.z_plot.vlines(pos_origin[2], min(cts_list[2]), max(cts_list[2]), colors="r",
                                        linestyles="dashed")
        self.ui.track_fig.z_plot.vlines(pos_final[2], min(cts_list[2]), max(cts_list[2]), colors="b",
                                        linestyles="dashed")

        self.ui.track_fig.draw()

    # Methods for Sweep Threads
    @QtCore.pyqtSlot(int, int, float, int, int)
    def exp_data_back(self, sig, ref, freq_or_time, point_num, loop_num):
        """
        Pass the data that Scan Thread send back to Data Thread
        :param sig: Signal Counts  (int)
        :param ref: Reference Counts (int)
        :param freq_or_time: Frequency Point or Time Point (float)
        :param point_num: Number of point (int)
        :param loop_num: Number of loop (int)
        :return: None
        """
        self.dThread.sig = sig
        self.dThread.ref = ref
        self.dThread.freq_or_time = freq_or_time
        self.dThread.point = point_num
        self.dThread.loop = loop_num

        self.dThread.ref_ave_temp = self.ref_ave
        self.dThread.sig_ave_temp = self.sig_ave
        self.dThread.start()

        self.ui.leTrackingSignal.setText(str(sig))
        self.ui.leTrackingReference.setText(str(ref))

        self.ui.leCurrentPointNum.setText(str(point_num + 1))
        self.ui.leCurrentLoopNum.setText(str(loop_num + 1))

    @QtCore.pyqtSlot()
    def scan_stop(self):
        """
        Call this method when scan thread end
        If the Scan Thread end with pause status, the methods will do nothing
        if the Scan Thread end directly, the method will initial the button status
        :return: None
        """
        # If in Pause Status, do nothing
        if self.pause_status is True:
            return
        # Set the running status of the Scanning Thread
        if self.ui.checkBoxUseScan.isChecked() is True:
            self.fsThread.running_status = False
        else:
            self.tsThread.running_status = False
        # Set Start Button
        self.ui.pbExpStart.setText('Start')
        self.ui.pbExpStart.clicked.disconnect()
        self.ui.pbExpStart.clicked.connect(self.start_scan)
        # Set button enable state
        self.ui.pbExpStop.setEnabled(False)
        self.ui.pbReset.setEnabled(True)
        self.ui.pbSetScanningStatus.setEnabled(False)
        # Enable text box
        # Track Group
        self.ui.pbTrack.setEnabled(True)
        self.ui.leTrackingThreshold.setEnabled(True)
        # Microwave Group
        self.ui.checkBoxUseScan.setEnabled(True)
        self.ui.leFixedFreqSetting.setEnabled(True)
        self.ui.leMWPowerSetting.setEnabled(True)
        self.ui.leStartFreqSetting.setEnabled(True)
        self.ui.leEndFreqSetting.setEnabled(True)
        self.ui.leStepSetting.setEnabled(True)
        self.ui.pbMWPowerOff.setEnabled(True)
        # Time Group
        self.ui.leTimeStart.setEnabled(True)
        self.ui.leTimeEnd.setEnabled(True)
        self.ui.leTimeStep.setEnabled(True)
        self.ui.leNumberOfStep.setEnabled(True)
        self.ui.tabWidget.setEnabled(True)
        # Scanning Status
        self.ui.leCurrentLoopNum.setEnabled(True)
        self.ui.leCurrentPointNum.setEnabled(True)
        self.ui.leCurrentAverageNum.setEnabled(True)
        self.ui.leTotalLoopNum.setEnabled(True)
        self.ui.leTotalAverageNum.setEnabled(True)

    # Methods for Data Thread
    @QtCore.pyqtSlot(list, list)
    def update_base_on_data(self, ref, sig):
        """
        Replot the Data Plot based on data
        :param ref: Reference Data (list)
        :param sig: Signal Data (list)
        :return: None
        """
        self.ref_ave = ref
        self.sig_ave = sig
        self.replot_data()

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        """
        When close the event, ask if to save the Defaults
        :param event:
        :return: None
        """
        quit_message = 'Save parameters as Defaults?'
        reply = QtWidgets.QMessageBox.question(self, 'Message', quit_message, QtWidgets.QMessageBox.Save |
                                               QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Save:
            self.save_defaults()
            self.ExpESRClose.emit()
            event.accept()
        elif reply == QtWidgets.QMessageBox.Discard:
            self.ExpESRClose.emit()
            event.accept()
        else:
            event.ignore()

    @QtCore.pyqtSlot()
    def check_and_update_plot(self):
        if int(self.ui.leTimeEnd_exp.text()) > int(self.ui.leTimeStart_exp.text()):
            self.generate_sweep_points_and_replot()
        else:
            self.ui.statusbar.showMessage('Please check the Time Sweep settings!')

    def generate_sweep_points(self):
        """
        This methods generate the sweep points based on the state of the ScanState Checkbox, and pass them to GUI
        :return: None
        """
        # Generate freq_sweep (list) if choose Frequency Scan
        if self.ui.checkBoxUseScan.isChecked() is True:
            # Load Frequency Start Point, End Point, Step from GUI
            start_freq = float(self.ui.leStartFreqSetting.text())
            end_freq = float(self.ui.leEndFreqSetting.text())
            step_freq = float(self.ui.leStepSetting.text())
            # Calculate the Step Number and pass it to GUI
            freq_step_num = math.ceil(float((end_freq - start_freq) / step_freq)) + 1
            self.ui.leTotalPointNum.setText(str(freq_step_num))
            # Generate the Frequency Sweep Points (list) based on settings
            self.freq_sweep = list(np.linspace(start_freq, end_freq, freq_step_num))
            # Generate Fake Data
            self.ref_ave = list(np.random.randint(0, 5, np.size(self.freq_sweep)) + 10)
            self.sig_ave = list(np.random.randint(0, 5, np.size(self.freq_sweep)))
        # Generate time_sweep (list) if choose Time Scan
        else:
            # Generate the Time Sweep Points (list) based on settings
            if self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Linear':
                # Load Time Start Point, End Point, Step, Step Number from GUI
                step_time = int(self.ui.leTimeStep.text())
                start_time = int(self.ui.leTimeStart.text()) + step_time
                end_time = int(self.ui.leTimeEnd.text())
                # Calculate the Step Number and pass it to GUI
                time_step_num = math.ceil(float((end_time - start_time) / step_time)) + 1
                self.ui.leTotalPointNum.setText(str(time_step_num))
                self.time_sweep = list(np.linspace(start_time, end_time, time_step_num))
            elif self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Exponential':
                # Load Time Start Point, End Point, Step, Step Number from GUI
                start_time = int(self.ui.leTimeStart_exp.text())
                end_time = int(self.ui.leTimeEnd_exp.text())
                # Calculate the Step Number and pass it to GUI
                time_step_num = int(self.ui.leNumberOfStep_exp.text())
                self.ui.leTotalPointNum.setText(str(time_step_num))
                self.time_sweep = list(np.logspace(np.log(start_time), np.log(end_time), time_step_num, base=np.exp(1)))
            # Generate Fake Data
            self.ref_ave = list(np.random.randint(0, 5, np.size(self.time_sweep)) + 10)
            self.sig_ave = list(np.random.randint(0, 5, np.size(self.time_sweep)))

    def generate_sweep_points_and_replot(self):
        """
        Generate the sweep point and replot the plot for Data
        :return: None
        """
        if float(self.ui.leStartFreqSetting.text()) < float(self.ui.leEndFreqSetting.text()):
            self.generate_sweep_points()
            self.replot_data()
        else:
            self.ui.statusbar.showMessage('Please check the Microwave Frequency setting!')

    def replot_data(self):
        """
        Replot the data plot.
        :return: None
        """
        if self.ui.checkBoxUseScan.isChecked() is True:
            self.ref_plot.set_data(self.freq_sweep, self.ref_ave)
            self.sig_plot.set_data(self.freq_sweep, self.sig_ave)
            self.ui.data_fig.axes.set_xlabel('Frequency (MHz)')
            self.ui.data_fig.axes.set_ylabel('Counts')
            self.ui.data_fig.axes.set_xlim(np.min(self.freq_sweep) * 0.99, np.max(self.freq_sweep) * 1.01)
            self.ui.data_fig.axes.set_xscale("linear")

        else:
            self.ref_plot.set_data(self.time_sweep, self.ref_ave)
            self.sig_plot.set_data(self.time_sweep, self.sig_ave)
            self.ui.data_fig.axes.set_xlabel('Time (ns)')
            self.ui.data_fig.axes.set_ylabel('Counts')
            self.ui.data_fig.axes.set_xlim(np.min(self.time_sweep) * 0.99, np.max(self.time_sweep) * 1.01)
            if self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex()) == 'Exponential':
                self.ui.data_fig.axes.set_xscale("log")
            else:
                self.ui.data_fig.axes.set_xscale("linear")

        self.ui.data_fig.axes.set_ylim(min(np.min(self.sig_ave), np.min(self.ref_ave)) -
                                       max(np.ptp(self.sig_ave), np.ptp(self.ref_ave)) * 0.05,
                                       max(np.max(self.sig_ave), np.max(self.ref_ave)) +
                                       max(np.ptp(self.sig_ave), np.ptp(self.ref_ave)) * 0.05)
        self.ui.data_fig.draw()
        self.ui.statusbar.showMessage('Successfully replot the figure!')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mainGUI()
    myWindow.show()
    sys.exit(app.exec_())
