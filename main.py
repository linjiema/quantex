"""

"""

import sys
import os

from ui.uipy.mainWindow import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore

from src.interface.confocal import mainGUI as confocal_interface
from src.hardware import device_manager
import src.utils.logger as logger


class mainGUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.hardware = device_manager()
        self.connect_pb_all()
        self.confocal_interface = None

    def connect_pb_all(self):
        self.ui.pbExpConfocal.clicked.connect(self.open_confocal_interface)

    def update_hardware_status(self):
        pass

    def open_confocal_interface(self):
        if self.confocal_interface is None:
            self.confocal_interface = confocal_interface(hardware=self.hardware)
            self.confocal_interface.ExpConfocalClose.connect(self.confocal_interface_closed)
            self.confocal_interface.show()
            self.ui.statusbar.showMessage('Open Confocal scan window.', msecs=3000)
        else:
            self.ui.statusbar.showMessage('Confocal scan window is opened already!', msecs=3000)

    def confocal_interface_closed(self):
        self.confocal_interface = None


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mainGUI()
    myWindow.show()
    sys.exit(app.exec_())