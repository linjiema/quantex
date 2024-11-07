"""
Created on Jun 30, 2021

This File is the dialog of Sequence Editor. Including the connect of the methods and the function.
This work need the pyUI file of SeqEditor

@author: Linjie
"""

import sys
import os
from pathlib import Path

from ui.uipy.pulse_ESR.SeqEditor import Ui_SeqEditor
from PyQt5 import QtCore, QtWidgets

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def find_project_root(current_path, marker_files=("README.md", ".git")):
    for parent in current_path.parents:
        if any((parent / marker).exists() for marker in marker_files):
            print(parent)
            return parent
    return current_path


class SeqEditor_GUI(QtWidgets.QDialog):
    def __init__(self, seq_dir=None, parent=None):
        self.project_dir = find_project_root(current_path=Path(__file__).resolve())
        # Set up UI
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_SeqEditor()
        self.ui.setupUi(self)
        # Connect the button box of the qt_dialog
        self.ui.buttonBox.accepted.connect(self.save_dir_and_accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        # Init some variables
        self.seq = None
        self.seq_name = None
        self.y_arrs_plot = [[], [], [], []]
        # Init plot and connect methods
        self.init_plot()
        self.connect_functions()
        # Init self.seq and replot the data
        if seq_dir is None:
            self.seq = []
        else:
            self.load_seq(directory=seq_dir)

    def init_plot(self):
        """
        Call this method when need to init the plot.
        """
        fig = Figure()
        self.ui.seq_plot = FigureCanvas(fig)
        self.ui.seq_plot.setParent(self.ui.widget)
        self.ui.seq_plot.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), self.ui.widget.size()))
        self.ui.seq_plot.axes = fig.add_subplot(111)

    def connect_functions(self):
        """
        Call this method when need to connect the function to all the slot
        """
        # File Group
        self.ui.pbLoadSeq.clicked.connect(self.load_seq)
        self.ui.pbSaveSeq.clicked.connect(self.save_seq)
        # Add Pulse Group
        self.ui.pbAddScanStart.clicked.connect(self.add_scan_start)
        self.ui.pbAddScanStop.clicked.connect(self.add_scan_stop)
        self.ui.pbClearScan.clicked.connect(self.clear_scan)
        self.ui.pbAddPulse.clicked.connect(self.add_pulse)

        self.ui.leStart.editingFinished.connect(self.update_duration)
        self.ui.leStop.editingFinished.connect(self.update_duration)
        self.ui.leDuration.editingFinished.connect(self.update_stop)
        # Overview
        self.ui.pbDelete.clicked.connect(self.delete_pulse)
        self.ui.listWidget.itemClicked.connect(lambda: self.ui.pbDelete.setEnabled(True))
        # Add Protocol
        self.ui.pbAddShelving.clicked.connect(self.add_shelving)
        self.ui.pbAddMeasure.clicked.connect(self.add_measure)

    # File Group
    def load_seq(self, directory=None):
        """
        Call this method when need to load the Pulse Seq from the file or push the 'Load' button
        :param directory: The abs dir of the Seq file
        :return: None
        """
        # Load the dir
        if directory is False:  # If do not have income dir
            # Get the abs path of the pulse File
            dir_pulse_seq = os.path.join(self.project_dir,
                                         'config\\config_pulse_ESR\\PulseSeq')
            _directory = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Pulse Sequence',
                                                               dir_pulse_seq, 'Text (*.txt)')
            _directory = str(_directory[0].replace('/', '\\'))
        else:
            _directory = directory
            self.seq_dir = _directory
        # Read the Seq File
        if _directory != '':
            with open(_directory, 'r') as f_seq:
                self.seq = []
                # Load into self.seq
                for line in f_seq.readlines():
                    line = line.replace('\n', '').replace('[', '').replace(']', '').replace("'", '')
                    self.seq.append(line.split(','))
            # Load the Name of Seq
            self.seq_name = _directory.split('\\')[-1].replace('.txt', '')
            self.ui.leSeqName.setText(self.seq_name)
            # Load seq into listWidget
            self.make_listWidget()
            # Replot the figure of Pulse Sequence
            self.update_plot()
            self.seq_dir = _directory
        else:
            sys.stderr.write('No file is selected!\n')
        # Back to the normal dir
        os.chdir(os.path.dirname(__file__))

    def save_seq(self):
        """
        Call this method when push the 'Save' button.
        :return: None
        """
        # Get the abs path of the pulse File
        dir_pulse_seq = os.path.join(self.project_dir,
                                     'config\\config_pulse_ESR_polarization\\PulseSeq')
        # Get the name of the file
        self.seq_name = self.ui.leSeqName.text()
        path_pulse_seq = os.path.join(dir_pulse_seq, self.seq_name)
        # Get the dir of SaveSeq
        dir_save_seq = QtWidgets.QFileDialog.getSaveFileName(self, 'Enter save file', path_pulse_seq, 'Text (*.txt)')
        dir_save_seq = str(dir_save_seq[0].replace('/', '\\'))
        # Save the seq in file
        if dir_save_seq != '':
            with open(dir_save_seq, 'w') as f_save_seq:
                for each_pulse in self.seq:
                    f_save_seq.write(str(each_pulse) + '\n')
            self.seq_dir = dir_save_seq
        else:
            sys.stderr.write('No file is saved!\n')

    # Add Pulse
    def add_scan_start(self):
        """
        Call this method when push the 'Add Scan Start' button.
        This Method will add a 't' at the start of the pulse;
        Also, as the start time increase, the end time will also increase.
        :return: None
        """
        # Read the scan start/stop status
        scan_start = self.ui.leStart_t.text()
        scan_stop = self.ui.leStop_t.text()
        # Add scan start location
        if scan_start == '':
            self.ui.leStart_t.setText('+t')
        elif scan_start == '+t':
            self.ui.leStart_t.setText('+2t')
        else:
            nt = int(scan_start[1:-1])
            self.ui.leStart_t.setText('+' + str(nt + 1) + 't')
        # Add scan stop location
        if scan_stop == '':
            self.ui.leStop_t.setText('+t')
        elif scan_stop == '+t':
            self.ui.leStop_t.setText('+2t')
        else:
            nt = int(scan_stop[1:-1])
            self.ui.leStop_t.setText('+' + str(nt + 1) + 't')

    def add_scan_stop(self):
        """
       Call this method when push the 'Add Scan Stop' button.
       This Method will add a 't' at the end of the pulse;
       Also, as the end time increase, the duration time will also increase.
       :return: None
       """
        # Read the scan start/stop status
        scan_stop = self.ui.leStop_t.text()
        scan_dur = self.ui.leDuration_t.text()
        # Add scan stop location
        if scan_stop == '':
            self.ui.leStop_t.setText('+t')
        elif scan_stop == '+t':
            self.ui.leStop_t.setText('+2t')
        else:
            nt = int(scan_stop[1:-1])
            self.ui.leStop_t.setText('+' + str(nt + 1) + 't')
        # Add scan duration time
        if scan_dur == '':
            self.ui.leDuration_t.setText('+t')
        elif scan_dur == '+t':
            self.ui.leDuration_t.setText('+2t')
        else:
            nt = int(scan_dur[1:-1])
            self.ui.leDuration_t.setText('+' + str(nt + 1) + 't')

    def clear_scan(self):
        """
        Call this method when push the 'Clear Scan' button.
        This method will clear the text box of the scan setting.
        :return: None
        """
        self.ui.leStart_t.clear()
        self.ui.leStop_t.clear()
        self.ui.leDuration_t.clear()

    def add_pulse(self):
        """
        Call this Method when push the 'Add Pulse' button.
        This method will ass a pause based on the selected channel, write it in the self.seq and listWidget.
        :return: None
        """
        # Read the value from GUI Textbox
        channel = str(self.ui.comboBoxChannel.currentText())
        start_point = str(self.ui.leStart.text()) + str(self.ui.leStart_t.text())
        stop_point = str(self.ui.leStop.text()) + str(self.ui.leStop_t.text())
        # Write value in self.seq and listWidget
        self.seq.append([channel, start_point, stop_point])
        self.ui.listWidget.addItem(channel + ',' + start_point + ',' + stop_point)
        self.update_plot()

    def update_duration(self):
        """
        Call this method when change the Start/Stop time.
        This Method changes duration time based on the value in Start Time and Stop Time text box.
        :return: None
        """
        start = int(self.ui.leStart.text())
        stop = int(self.ui.leStop.text())
        self.ui.leDuration.setText(str(stop - start))

    def update_stop(self):
        """
        Call this method when change the Duration time.
        This Method changes Stop time based on the value in Start Time and Duration Time text box.
        :return: None
        """
        start = int(self.ui.leStart.text())
        duration = int(self.ui.leDuration.text())
        self.ui.leStop.setText(str(start + duration))

    # Overview
    def delete_pulse(self):
        """
        Call this method when push the 'Delete' button.
        This method will delete the selected pulse from self.seq and listWidget.
        :return: None
        """
        # Get the selected pulse index from listWidget
        index = self.ui.listWidget.currentRow()
        # Delete selected pulse from self.seq
        del self.seq[index]
        # Delete selected pulse from listWidget
        self.ui.listWidget.takeItem(index)

        self.ui.pbDelete.setEnabled(False)
        self.update_plot()

    # Add Protocol
    def add_shelving(self):
        """
        Call this method when push the 'Add Shelving' button
        :return: None
        """
        # Get shelving delay from GUI text box
        shelving_delay = int(self.ui.leShelvingDelay.text())
        for i in range(len(self.seq)):
            # Edit start point
            start = self.seq[i][1]
            if '+' in start:
                new_start = str(int(start.split('+')[0]) + shelving_delay) + '+' + start.split('+')[1]
            else:
                new_start = str(int(start) + shelving_delay)
            # Edit stop point
            stop = self.seq[i][2]
            if '+' in stop:
                new_stop = str(int(stop.split('+')[0]) + shelving_delay) + '+' + stop.split('+')[1]
            else:
                new_stop = str(int(stop) + shelving_delay)
            # Modify the Pulse in self.seq
            self.seq[i][1] = new_start
            self.seq[i][2] = new_stop
            # Modify the pulse in listWidget
            new_item = self.seq[i][0] + ',' + new_start + ',' + new_stop
            self.ui.listWidget.takeItem(i)
            self.ui.listWidget.insertItem(i, new_item)
        self.update_plot()

    def add_measure(self):
        """
        Call this method when push the 'Add Measure' button.
        :return: None
        """
        end_max = 0
        line_max = 0

        for each_pulse in self.seq:
            end_point = int(each_pulse[-1].split('+')[0])
            if end_point > end_max:
                end_max = end_point
                line_max = self.seq.index(each_pulse)
        # Get waiting time from GUI text box
        waiting_time = int(self.ui.leWaitingTime.text())

        if '+' in self.seq[line_max][2]:
            start = str(int(self.seq[line_max][2].split('+')[0]) + waiting_time)
            scan = '+' + self.seq[line_max][2].split('+')[-1]
        else:
            start = str(int(self.seq[line_max][2]) + waiting_time)
            scan = ''
        # Add pulse in self.seq and listWidget
        self.seq.append(['Laser', start + scan, str(int(start) + 3000) + scan])
        self.seq.append(['Sig', start + scan, str(int(start) + 300) + scan])
        self.seq.append(['Ref', str(int(start) + 2700) + scan, str(int(start) + 3000) + scan])
        self.ui.listWidget.addItem('Laser,' + start + scan + ',' + str(int(start) + 3000) + scan)
        self.ui.listWidget.addItem('Sig,' + start + scan + ',' + str(int(start) + 100) + scan)
        self.ui.listWidget.addItem('Ref,' + str(int(start) + 2700) + scan + ',' + str(int(start) + 3000) + scan)
        # Update plot
        self.update_plot()

    def update_plot(self):
        """
        This methods update the plot based on the self.seq list.
        :return:
        """
        # Define the x range of the plot
        end_max = 0
        for each_pulse in self.seq:
            end = int(each_pulse[-1].split('+')[0])
            if end > end_max:
                end_max = end
        x_arr_plot = range(end_max + 1)
        # Init the y lists
        self.y_arrs_plot = [[0] * (end_max + 1), [2] * (end_max + 1), [4] * (end_max + 1), [6] * (end_max + 1)]
        self.dic_channel = {
            'Ref': self.y_arrs_plot[0],
            'Sig': self.y_arrs_plot[1],
            'Laser': self.y_arrs_plot[2],
            'MicroWave': self.y_arrs_plot[3],
        }
        # Adjust the y value for each channel based on each seq store in the self.seq
        for each_pulse in self.seq:
            channel_seq = self.dic_channel.get(each_pulse[0])
            start_point = int(each_pulse[1].split('+')[0])
            stop_point = int(each_pulse[2].split('+')[0])
            # Define the Open time of each Channel
            for point in range(start_point, stop_point):
                # Prevent add multi pulse at same time point
                if channel_seq[point] % 2 == 0:
                    channel_seq[point] += 1
        # Plot
        self.ui.seq_plot.figure.clear()
        self.ui.seq_plot.axes = self.ui.seq_plot.figure.add_subplot(111)
        self.ui.seq_plot.axes.plot(x_arr_plot, self.y_arrs_plot[3], 'r-', label='Microwave')
        self.ui.seq_plot.axes.plot(x_arr_plot, self.y_arrs_plot[2], 'g-', label='Laser')
        self.ui.seq_plot.axes.plot(x_arr_plot, self.y_arrs_plot[1], 'k-', label='Sig')
        self.ui.seq_plot.axes.plot(x_arr_plot, self.y_arrs_plot[0], 'b-', label='Ref')
        self.ui.seq_plot.axes.legend()
        self.ui.seq_plot.draw()

    def make_listWidget(self):
        """
        Call this method when need to create listWidget
        :return:
        """
        self.ui.listWidget.clear()
        for [channel, start, stop] in self.seq:
            self.ui.listWidget.addItem(channel + ',' + start + ',' + stop)

    # Button Box
    def save_dir_and_accept(self):
        # Get the name of the file
        self.seq_name = self.ui.leSeqName.text()
        dir_save_seq = os.path.join(self.project_dir,
                                    'cache\\cache_pulse_ESR_polarization\\temp\\' + self.seq_name + '.txt')
        # Save the seq in file
        if dir_save_seq != '':
            with open(dir_save_seq, 'w') as f_save_seq:
                for each_pulse in self.seq:
                    f_save_seq.write(str(each_pulse) + '\n')
            self.seq_dir = dir_save_seq
        else:
            sys.stderr.write('No file is saved!\n')
        self.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    myWindow = SeqEditor_GUI()
    myWindow.show()

    sys.exit(app.exec_())

