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

        # hardware group
        self.ui.pbPiezoInit.clicked.connect(self.init_piezo_stage)
        self.ui.pbPiezoReset.clicked.connect(self.reset_piezo_stage)
        self.ui.pbGalvoInit.clicked.connect(self.init_galvo_mirror)
        self.ui.pbGalvoReset.clicked.connect(self.reset_galvo_mirror)
        self.ui.pbPulseGenInit.clicked.connect(self.init_pulser)
        self.ui.pbPulseGenReset.clicked.connect(self.reset_pulser)
        self.ui.pbTaggerInit.clicked.connect(self.init_timetagger)
        self.ui.pbTaggerReset.clicked.connect(self.reset_timetagger)
        self.ui.pbDaqInit.clicked.connect(self.init_nidaq)
        self.ui.pbDaqReset.clicked.connect(self.reset_nidaq)
        self.ui.pbMWInit.clicked.connect(self.init_mw_source)
        self.ui.pbMWReset.clicked.connect(self.reset_mw_source)
        self.ui.pbRotatorInit.clicked.connect(self.init_rotator)
        self.ui.pbRotatorReset.clicked.connect(self.reset_rotator)
        self.ui.pbInitAll.clicked.connect(self.init_all_hardware)
        self.ui.pbResetAll.clicked.connect(self.reset_all_hardware)

        self.hardware.DeviceStatusUpdate.connect(self.update_hardware_status)


    # data processing group
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



    def init_piezo_stage(self):
        self.hardware.init_mover()

    def reset_piezo_stage(self):
        self.hardware.reset_mover()

    def init_galvo_mirror(self):
        self.hardware.init_scanner()

    def reset_galvo_mirror(self):
        self.hardware.reset_scanner()

    def init_pulser(self):
        self.hardware.init_pulser()

    def reset_pulser(self):
        self.hardware.reset_pulser()

    def init_timetagger(self):
        self.hardware.init_counter()

    def reset_timetagger(self):
        self.hardware.reset_counter()

    def init_nidaq(self):
        self.hardware.init_triggered_counter()
        self.hardware.init_triggered_location_sensor()
        self.hardware.init_timer()
        self.hardware.init_one_time_counter()

        if self.hardware.triggered_counter_status and self.hardware.triggered_location_sensor_status and \
                self.hardware.timer_status and self.hardware.one_time_counter_status:
            self.update_hardware_status('NIDAQ', True)

    def reset_nidaq(self):
        self.hardware.reset_triggered_counter()
        self.hardware.reset_triggered_location_sensor()
        self.hardware.reset_timer()
        self.hardware.reset_one_time_counter()

        if not self.hardware.triggered_counter_status and not self.hardware.triggered_location_sensor_status and \
                not self.hardware.timer_status and not self.hardware.one_time_counter_status:
            self.update_hardware_status('NIDAQ', False)

    def init_mw_source(self):
        pass

    def reset_mw_source(self):
        pass

    def init_rotator(self):
        pass

    def reset_rotator(self):
        pass

    def init_all_hardware(self):
        self.hardware.init_all_device()

    def reset_all_hardware(self):
        self.hardware.cleanup()

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

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        quit_message = 'Do you want to quit?'
        reply = QtWidgets.QMessageBox.question(self, 'Message', quit_message, QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Yes:
            self.reset_all_hardware()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mainGUI()
    myWindow.show()
    sys.exit(app.exec_())