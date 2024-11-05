"""

"""

import sys
import os

from ui.uipy.mainWindow import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore

from src.interface.confocal import mainGUI as confocal_interface
from src.hardware import DeviceManager
import src.utils.logger as logger


class mainGUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.hardware = DeviceManager()
        self.connect_pb_all()
        self.confocal_interface = None

    def connect_pb_all(self):
        # experiment interface group
        self.ui.pbExpConfocal.clicked.connect(self.open_confocal_interface)
        # pb button connect
        self.ui.pbPiezoInit.clicked.connect(self.hardware.init_mover)
        self.ui.pbPiezoReset.clicked.connect(self.hardware.reset_mover)
        self.ui.pbGalvoInit.clicked.connect(self.hardware.init_scanner)
        self.ui.pbGalvoReset.clicked.connect(self.hardware.reset_scanner)
        self.ui.pbPulseGenInit.clicked.connect(lambda: self.hardware.init_pulser())
        self.ui.pbPulseGenReset.clicked.connect(self.hardware.reset_pulser)
        self.ui.pbTaggerInit.clicked.connect(self.hardware.init_counter)
        self.ui.pbTaggerReset.clicked.connect(self.hardware.reset_counter)
        self.ui.pbDaqInit.clicked.connect(self.hardware.init_ni)
        self.ui.pbDaqReset.clicked.connect(self.hardware.reset_ni)
        self.ui.pbMWInit.clicked.connect(blank_function)
        self.ui.pbMWReset.clicked.connect(blank_function)
        self.ui.pbRotatorInit.clicked.connect(blank_function)
        self.ui.pbRotatorReset.clicked.connect(blank_function)
        self.ui.pbInitAll.clicked.connect(self.hardware.init_all_device)
        self.ui.pbResetAll.clicked.connect(self.hardware.cleanup)
        # connect device status update signal to handling function
        self.hardware.DeviceStatusUpdate.connect(self.update_hardware_status)

    # function for processing input hardware status signal
    @QtCore.pyqtSlot(str, bool, name='DeviceStatusUpdate')
    def update_hardware_status(self, device, status):
        if device == 'mover':
            self.ui.rbPiezoConnect.setChecked(status), self.ui.rbPiezoDisconnect.setChecked(not status)
            self.ui.pbPiezoInit.setEnabled(not status), self.ui.pbPiezoReset.setEnabled(status)
        elif device == 'scanner':
            self.ui.rbGalvoConnect.setChecked(status), self.ui.rbGalvoDisconnect.setChecked(not status)
            self.ui.pbGalvoInit.setEnabled(not status), self.ui.pbGalvoReset.setEnabled(status)
        elif device == 'pulser':
            self.ui.rbPulseGenConnect.setChecked(status), self.ui.rbPulseGenDisconnect.setChecked(not status)
            self.ui.pbPulseGenInit.setEnabled(not status), self.ui.pbPulseGenReset.setEnabled(status)
        elif device == 'counter':
            self.ui.rbTaggerConnect.setChecked(status), self.ui.rbTaggerDisconnect.setChecked(not status)
            self.ui.pbTaggerInit.setEnabled(not status), self.ui.pbTaggerReset.setEnabled(status)
        elif device == 'NIDAQ':
            self.ui.rbDaqConnect.setChecked(status), self.ui.rbDaqDisconnect.setChecked(not status)
            self.ui.pbDaqInit.setEnabled(not status), self.ui.pbDaqReset.setEnabled(status)
        elif device == 'MW':
            self.ui.rbMWConnect.setChecked(status), self.ui.rbMWDisconnect.setChecked(not status)
            self.ui.pbMWInit.setEnabled(not status), self.ui.pbMWReset.setEnabled(status)
        elif device == 'rotator':
            self.ui.rbRotatorConnect.setChecked(status), self.ui.rbRotatorDisconnect.setChecked(not status)
            self.ui.pbRotatorInit.setEnabled(not status), self.ui.pbRotatorReset.setEnabled

    # function for handling experiment interface
    def open_confocal_interface(self):
        if self.confocal_interface is None:
            self.confocal_interface = confocal_interface(hardware=self.hardware)
            self.confocal_interface.ExpConfocalClose.connect(self.confocal_interface_closed)
            self.confocal_interface.show()
            self.ui.statusbar.showMessage('Open Confocal scan window.', msecs=3000)
        else:
            self.ui.statusbar.showMessage('Confocal scan window is opened already!', msecs=3000)

    @QtCore.pyqtSlot()
    def confocal_interface_closed(self):
        self.confocal_interface = None

    # function for close event
    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        quit_message = 'Do you want to quit?'
        reply = QtWidgets.QMessageBox.question(self, 'Message', quit_message, QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Yes:
            self.hardware.cleanup()
            event.accept()
        else:
            event.ignore()


def blank_function():
    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mainGUI()
    myWindow.show()
    sys.exit(app.exec_())