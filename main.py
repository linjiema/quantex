"""

"""

import sys
import os

from ui.uipy.confocal import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore

from src.interface.confocal import mainGUI as confocal_interface
from src.hardware import device_manager
import src.utils.logger as logger


class mainGUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        self.hardware = device_manager()
        self.confocal_interface = confocal_interface(hardware=self.hardware)
        self.confocal_interface.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mainGUI()
    myWindow.show()
    sys.exit(app.exec_())