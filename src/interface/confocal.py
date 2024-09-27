"""
This is the program that link the program with GUI
"""
import sys
import os.path
import time
import numpy
import yaml
from ui.uipy.confocal import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from matplotlib import cm
from collections import deque

from src.threads.confocal_threads import CountThread, MoveThread, ConfocalScanThread, XZScanThread, MaxThread, DataThread
from src.hardware import AllHardware

import src.utils.logger as logger


class mainGUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None, hardware=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Load defaults
        self.load_defaults()
        # Initialize plots
        self.init_xy_scan_plot()
        self.init_z_scan_plot()
        self.init_counts_plot()
        # Initialize hardware
        self.hardware = hardware
        # Initialize Cursor Lines
        self.cursor = None
        self.curh = self.ui.mplMap.axes.axhline(color='red', linewidth=1, visible=False)
        self.curh.set_ydata((float(self.ui.txtYcom.text()), float(self.ui.txtYcom.text())))
        self.curv = self.ui.mplMap.axes.axvline(color='red', linewidth=1, visible=False)
        self.curv.set_xdata((float(self.ui.txtXcom.text()), float(self.ui.txtXcom.text())))

        self.cursor_ZScan = None
        self.curh_ZScan = self.ui.mplMapZ.axes.axhline(color='red', linewidth=1, visible=False)
        self.curh_ZScan.set_ydata((float(self.ui.txtZcom.text()), float(self.ui.txtZcom.text())))
        self.curv_ZScan = self.ui.mplMapZ.axes.axvline(color='red', linewidth=1, visible=False)
        self.curv_ZScan.set_xdata((float(self.ui.txtXcom.text()), float(self.ui.txtXcom.text())))

        # Connect to qt Slots
        # Hardware Group
        self.ui.pbInitHW.clicked.connect(self.init_hardware)
        self.ui.pbCleanupHW.clicked.connect(self.cleanup_hardware)
        # Laser Group
        self.ui.pbLaserOn.clicked.connect(self.laser_on)
        self.ui.pbLaserOff.clicked.connect(self.laser_off)
        # Scan Group
        self.ui.pbFullRange.clicked.connect(self.set_full_range)
        self.ui.pbSelectRange.clicked.connect(self.select_range)
        self.ui.pbCenter.clicked.connect(self.set_center_range)
        self.ui.pbStart.clicked.connect(self.scan_start)
        self.ui.pbStop.clicked.connect(self.scan_stop)
        # Scan Group Z
        self.ui.pbFullRangeZ.clicked.connect(self.set_full_range_ZScan)
        self.ui.pbSelectRangeZ.clicked.connect(self.select_range_ZScan)
        self.ui.pbCenterZ.clicked.connect(self.set_center_range_Zscan)
        self.ui.pbStartZ.clicked.connect(self.scan_start_Z)
        self.ui.pbStopZ.clicked.connect(self.scan_stop_Z)


        # Cursor Group
        self.ui.pbNewCursor.clicked.connect(self.new_cursor)
        self.ui.pbShowCursor.clicked.connect(self.show_cursor)
        self.ui.pbHideCursor.clicked.connect(self.hide_cursor)
        self.ui.pbGoToMid.clicked.connect(self.go_to_mid)
        self.ui.pbGoTo.clicked.connect(self.go_to)
        self.ui.pbGetPos.clicked.connect(self.mark_current_position)
        # Move Group
        self.ui.pbXleft.clicked.connect(lambda: self.go_to('x-'))
        self.ui.pbXright.clicked.connect(lambda: self.go_to('x+'))
        self.ui.pbYdown.clicked.connect(lambda: self.go_to('y-'))
        self.ui.pbYup.clicked.connect(lambda: self.go_to('y+'))
        self.ui.pbZdown.clicked.connect(lambda: self.go_to('z-'))
        self.ui.pbZup.clicked.connect(lambda: self.go_to('z+'))
        '''missing keep NV'''
        # Counts Group
        self.ui.pbCount.clicked.connect(self.count_start)
        self.ui.cbCountFreq.currentIndexChanged[str].connect(self.change_rate)
        self.ui.pbMax.clicked.connect(self.maximize)
        # Plot Group XY
        self.ui.pbSaveData.clicked.connect(self.save_data)
        self.ui.pbReplot.clicked.connect(self.replot_image)
        self.ui.vsMax.sliderMoved.connect(self.modify_image)
        self.ui.vsMin.sliderMoved.connect(self.modify_image)
        # Plot Group Z
        self.ui.pbSaveData_ZScan.clicked.connect(self.save_data_ZScan)
        self.ui.pbReplot_ZScan.clicked.connect(self.replot_image_ZScan)
        self.ui.vsMax_ZScan.sliderMoved.connect(self.modify_image_ZScan)
        self.ui.vsMin_ZScan.sliderMoved.connect(self.modify_image_ZScan)
        # Load and Save defaults
        self.ui.actionOpen_Defaults.triggered.connect(self.open_defaults)
        self.ui.actionSave_Defaults.triggered.connect(self.save_defaults)

    # init methods
    def init_xy_scan_plot(self):
        # Image matplotlib widget
        fig = Figure()
        self.ui.mplMap = FigureCanvas(fig)
        self.ui.mplMap.setParent(self.ui.wMpl)
        self.ui.mplMap.axes = fig.add_subplot(111)
        self.ui.mplMap.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), self.ui.wMpl.size()))

        # Toolbar widget for image
        self.ui.mplToolbar = NavigationToolbar(self.ui.mplMap, self.ui.wToolbar)
        self.ui.mplToolbar.setGeometry(QtCore.QRect(0, 0, self.ui.wToolbar.size().width(), 31))
        self.ui.mplToolbar.setParent(self.ui.wToolbar)

        # Initialize Dummy Map Data
        self.init_xy_dummy_map()

    def init_xy_dummy_map(self):
        # Initialize Dummy Map Data
        xNum = int((float(self.ui.txtEndX.text()) - float(self.ui.txtStartX.text())) / float(self.ui.txtStepX.text()))
        yNum = int((float(self.ui.txtEndY.text()) - float(self.ui.txtStartY.text())) / float(self.ui.txtStepY.text()))
        self.map = numpy.random.randint(0, 100, size=(yNum, xNum))
        self.map[30][40] = 100000

        # Initialize Map
        self.mapColor = 'gist_earth'
        # See https://matplotlib.org/tutorials/colors/colormaps.html for colormap
        self.image = self.ui.mplMap.axes.imshow(self.map, cmap=cm.get_cmap(self.mapColor), vmin=0, vmax=self.map.max(),
                                                extent=[float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text()),
                                                        float(self.ui.txtStartY.text()), float(self.ui.txtEndY.text())],
                                                interpolation='nearest',
                                                origin='lower')
        # See https://matplotlib.org/gallery/images_contours_and_fields/interpolation_methods.html for interpolation
        self.ui.mplMap.axes.set_ylim([float(self.ui.txtStartY.text()), float(self.ui.txtEndY.text())])
        self.ui.mplMap.axes.set_xlim([float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text())])
        self.cbar = self.ui.mplMap.figure.colorbar(self.image)
        self.ui.mplMap.figure.tight_layout()

    def init_z_scan_plot(self):
        # Image matplotlib widget
        fig = Figure()
        self.ui.mplMapZ = FigureCanvas(fig)
        self.ui.mplMapZ.setParent(self.ui.wMpl_ZScan)
        self.ui.mplMapZ.axes = fig.add_subplot(111)
        self.ui.mplMapZ.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), self.ui.wMpl_ZScan.size()))

        # Toolbar widget for image
        self.ui.mplToolbarZ = NavigationToolbar(self.ui.mplMapZ, self.ui.wToolbar_ZScan)
        self.ui.mplToolbarZ.setGeometry(QtCore.QRect(0, 0, self.ui.wToolbar_ZScan.size().width(), 31))
        self.ui.mplToolbarZ.setParent(self.ui.wToolbar_ZScan)

        # Initialize Dummy Map Data
        self.init_z_dummy_map()

    def init_z_dummy_map(self):
        # Initialize Dummy Map Data
        xNum = int((float(self.ui.txtEndX.text()) - float(self.ui.txtStartX.text())) / float(self.ui.txtStepX.text()))
        yNum = int((float(self.ui.txtEndZ.text()) - float(self.ui.txtStartZ.text())) / float(self.ui.txtStepZ.text()))
        self.mapZ = numpy.random.randint(0, 100, size=(yNum, xNum))
        self.mapZ[10][10] = 100000

        # Initialize Map
        self.mapColor = 'gist_earth'
        # See https://matplotlib.org/tutorials/colors/colormaps.html for colormap
        self.imageZ = self.ui.mplMapZ.axes.imshow(self.mapZ, cmap=cm.get_cmap(self.mapColor), vmin=0, vmax=self.mapZ.max(),
                                                extent=[float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text()),
                                                        float(self.ui.txtStartZ.text()), float(self.ui.txtEndZ.text())],
                                                interpolation='nearest',
                                                origin='lower')
        # See https://matplotlib.org/gallery/images_contours_and_fields/interpolation_methods.html for interpolation
        self.ui.mplMapZ.axes.set_ylim([float(self.ui.txtStartZ.text()), float(self.ui.txtEndZ.text())])
        self.ui.mplMapZ.axes.set_xlim([float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text())])
        self.cbarZ = self.ui.mplMapZ.figure.colorbar(self.imageZ)
        self.ui.mplMapZ.figure.tight_layout()

    def init_counts_plot(self):
        # Counts plot matplotlib widget
        fig = Figure()
        self.ui.mplPlot = FigureCanvas(fig)
        self.ui.mplPlot.setParent(self.ui.wMplCounts)
        self.ui.mplPlot.axes = fig.add_subplot(111)
        self.ui.mplPlot.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), self.ui.wMplCounts.size()))

    def init_counts_dummy_data(self):
        # Initialize Dummy Counts Data
        self.countsX = deque(numpy.arange(10).tolist())
        self.countsY = deque(numpy.zeros(10, dtype=int).tolist())

        # Initialize counts plot
        self.countPlot, = self.ui.mplPlot.axes.plot(self.countsX, self.countsY)
        self.ui.mplPlot.axes.set_xlabel('time (s)')
        self.ui.mplPlot.figure.subplots_adjust(top=0.95, bottom=0.3, right=0.99)

    # Methods for QT slots
    # Hardware Group
    @QtCore.pyqtSlot()
    def init_hardware(self):
        self.ui.statusbar.showMessage('Initializing Hardware...')
        # Initialize...
        try:
            if self.hardware is None:
                self.hardware = AllHardware()
            # Connect Piezo Stage
            status = self.hardware.mover.scan_devices()
            if status == 0:
                self.hardware.mover.open_devices()
                self.init_position()
            else:
                print('Warning: Piezo stage hasn\'t been connected!')

            # Initialize thread (Need to initialize hardware first!!)
            # Initialize Count Thread
            self.cThread = CountThread(self.hardware)
            self.cThread.counts.connect(self.update_counts)
            self.cThread.finished.connect(self.count_stopped)
            # Initialize Move Thread
            self.mThread = MoveThread(self.hardware)
            self.mThread.moved.connect(self.gone_to)
            # Initialize Confocal Scan Thread
            self.sThread = ConfocalScanThread(self.hardware)
            self.sThread.update.connect(self.scan_data_back)
            self.sThread.finished.connect(self.scan_stopped)
            # Initialize XZ Scan Thread
            self.sThreadZ = XZScanThread(self.hardware)
            self.sThreadZ.update.connect(self.scan_data_back_ZScan)
            self.sThreadZ.finished.connect(self.scan_stopped_ZScan)
            # Initialize Max Thread
            self.maxThread = MaxThread(self.hardware)
            self.maxThread.counts.connect(self.update_counts)
            self.maxThread.moved.connect(self.gone_to)
            # Initialize Data Thread
            self.dThread = DataThread()
            self.dThread.update.connect(self.update_image)

        except BaseException as e:
            print(e)
            self.ui.statusbar.showMessage('Hardware Initialization Failed.')
            return
        # Set buttons available
        self.ui.pbCount.setEnabled(True)
        self.ui.cbCountFreq.setEnabled(True)
        self.ui.pbGoTo.setEnabled(True)
        self.ui.pbGoToMid.setEnabled(True)
        self.ui.pbLaserOn.setEnabled(True)
        self.ui.pbLaserOff.setEnabled(False)
        self.ui.pbMax.setEnabled(True)
        self.ui.pbKeepNV.setEnabled(True)
        self.ui.pbStart.setEnabled(True)
        self.ui.pbStartZ.setEnabled(True)
        self.ui.pbXleft.setEnabled(True)
        self.ui.pbXright.setEnabled(True)
        self.ui.pbYdown.setEnabled(True)
        self.ui.pbYup.setEnabled(True)
        self.ui.pbZdown.setEnabled(True)
        self.ui.pbZup.setEnabled(True)
        self.ui.pbInitHW.setEnabled(False)
        self.ui.pbCleanupHW.setEnabled(True)

        self.ui.statusbar.showMessage('Hardware Initialized Successfully.')

        self.stepMoveDic = {
            'x+': lambda: self.ui.txtXcom.setText(
                str(round(float(self.ui.txtXcom.text()) + float(self.ui.txtStepX.text()), 3))),

            'x-': lambda: self.ui.txtXcom.setText(
                str(round(float(self.ui.txtXcom.text()) - float(self.ui.txtStepX.text()), 3))),

            'y+': lambda: self.ui.txtYcom.setText(
                str(round(float(self.ui.txtYcom.text()) + float(self.ui.txtStepY.text()), 3))),

            'y-': lambda: self.ui.txtYcom.setText(
                str(round(float(self.ui.txtYcom.text()) - float(self.ui.txtStepY.text()), 3))),

            'z+': lambda: self.ui.txtZcom.setText(
                str(round(float(self.ui.txtZcom.text()) + float(self.ui.txtStep.text()), 3))),

            'z-': lambda: self.ui.txtZcom.setText(
                str(round(float(self.ui.txtZcom.text()) - float(self.ui.txtStep.text()), 3)))}

    def init_position(self):
        x = self.hardware.mover.read_position_single(channel=1)
        y = self.hardware.mover.read_position_single(channel=2)
        z = self.hardware.mover.read_position_single(channel=4)
        self.ui.txtX.setText(str(round(x, 3)))
        self.ui.txtY.setText(str(round(y, 3)))
        self.ui.txtZ.setText(str(round(z, 3)))
        self.ui.pbGetPos.setEnabled(True)

    @QtCore.pyqtSlot()
    def cleanup_hardware(self):
        # Set buttons unavailable
        self.ui.pbCount.setEnabled(False)
        self.ui.cbCountFreq.setEnabled(False)
        self.ui.pbGoTo.setEnabled(False)
        self.ui.pbGoToMid.setEnabled(False)
        self.ui.pbGetPos.setEnabled(False)
        self.ui.pbLaserOn.setEnabled(False)
        self.ui.pbLaserOff.setEnabled(False)
        self.ui.pbMax.setEnabled(False)
        self.ui.pbKeepNV.setEnabled(False)
        self.ui.pbStart.setEnabled(False)
        self.ui.pbStartZ.setEnabled(False)
        self.ui.pbStop.setEnabled(False)
        self.ui.pbStopZ.setEnabled(False)
        self.ui.pbXleft.setEnabled(False)
        self.ui.pbXright.setEnabled(False)
        self.ui.pbYdown.setEnabled(False)
        self.ui.pbYup.setEnabled(False)
        self.ui.pbZdown.setEnabled(False)
        self.ui.pbZup.setEnabled(False)

        __status = self.hardware.cleanup()
        if __status == 0:
            self.ui.statusbar.showMessage('Hardware Reset Successfully.')
            # self.hardware = None
            # Set button
            self.ui.pbInitHW.setEnabled(True)
            self.ui.pbCleanupHW.setEnabled(False)
        else:
            self.ui.statusbar.showMessage('Hardware Reset Failed.')

    # Laser Group
    @QtCore.pyqtSlot()
    def laser_on(self):
        self.hardware.pulser.laser_on()
        self.ui.pbLaserOn.setEnabled(False)
        self.ui.pbLaserOff.setEnabled(True)

    @QtCore.pyqtSlot()
    def laser_off(self):
        self.hardware.pulser.laser_off()
        self.ui.pbLaserOn.setEnabled(True)
        self.ui.pbLaserOff.setEnabled(False)

    # Scan Group
    @QtCore.pyqtSlot()
    def set_full_range(self):
        self.ui.txtStartX.setText('0')
        self.ui.txtEndX.setText('65')
        self.ui.txtStepX.setText('0.65')
        self.ui.txtStartY.setText('0')
        self.ui.txtEndY.setText('65')
        self.ui.txtStepY.setText('0.65')

    @QtCore.pyqtSlot()
    def select_range(self):
        if self.cursor:
            self.cursor.disconnect_events()
            self.cursor = None
            self.ui.mplMap.draw()

        self._cid = []
        cid = self.ui.mplMap.mpl_connect('axes_enter_event',
                                         lambda event: self.ui.mplMap.setCursor(QtCore.Qt.CrossCursor))
        self._cid.append(cid)
        cid = self.ui.mplMap.mpl_connect('axes_leave_event',
                                         lambda event: self.ui.mplMap.setCursor(QtCore.Qt.ArrowCursor))
        self._cid.append(cid)
        cid = self.ui.mplMap.mpl_connect('button_press_event', self.select_drag_start)
        self._cid.append(cid)

    def select_drag_start(self, event):
        if event.inaxes and event.x < 330:
            self.select_x0 = event.xdata
            self.select_y0 = event.ydata
            self._x0 = event.x
            self._y0 = event.y
            cid = self.ui.mplMap.mpl_connect('button_release_event', self.select_drag_end)
            self._cid.append(cid)
            cid = self.ui.mplMap.mpl_connect('motion_notify_event', self.select_dragging)
            self._cid.append(cid)

    def select_dragging(self, event):
        if event.inaxes and event.x < 330:
            self.select_x1 = event.xdata
            self.select_y1 = event.ydata

            x1 = event.x
            y1 = event.y
            x0 = self._x0
            y0 = self._y0
            height = self.ui.mplMap.figure.bbox.height
            y1 = height - y1
            y0 = height - y0

            if abs(x1 - x0) < abs(y1 - y0):
                if (x1 - x0) * (y1 - y0) > 0:
                    rect = [int(val) for val in (x0, y0, x1 - x0, x1 - x0)]
                    self.select_y1 = self.select_y0 + self.select_x0 - self.select_x1
                else:
                    rect = [int(val) for val in (x0, y0, x1 - x0, x0 - x1)]
                    self.select_y1 = self.select_y0 + self.select_x1 - self.select_x0
            else:
                if (x1 - x0) * (y1 - y0) > 0:
                    rect = [int(val) for val in (x0, y0, y1 - y0, y1 - y0)]
                    self.select_x1 = self.select_x0 + self.select_y0 - self.select_y1
                else:
                    rect = [int(val) for val in (x0, y0, y0 - y1, y1 - y0)]
                    self.select_x1 = self.select_x0 + self.select_y1 - self.select_y0
            self.ui.mplMap.drawRectangle(rect)

    def select_drag_end(self, event):
        self.ui.txtStartX.setText(str(round(min(self.select_x0, self.select_x1), 3)))
        self.ui.txtEndX.setText(str(round(max(self.select_x0, self.select_x1), 3)))
        self.ui.txtStepX.setText(str(round(abs(self.select_x0 - self.select_x1) / 100, 3)))
        self.ui.txtStartY.setText(str(round(min(self.select_y0, self.select_y1), 3)))
        self.ui.txtEndY.setText(str(round(max(self.select_y0, self.select_y1), 3)))
        self.ui.txtStepY.setText(str(round(abs(self.select_y0 - self.select_y1) / 100, 3)))
        self.ui.mplMap.setCursor(QtCore.Qt.ArrowCursor)
        for cid in self._cid:
            self.ui.mplMap.mpl_disconnect(cid)

    @QtCore.pyqtSlot()
    def set_center_range(self):
        x_val = round(float(self.ui.txtXcom.text()), 1)
        y_val = round(float(self.ui.txtYcom.text()), 1)
        d = float(self.ui.txtRange.text())
        self.ui.txtStartX.setText(str(round(x_val - d / 2, 3)))
        self.ui.txtStartY.setText(str(round(y_val - d / 2, 3)))
        self.ui.txtEndX.setText(str(round(x_val + d / 2, 3)))
        self.ui.txtEndY.setText(str(round(y_val + d / 2, 3)))
        self.ui.txtStepX.setText(str(round(d / 100, 3)))
        self.ui.txtStepY.setText(str(round(d / 100, 3)))

    @QtCore.pyqtSlot()
    def scan_start(self):
        self.ui.statusbar.showMessage('Scanning...')
        self.ui.pbCount.setEnabled(False)
        self.ui.pbGoTo.setEnabled(False)
        self.ui.pbGoToMid.setEnabled(False)
        self.ui.pbMax.setEnabled(False)
        self.ui.pbKeepNV.setEnabled(False)
        self.ui.pbXleft.setEnabled(False)
        self.ui.pbXright.setEnabled(False)
        self.ui.pbYdown.setEnabled(False)
        self.ui.pbYup.setEnabled(False)
        self.ui.pbZdown.setEnabled(False)
        self.ui.pbZup.setEnabled(False)
        self.ui.pbStart.setEnabled(False)
        self.ui.pbStop.setEnabled(True)
        self.ui.tabScanControl.setTabEnabled(1, False)
        self.ui.pbFullRange.setEnabled(False)
        self.ui.pbSelectRange.setEnabled(False)
        self.ui.pbCount.setEnabled(False)
        self.ui.txtStartX.setEnabled(False)
        self.ui.txtEndX.setEnabled(False)
        self.ui.txtStepX.setEnabled(False)
        self.ui.txtStartY.setEnabled(False)
        self.ui.txtEndY.setEnabled(False)
        self.ui.txtStepY.setEnabled(False)
        self.ui.rbPiezo.setEnabled(False)
        self.ui.rbGalvo.setEnabled(False)
        if self.ui.rbPiezo.isChecked():
            self.sThread.parameters = (float(self.ui.txtStartX.text()),
                                       float(self.ui.txtEndX.text()),
                                       float(self.ui.txtStepX.text()),
                                       float(self.ui.txtStartY.text()),
                                       float(self.ui.txtEndY.text()),
                                       float(self.ui.txtStepY.text()),
                                       float(self.ui.txtZcom.text()),
                                       float(self.ui.cbFreq.currentText())
                                       )
            self.dThread.xArr = numpy.arange(float(self.ui.txtStartX.text()),
                                             float(self.ui.txtEndX.text()),
                                             float(self.ui.txtStepX.text()))
            self.dThread.yArr = numpy.arange(float(self.ui.txtStartY.text()),
                                             float(self.ui.txtEndY.text()),
                                             float(self.ui.txtStepY.text()))
            self.dThread.raw = None
            self.dThread.map = numpy.zeros((len(self.dThread.yArr), len(self.dThread.xArr)), dtype=int)
            self.dThread.update.disconnect()
            self.dThread.update.connect(self.update_image)
            self.sThread.start()
        elif self.ui.rbGalvo.isChecked():
            pass

    @QtCore.pyqtSlot()
    def scan_stop(self):
        self.ui.statusbar.showMessage('Scan stopping...')
        self.ui.pbStop.setEnabled(False)
        self.ui.tabScanControl.setTabEnabled(1, True)
        self.ui.rbPiezo.setEnabled(True)
        self.ui.rbGalvo.setEnabled(True)
        # Stop the process
        if self.ui.rbPiezo.isChecked():
            self.sThread.running = False
        elif self.ui.rbGalvo.isChecked():
            pass

    @QtCore.pyqtSlot()
    def set_full_range_ZScan(self):
        self.ui.txtStartX.setText('0')
        self.ui.txtEndX.setText('65')
        self.ui.txtStepX.setText('0.65')
        self.ui.txtStartZ.setText('0')
        self.ui.txtEndZ.setText('30')
        self.ui.txtStepZ.setText('0.6')

    @QtCore.pyqtSlot()
    def select_range_ZScan(self):
        if self.cursor_ZScan:
            self.cursor_ZScan.disconnect_events()
            self.cursor_ZScan = None
            self.ui.mplMapZ.draw()

        self._cid = []
        cid = self.ui.mplMapZ.mpl_connect('axes_enter_event',
                                         lambda event: self.ui.mplMapZ.setCursor(QtCore.Qt.CrossCursor))
        self._cid.append(cid)
        cid = self.ui.mplMapZ.mpl_connect('axes_leave_event',
                                         lambda event: self.ui.mplMapZ.setCursor(QtCore.Qt.ArrowCursor))
        self._cid.append(cid)
        cid = self.ui.mplMapZ.mpl_connect('button_press_event', self.select_drag_start_Zscan)
        self._cid.append(cid)

    def select_drag_start_Zscan(self, event):
        if event.inaxes and event.x < 330:
            self.select_x0 = event.xdata
            self.select_y0 = event.ydata
            self._x0 = event.x
            self._y0 = event.y
            cid = self.ui.mplMapZ.mpl_connect('button_release_event', self.select_drag_end_Zscan)
            self._cid.append(cid)
            cid = self.ui.mplMapZ.mpl_connect('motion_notify_event', self.select_dragging_Zscan)
            self._cid.append(cid)

    def select_dragging_Zscan(self, event):
        if event.inaxes and event.x < 330:
            self.select_x1 = event.xdata
            self.select_y1 = event.ydata

            x1 = event.x
            y1 = event.y
            x0 = self._x0
            y0 = self._y0
            height = self.ui.mplMapZ.figure.bbox.height
            y1 = height - y1
            y0 = height - y0

            if abs(x1 - x0) < abs(y1 - y0):
                if (x1 - x0) * (y1 - y0) > 0:
                    rect = [int(val) for val in (x0, y0, x1 - x0, x1 - x0)]
                    self.select_y1 = self.select_y0 + self.select_x0 - self.select_x1
                else:
                    rect = [int(val) for val in (x0, y0, x1 - x0, x0 - x1)]
                    self.select_y1 = self.select_y0 + self.select_x1 - self.select_x0
            else:
                if (x1 - x0) * (y1 - y0) > 0:
                    rect = [int(val) for val in (x0, y0, y1 - y0, y1 - y0)]
                    self.select_x1 = self.select_x0 + self.select_y0 - self.select_y1
                else:
                    rect = [int(val) for val in (x0, y0, y0 - y1, y1 - y0)]
                    self.select_x1 = self.select_x0 + self.select_y1 - self.select_y0
            self.ui.mplMapZ.drawRectangle(rect)

    def select_drag_end_Zscan(self, event):
        self.ui.txtStartX.setText(str(round(min(self.select_x0, self.select_x1), 3)))
        self.ui.txtEndX.setText(str(round(max(self.select_x0, self.select_x1), 3)))
        self.ui.txtStepX.setText(str(round(abs(self.select_x0 - self.select_x1) / 100, 3)))
        self.ui.txtStartZ.setText(str(round(min(self.select_y0, self.select_y1), 3)))
        self.ui.txtEndZ.setText(str(round(max(self.select_y0, self.select_y1), 3)))
        self.ui.txtStepZ.setText(str(round(abs(self.select_y0 - self.select_y1) / 50, 3)))
        self.ui.mplMapZ.setCursor(QtCore.Qt.ArrowCursor)
        for cid in self._cid:
            self.ui.mplMapZ.mpl_disconnect(cid)

    def set_center_range_Zscan(self):
        x_val = round(float(self.ui.txtXcom.text()), 1)
        z_val = round(float(self.ui.txtZcom.text()), 1)
        d = float(self.ui.txtRange.text())
        self.ui.txtStartX.setText(str(round(x_val - d / 2, 3)))
        self.ui.txtStartZ.setText(str(round(z_val - d / 2, 3)))
        self.ui.txtEndX.setText(str(round(x_val + d / 2, 3)))
        self.ui.txtEndZ.setText(str(round(z_val + d / 2, 3)))
        self.ui.txtStepX.setText(str(round(d / 100, 3)))
        self.ui.txtStepZ.setText(str(round(d / 50, 3)))

    def scan_start_Z(self):
        self.ui.statusbar.showMessage('Scanning...')
        self.ui.pbCount.setEnabled(False)
        self.ui.pbGoTo.setEnabled(False)
        self.ui.pbGoToMid.setEnabled(False)
        self.ui.pbMax.setEnabled(False)
        self.ui.pbKeepNV.setEnabled(False)
        self.ui.pbXleft.setEnabled(False)
        self.ui.pbXright.setEnabled(False)
        self.ui.pbYdown.setEnabled(False)
        self.ui.pbYup.setEnabled(False)
        self.ui.pbZdown.setEnabled(False)
        self.ui.pbZup.setEnabled(False)
        self.ui.pbStartZ.setEnabled(False)
        self.ui.pbStopZ.setEnabled(True)
        self.ui.tabScanControl.setTabEnabled(0, False)
        self.ui.pbFullRange.setEnabled(False)
        self.ui.pbSelectRange.setEnabled(False)
        self.ui.pbCount.setEnabled(False)
        self.ui.txtStartX.setEnabled(False)
        self.ui.txtEndX.setEnabled(False)
        self.ui.txtStepX.setEnabled(False)
        self.ui.txtStartY.setEnabled(False)
        self.ui.txtEndY.setEnabled(False)
        self.ui.txtStepY.setEnabled(False)
        self.ui.rbPiezo.setEnabled(False)
        self.ui.rbGalvo.setEnabled(False)

        if self.ui.rbPiezo.isChecked():
            self.sThreadZ.parameters = (float(self.ui.txtStartX.text()),
                                        float(self.ui.txtEndX.text()),
                                        float(self.ui.txtStepX.text()),
                                        float(self.ui.txtStartZ.text()),
                                        float(self.ui.txtEndZ.text()),
                                        float(self.ui.txtStepZ.text()),
                                        float(self.ui.txtYcom.text()),
                                        float(self.ui.cbFreq.currentText())
                                        )
            self.dThread.xArr = numpy.arange(float(self.ui.txtStartX.text()),
                                             float(self.ui.txtEndX.text()),
                                             float(self.ui.txtStepX.text()))
            self.dThread.yArr = numpy.arange(float(self.ui.txtStartZ.text()),
                                             float(self.ui.txtEndZ.text()),
                                             float(self.ui.txtStepZ.text()))
            self.dThread.raw = None
            self.dThread.map = numpy.zeros((len(self.dThread.yArr), len(self.dThread.xArr)), dtype=int)
            self.dThread.update.disconnect()
            self.dThread.update.connect(self.update_image_ZScan)
            self.sThreadZ.start()
        elif self.ui.rbGalvo.isChecked():
            pass

    def scan_stop_Z(self):
        self.ui.statusbar.showMessage('Scan stopping...')
        self.ui.pbStopZ.setEnabled(False)
        self.ui.rbPiezo.setEnabled(True)
        self.ui.rbGalvo.setEnabled(True)
        self.ui.tabScanControl.setTabEnabled(0, True)
        # Stop the process
        if self.ui.rbPiezo.isChecked():
            self.sThreadZ.running = False
        elif self.ui.rbGalvo.isChecked():
            pass

    # Cursor Group
    @QtCore.pyqtSlot()
    def new_cursor(self):
        self.hide_cursor()
        self.cursor = Cursor(self.ui.mplMap.axes, useblit=True, color='red', linewidth=1)
        self.cursor.connect_event('button_press_event', self.new_cursor_marked)
        self.cursor_ZScan = Cursor(self.ui.mplMapZ.axes, useblit=True, color='red', linewidth=1)
        self.cursor_ZScan.connect_event('button_press_event', self.new_cursor_marked_ZScan)
        self.ui.mplMap.draw()
        self.ui.mplMapZ.draw()

    @QtCore.pyqtSlot()
    def new_cursor_marked(self, event):
        if event.inaxes and event.x < 330:
            x = round(event.xdata, 3)
            y = round(event.ydata, 3)
            self.ui.txtXcom.setText(str(x))
            self.ui.txtYcom.setText(str(y))
            self.cursor.disconnect_events()
            self.curh.set_ydata((y, y))
            self.curv.set_xdata((x, x))
            self.show_cursor()
            self.cursor = None

    def new_cursor_marked_ZScan(self, event):
        if event.inaxes and event.x < 330:
            x = round(event.xdata, 3)
            z = round(event.ydata, 3)
            self.ui.txtXcom.setText(str(x))
            self.ui.txtZcom.setText(str(z))
            self.cursor_ZScan.disconnect_events()
            self.curh_ZScan.set_ydata((z, z))
            self.curv_ZScan.set_xdata((x, x))
            self.show_cursor()
            self.cursor_ZScan = None

    @QtCore.pyqtSlot()
    def show_cursor(self):
        if self.cursor:
            self.cursor.disconnect_events()
            self.cursor = None
        if self.cursor_ZScan:
            self.cursor_ZScan.disconnect_events()
            self.cursor_ZScan = None
        # show xy cursor
        self.curh.set_visible(True)
        self.curh.set_ydata((float(self.ui.txtYcom.text()), float(self.ui.txtYcom.text())))
        self.curv.set_visible(True)
        self.curv.set_xdata((float(self.ui.txtXcom.text()), float(self.ui.txtXcom.text())))
        self.ui.mplMap.draw()
        # show z cursor
        self.curh_ZScan.set_visible(True)
        self.curh_ZScan.set_ydata((float(self.ui.txtZcom.text()), float(self.ui.txtZcom.text())))
        self.curv_ZScan.set_visible(True)
        self.curv_ZScan.set_xdata((float(self.ui.txtXcom.text()), float(self.ui.txtXcom.text())))
        self.ui.mplMapZ.draw()

        self.ui.pbShowCursor.setEnabled(False)
        self.ui.pbHideCursor.setEnabled(True)

    @QtCore.pyqtSlot()
    def hide_cursor(self):
        self.cur_vis = False
        # hide xy cursor
        self.curh.set_visible(False)
        self.curv.set_visible(False)
        self.ui.mplMap.draw()
        # hide z cursor
        self.curh_ZScan.set_visible(False)
        self.curv_ZScan.set_visible(False)
        self.ui.mplMapZ.draw()

        self.ui.pbShowCursor.setEnabled(True)
        self.ui.pbHideCursor.setEnabled(False)

    @QtCore.pyqtSlot()
    def go_to_mid(self):
        self.ui.txtXcom.setText('32.5')
        self.ui.txtYcom.setText('32.5')
        self.ui.txtZcom.setText('17.5')
        self.go_to()

    @QtCore.pyqtSlot()
    def go_to(self, *args):
        self.ui.pbStart.setEnabled(False)
        self.ui.pbMax.setEnabled(False)
        self.ui.pbGoToMid.setEnabled(False)
        self.ui.pbGoTo.setEnabled(False)
        self.ui.pbXleft.setEnabled(False)
        self.ui.pbXright.setEnabled(False)
        self.ui.pbYdown.setEnabled(False)
        self.ui.pbYup.setEnabled(False)
        self.ui.pbZdown.setEnabled(False)
        self.ui.pbZup.setEnabled(False)

        if args:
            self.stepMoveDic.get(args[0], lambda: 0)()
        if not self.ui.pbShowCursor.isEnabled() or self.cursor:
            self.show_cursor()
        if self.ui.rbPiezo.isChecked():
            self.mThread.command = self.cursorPosition
            self.mThread.start()
        elif self.ui.rbGalvo.isChecked():
            pass


    @QtCore.pyqtSlot()
    def mark_current_position(self):
        self.ui.txtXcom.setText(self.ui.txtX.text())
        self.ui.txtYcom.setText(self.ui.txtY.text())
        self.ui.txtZcom.setText(self.ui.txtZ.text())

    @property
    def cursorPosition(self):
        return [float(self.ui.txtXcom.text()), float(self.ui.txtYcom.text()), float(self.ui.txtZcom.text())]

    # Move Group
    # Counts Group
    @QtCore.pyqtSlot()
    def count_start(self):
        self.ui.statusbar.showMessage('Counting...')
        self.ui.pbMax.setEnabled(False)
        self.ui.pbKeepNV.setEnabled(False)
        self.ui.pbStart.setEnabled(False)
        self.ui.pbCount.setText('Off')

        self.cThread.start()
        self.ui.pbCount.clicked.disconnect()
        self.ui.pbCount.clicked.connect(self.count_stop)

    @QtCore.pyqtSlot()
    def count_stop(self):
        self.cThread.running = False

    @QtCore.pyqtSlot(str)
    def change_rate(self, s):
        new_freq = eval(s)
        self.cThread.count_freq = new_freq
        self.cThread.count_freq_changed = True

    @QtCore.pyqtSlot()
    def maximize(self):
        self.ui.pbStart.setEnabled(False)
        self.ui.pbMax.setEnabled(False)
        self.ui.pbGoToMid.setEnabled(False)
        self.ui.pbGoTo.setEnabled(False)
        self.ui.pbXleft.setEnabled(False)
        self.ui.pbXright.setEnabled(False)
        self.ui.pbYdown.setEnabled(False)
        self.ui.pbYup.setEnabled(False)
        self.ui.pbZdown.setEnabled(False)
        self.ui.pbZup.setEnabled(False)
        self.ui.pbCount.setEnabled(False)

        self.maxThread.step = round(float(self.ui.txtStep.text()), 3)
        self.maxThread.start()

    # Plot Group
    @QtCore.pyqtSlot()
    def save_data(self):
        try:
            self.saved_data = self.actualData_xy
        except:
            sys.stderr.write('No data to be saved!\n')
            return
        self.save_data_uni()

    @QtCore.pyqtSlot()
    def save_data_ZScan(self):
        try:
            self.saved_data = self.actualData_z
        except:
            sys.stderr.write('No data to be saved!\n')
            return
        self.save_data_uni()


    def save_data_uni(self):
        directory = QtWidgets.QFileDialog.getSaveFileName(self, 'Enter save file', "", "Text (*.txt)")
        directory = str(directory[0].replace('/', '\\'))
        if directory != '':
            f = open(directory, 'w')
            for each_datapoint in self.saved_data:
                f.write(str(each_datapoint[0]) + '\t' + str(each_datapoint[1]) + '\t' + str(each_datapoint[2]) + '\n')
            f.close()
        else:
            sys.stderr.write('No file selected\n')


    @QtCore.pyqtSlot()
    def replot_image(self):
        self.ui.mplMap.figure.clear()
        self.ui.mplMap.axes = self.ui.mplMap.figure.add_subplot(111)
        self.image = self.ui.mplMap.axes.imshow(self.map,
                                                cmap=cm.get_cmap(self.mapColor),
                                                vmin=0, vmax=self.map.max(),
                                                extent=[float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text()),
                                                        float(self.ui.txtStartY.text()), float(self.ui.txtEndY.text())],
                                                interpolation='nearest',
                                                origin='lower')
        # See https://matplotlib.org/gallery/images_contours_and_fields/interpolation_methods.html for interpolation

        self.ui.mplMap.axes.set_ylim([float(self.ui.txtStartY.text()), float(self.ui.txtEndY.text())])
        self.ui.mplMap.axes.set_xlim([float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text())])
        self.cbar = self.ui.mplMap.figure.colorbar(self.image)
        self.ui.mplMap.figure.tight_layout()

        self.cursor = None
        self.curh = self.ui.mplMap.axes.axhline(color='red', linewidth=1, visible=False)
        self.curh.set_ydata((float(self.ui.txtYcom.text()), float(self.ui.txtYcom.text())))
        self.curv = self.ui.mplMap.axes.axvline(color='red', linewidth=1, visible=False)
        self.curv.set_xdata((float(self.ui.txtXcom.text()), float(self.ui.txtXcom.text())))

        self.modify_image()

    @QtCore.pyqtSlot()
    def replot_image_ZScan(self):
        self.ui.mplMapZ.figure.clear()
        self.ui.mplMapZ.axes = self.ui.mplMapZ.figure.add_subplot(111)
        self.imageZ = self.ui.mplMapZ.axes.imshow(self.mapZ,
                                                cmap=cm.get_cmap(self.mapColor),
                                                vmin=0, vmax=self.mapZ.max(),
                                                extent=[float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text()),
                                                        float(self.ui.txtStartZ.text()), float(self.ui.txtEndZ.text())],
                                                interpolation='nearest',
                                                origin='lower')
        # See https://matplotlib.org/gallery/images_contours_and_fields/interpolation_methods.html for interpolation

        self.ui.mplMapZ.axes.set_ylim([float(self.ui.txtStartZ.text()), float(self.ui.txtEndZ.text())])
        self.ui.mplMapZ.axes.set_xlim([float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text())])
        self.cbarZ = self.ui.mplMapZ.figure.colorbar(self.imageZ)
        self.ui.mplMapZ.figure.tight_layout()

        self.cursor_ZScan = None
        self.curh_ZScan = self.ui.mplMapZ.axes.axhline(color='red', linewidth=1, visible=False)
        self.curh_ZScan.set_ydata((float(self.ui.txtZcom.text()), float(self.ui.txtZcom.text())))
        self.curv_ZScan = self.ui.mplMapZ.axes.axvline(color='red', linewidth=1, visible=False)
        self.curv_ZScan.set_xdata((float(self.ui.txtXcom.text()), float(self.ui.txtXcom.text())))

        self.modify_image_ZScan()

    @QtCore.pyqtSlot()
    def modify_image(self):
        val_max = self.ui.vsMax.value()
        val_min = self.ui.vsMin.value()
        vmax = self.map.max() * (10 ** ((val_max + 1) / 20)) / 1000
        vmin = min(self.map.mean(), vmax) * val_min / 100

        self.image.set_clim(vmin, vmax)
        self.ui.mplMap.draw()

    @QtCore.pyqtSlot()
    def modify_image_ZScan(self):
        val_max = self.ui.vsMax_ZScan.value()
        val_min = self.ui.vsMin_ZScan.value()
        vmax = self.mapZ.max() * (10 ** ((val_max + 1) / 20)) / 1000
        vmin = min(self.mapZ.mean(), vmax) * val_min / 100

        self.imageZ.set_clim(vmin, vmax)
        self.ui.mplMapZ.draw()

    # Load and Save defaults
    @QtCore.pyqtSlot()
    def open_defaults(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        location, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose Defaults File', directory)
        if location != '':
            self.load_defaults(location)


    def load_defaults(self, config_path='config/config_confocal.yaml'):
        self.config_confocal = load_config(config_path=config_path)
        self.ui.txtStartX.setText(str(self.config_confocal['scan']['x']['start']))
        self.ui.txtStartY.setText(str(self.config_confocal['scan']['y']['start']))
        self.ui.txtStartZ.setText(str(self.config_confocal['scan']['z']['start']))
        self.ui.txtEndX.setText(str(self.config_confocal['scan']['x']['end']))
        self.ui.txtEndY.setText(str(self.config_confocal['scan']['y']['end']))
        self.ui.txtEndZ.setText(str(self.config_confocal['scan']['z']['end']))
        self.ui.txtStepX.setText(str(self.config_confocal['scan']['x']['step']))
        self.ui.txtStepY.setText(str(self.config_confocal['scan']['y']['step']))
        self.ui.txtStepZ.setText(str(self.config_confocal['scan']['z']['step']))
        self.ui.txtStep.setText(str(self.config_confocal['move']['step']))
        self.ui.txtXcom.setText(str(self.config_confocal['cursor']['x']))
        self.ui.txtYcom.setText(str(self.config_confocal['cursor']['y']))
        self.ui.txtZcom.setText(str(self.config_confocal['cursor']['z']))
        self.ui.txtRange.setText(str(self.config_confocal['scan']['range']))
        if self.config_confocal['scanner'] == 'piezo':
            self.ui.rbPiezo.setChecked(True)
        elif self.config_confocal['scanner'] == 'galvo':
            self.ui.rbGalvo.setChecked(True)

    @QtCore.pyqtSlot()
    def save_defaults(self, config_path='config/config_confocal.yaml'):
        self.config_confocal['scan']['x']['start'] = float(self.ui.txtStartX.text())
        self.config_confocal['scan']['y']['start'] = float(self.ui.txtStartY.text())
        self.config_confocal['scan']['z']['start'] = float(self.ui.txtStartZ.text())
        self.config_confocal['scan']['x']['end'] = float(self.ui.txtEndX.text())
        self.config_confocal['scan']['y']['end'] = float(self.ui.txtEndY.text())
        self.config_confocal['scan']['z']['end'] = float(self.ui.txtEndZ.text())
        self.config_confocal['scan']['x']['step'] = float(self.ui.txtStepX.text())
        self.config_confocal['scan']['y']['step'] = float(self.ui.txtStepY.text())
        self.config_confocal['scan']['z']['step'] = float(self.ui.txtStepZ.text())
        self.config_confocal['move']['step'] = float(self.ui.txtStep.text())
        self.config_confocal['cursor']['x'] = float(self.ui.txtXcom.text())
        self.config_confocal['cursor']['y'] = float(self.ui.txtYcom.text())
        self.config_confocal['cursor']['z'] = float(self.ui.txtZcom.text())
        self.config_confocal['scan']['range'] = float(self.ui.txtRange.text())
        if self.ui.rbPiezo.isChecked():
            self.config_confocal['scanner'] = 'piezo'
        elif self.ui.rbGalvo.isChecked():
            self.config_confocal['scanner'] = 'galvo'
        save_config(config=self.config_confocal, config_path=config_path)


    # Thread methods
    # cThread
    # Run when signal 'counts' emit
    @QtCore.pyqtSlot(int)
    def update_counts(self, data):
        self.ui.lcdNumber.display(int(data))
        self.countsY.append(data)
        self.countsY.popleft()
        a = numpy.array(self.countsY)
        yBot = a.min() * 0.7
        yTop = (a.max() + 1) * 1.1
        self.countPlot.set_ydata(self.countsY)
        self.ui.mplPlot.axes.set_ylim(bottom=yBot, top=yTop)
        self.ui.mplPlot.draw()

    # Run when finish
    @QtCore.pyqtSlot()
    def count_stopped(self):
        self.ui.statusbar.clearMessage()
        self.ui.pbMax.setEnabled(True)
        self.ui.pbKeepNV.setEnabled(True)
        self.ui.pbStart.setEnabled(True)
        self.ui.pbCount.setText('On')
        self.ui.pbCount.clicked.disconnect()
        self.ui.pbCount.clicked.connect(self.count_start)

    # mThread
    # Run when signal 'moved' emit
    @QtCore.pyqtSlot(float, float, float)
    def gone_to(self, x, y, z):
        self.ui.txtX.setText(str(round(x, 3)))
        self.ui.txtY.setText(str(round(y, 3)))
        self.ui.txtZ.setText(str(round(z, 3)))
        if not self.cThread.running:
            self.ui.pbStart.setEnabled(True)
        self.ui.pbMax.setEnabled(True)
        self.ui.pbGoTo.setEnabled(True)
        self.ui.pbGoToMid.setEnabled(True)
        self.ui.pbXleft.setEnabled(True)
        self.ui.pbXright.setEnabled(True)
        self.ui.pbYdown.setEnabled(True)
        self.ui.pbYup.setEnabled(True)
        self.ui.pbZdown.setEnabled(True)
        self.ui.pbZup.setEnabled(True)
        self.ui.pbCount.setEnabled(True)

    # sThread
    # Run when signal 'update' emit
    @QtCore.pyqtSlot(float, list, list)
    def scan_data_back(self, y, posData, countsData):
        self.dThread.y = y
        self.dThread.xData = posData
        self.dThread.countsData = countsData
        self.dThread.start()

    @QtCore.pyqtSlot()
    def scan_stopped(self):
        self.ui.statusbar.showMessage('Scanning stopped.')
        self.ui.pbCount.setEnabled(True)
        self.ui.pbGoTo.setEnabled(True)
        self.ui.pbGoToMid.setEnabled(True)
        self.ui.pbMax.setEnabled(True)
        self.ui.pbKeepNV.setEnabled(True)
        self.ui.pbXleft.setEnabled(True)
        self.ui.pbXright.setEnabled(True)
        self.ui.pbYdown.setEnabled(True)
        self.ui.pbYup.setEnabled(True)
        self.ui.pbZdown.setEnabled(True)
        self.ui.pbZup.setEnabled(True)
        self.ui.pbStart.setEnabled(True)
        self.ui.pbStartZ.setEnabled(True)
        self.ui.pbStop.setEnabled(False)
        self.ui.pbStopZ.setEnabled(False)
        self.ui.pbFullRange.setEnabled(True)
        self.ui.pbSelectRange.setEnabled(True)
        self.ui.pbCount.setEnabled(True)
        self.ui.txtStartX.setEnabled(True)
        self.ui.txtEndX.setEnabled(True)
        self.ui.txtStepX.setEnabled(True)
        self.ui.txtStartY.setEnabled(True)
        self.ui.txtEndY.setEnabled(True)
        self.ui.txtStepY.setEnabled(True)
        try:
            self.actualData_xy = self.dThread.raw
        except:
            return

    # sThreadZ
    # Run when signal 'update' emit
    @QtCore.pyqtSlot(float, list, list)
    def scan_data_back_ZScan(self, z, posData, countsData):
        self.dThread.y = z
        self.dThread.xData = posData
        self.dThread.countsData = countsData
        self.dThread.start()

    @QtCore.pyqtSlot()
    def scan_stopped_ZScan(self):
        self.ui.statusbar.showMessage('Scanning stopped.')
        self.ui.pbCount.setEnabled(True)
        self.ui.pbGoTo.setEnabled(True)
        self.ui.pbGoToMid.setEnabled(True)
        self.ui.pbMax.setEnabled(True)
        self.ui.pbKeepNV.setEnabled(True)
        self.ui.pbXleft.setEnabled(True)
        self.ui.pbXright.setEnabled(True)
        self.ui.pbYdown.setEnabled(True)
        self.ui.pbYup.setEnabled(True)
        self.ui.pbZdown.setEnabled(True)
        self.ui.pbZup.setEnabled(True)
        self.ui.pbStart.setEnabled(True)
        self.ui.pbStartZ.setEnabled(True)
        self.ui.pbStop.setEnabled(False)
        self.ui.pbStopZ.setEnabled(False)
        self.ui.pbFullRange.setEnabled(True)
        self.ui.pbSelectRange.setEnabled(True)
        self.ui.pbCount.setEnabled(True)
        self.ui.txtStartX.setEnabled(True)
        self.ui.txtEndX.setEnabled(True)
        self.ui.txtStepX.setEnabled(True)
        self.ui.txtStartY.setEnabled(True)
        self.ui.txtEndY.setEnabled(True)
        self.ui.txtStepY.setEnabled(True)
        try:
            self.actualData_z = self.dThread.raw
        except:
            return

    # dThread
    # Run when signal 'update' emit
    @QtCore.pyqtSlot(numpy.ndarray)
    def update_image(self, map_array):
        self.ui.statusbar.showMessage('updating...' + str(time.perf_counter()))
        print('updating...', time.perf_counter())
        self.map = map_array
        self.image.set_data(self.map)
        self.image.set_extent(
            [float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text()), float(self.ui.txtStartY.text()),
             float(self.ui.txtEndY.text())])

        self.ui.mplMap.axes.set_ylim([float(self.ui.txtStartY.text()), float(self.ui.txtEndY.text())])
        self.ui.mplMap.axes.set_xlim([float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text())])

        self.ui.vsMax.setValue(59)
        self.ui.vsMin.setValue(0)

        self.image.set_clim(0, self.map.max())
        self.ui.mplMap.draw()

    @QtCore.pyqtSlot(numpy.ndarray)
    def update_image_ZScan(self, map_array):
        self.ui.statusbar.showMessage('updating...' + str(time.perf_counter()))
        print('updating...', time.perf_counter())
        self.mapZ = map_array
        self.imageZ.set_data(self.mapZ)
        self.imageZ.set_extent(
            [float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text()), float(self.ui.txtStartZ.text()),
             float(self.ui.txtEndZ.text())])

        self.ui.mplMapZ.axes.set_ylim([float(self.ui.txtStartZ.text()), float(self.ui.txtEndZ.text())])
        self.ui.mplMapZ.axes.set_xlim([float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text())])

        self.ui.vsMax_ZScan.setValue(59)
        self.ui.vsMin_ZScan.setValue(0)

        self.imageZ.set_clim(0, self.mapZ.max())
        self.ui.mplMapZ.draw()

    # Run when close the program
    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Message', quit_msg, QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.save_defaults()
            if self.hardware is not None:
                self.cleanup_hardware()
            event.accept()
        else:
            event.ignore()


def load_config(config_path):
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config


def save_config(config, config_path):
    with open(config_path, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mainGUI()
    myWindow.show()
    sys.exit(app.exec_())
