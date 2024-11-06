"""
This is the program that link the program with GUI
"""
import sys
import os.path
import time
import numpy
import yaml
import tempfile
import pickle
from ui.uipy.confocal.mainWindow import Ui_Confocal
from PyQt5 import QtWidgets, QtCore
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from matplotlib import cm
from collections import deque

from src.threads.confocal_threads import DataThread, MoveThread, MoveThread_galvo, ConfocalScanThread, \
    ConfocalScanThread_galvo, CountThread, MaxThread, MaxThread_galvo, XZScanThread, XZScanThread_galvo

import src.utils.logger as logger


class mainGUI(QtWidgets.QMainWindow):
    SIGNAL_ExpConfocalClose = QtCore.pyqtSignal(name='ExpConfocalClose')
    XY_MIN_PIEZO = 0.0  # um
    XY_MAX_PIEZO = 65.0  # um
    XY_MIN_GALVO = -0.4  # V
    XY_MAX_GALVO = 0.4  # V
    Z_MIN_PIEZO = 0.0  # um
    Z_MAX_PIEZO = 35.0  # um
    CACHE_LIFE = 7  # days

    def __init__(self, parent=None, hardware=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Confocal()
        self.ui.setupUi(self)
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache\\confocal")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.scanning_cache = {
            "piezo_plot": tempfile.NamedTemporaryFile(dir=self.cache_dir, delete=False),
            "piezo_raw": tempfile.NamedTemporaryFile(dir=self.cache_dir, delete=False),
            "galvo_plot": tempfile.NamedTemporaryFile(dir=self.cache_dir, delete=False),
            "galvo_raw": tempfile.NamedTemporaryFile(dir=self.cache_dir, delete=False)
        }

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
        self.ui.rbGalvo.toggled.connect(self.scanner_changed)
        # self.ui.rbPiezo.toggled.connect(self.scanner_changed)
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
        self.ui.cbCountFreq.currentIndexChanged[str].connect(self.change_count_rate)
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

    def init_xy_dummy_data(self):
        # Initialize Dummy Map Data
        xNum = int((float(self.ui.txtEndX.text()) - float(self.ui.txtStartX.text())) / float(self.ui.txtStepX.text()))
        yNum = int((float(self.ui.txtEndY.text()) - float(self.ui.txtStartY.text())) / float(self.ui.txtStepY.text()))
        self.map = numpy.random.randint(0, 100, size=(yNum, xNum))
        self.map[30][40] = 100000

    def init_xy_dummy_map(self):
        self.init_xy_dummy_data()
        # Initialize Map
        self.mapColor = 'gist_earth'
        # See https://matplotlib.org/tutorials/colors/colormaps.html for colormap
        self.image = self.ui.mplMap.axes.imshow(self.map, cmap=matplotlib.colormaps.get_cmap(self.mapColor), vmin=0,
                                                vmax=self.map.max(),
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

    def init_z_dummy_data(self):
        # Initialize Dummy Map Data
        xNum = int((float(self.ui.txtEndX.text()) - float(self.ui.txtStartX.text())) / float(self.ui.txtStepX.text()))
        yNum = int((float(self.ui.txtEndZ.text()) - float(self.ui.txtStartZ.text())) / float(self.ui.txtStepZ.text()))
        self.mapZ = numpy.random.randint(0, 100, size=(yNum, xNum))
        self.mapZ[10][10] = 100000

    def init_z_dummy_map(self):
        self.init_z_dummy_data()
        # Initialize Map
        self.mapColor = 'gist_earth'
        # See https://matplotlib.org/tutorials/colors/colormaps.html for colormap
        self.imageZ = self.ui.mplMapZ.axes.imshow(self.mapZ, cmap=matplotlib.colormaps.get_cmap(self.mapColor), vmin=0,
                                                  vmax=self.mapZ.max(),
                                                  extent=[float(self.ui.txtStartX.text()),
                                                          float(self.ui.txtEndX.text()),
                                                          float(self.ui.txtStartZ.text()),
                                                          float(self.ui.txtEndZ.text())],
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
        # Initialize Dummy Count Data
        self.init_counts_dummy_data()

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
            self.hardware.init_mover()
            self.hardware.init_scanner()
            self.hardware.init_pulser()
            self.hardware.init_counter()
            self.hardware.init_ni()
            if self.hardware.mover_status:
                self.update_current_position()
                self.ui.pbGetPos.setEnabled(True)
            # Initialize thread (Need to initialize hardware first!!)
            # Initialize Count Thread
            self.cThread = CountThread(self.hardware)
            self.cThread.counts.connect(self.update_counts)
            self.cThread.finished.connect(self.count_stopped)
            # Initialize Move Thread
            self.mThread = MoveThread(self.hardware)
            self.mThread.moved.connect(self.gone_to)
            # Initialize Move Thread Galvo
            self.gmThread = MoveThread_galvo(self.hardware)
            self.gmThread.moved.connect(self.gone_to)
            # Initialize Confocal Scan Thread
            self.sThread = ConfocalScanThread(self.hardware)
            self.sThread.update.connect(self.scan_data_back)
            self.sThread.finished.connect(self.scan_stopped)
            # Initialize Confocal Scan Thread Galvo
            self.gsThread = ConfocalScanThread_galvo(self.hardware)
            self.gsThread.update.connect(self.scan_data_back)
            self.gsThread.finished.connect(self.scan_stopped)
            # Initialize XZ Scan Thread
            self.sThreadZ = XZScanThread(self.hardware)
            self.sThreadZ.update.connect(self.scan_data_back_ZScan)
            self.sThreadZ.finished.connect(self.scan_stopped_ZScan)
            # Initialize XZ Scan Thread Galvo
            self.gsThreadZ = XZScanThread_galvo(self.hardware)
            self.gsThreadZ.update.connect(self.scan_data_back_ZScan)
            self.gsThreadZ.finished.connect(self.scan_stopped_ZScan)
            # Initialize Max Thread
            self.maxThread = MaxThread(self.hardware)
            self.maxThread.counts.connect(self.update_counts)
            self.maxThread.moved.connect(self.gone_to)
            # Initialize Max Thread Galvo
            self.gmaxThread = MaxThread_galvo(self.hardware)
            self.gmaxThread.counts.connect(self.update_counts)
            self.gmaxThread.moved.connect(self.gone_to)
            # Initialize Data Thread
            self.dThread = DataThread()
            self.dThread.update.connect(self.update_image_data)

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
        # set step move dic for move point
        self.stepMoveDic = {
            'x+': lambda: self.ui.txtXcom.setText(
                str(round(float(self.ui.txtXcom.text()) + float(self.ui.txtStepXY.text()), 3))),

            'x-': lambda: self.ui.txtXcom.setText(
                str(round(float(self.ui.txtXcom.text()) - float(self.ui.txtStepXY.text()), 3))),

            'y+': lambda: self.ui.txtYcom.setText(
                str(round(float(self.ui.txtYcom.text()) + float(self.ui.txtStepXY.text()), 3))),

            'y-': lambda: self.ui.txtYcom.setText(
                str(round(float(self.ui.txtYcom.text()) - float(self.ui.txtStepXY.text()), 3))),

            'z+': lambda: self.ui.txtZcom.setText(
                str(round(float(self.ui.txtZcom.text()) + float(self.ui.txtStep.text()), 3))),

            'z-': lambda: self.ui.txtZcom.setText(
                str(round(float(self.ui.txtZcom.text()) - float(self.ui.txtStep.text()), 3)))}

    def update_current_position(self) -> None:
        """
        get real position of piezo and galvo by measured the realtime position, then update the ui.
        :return: None
        """
        try:
            if self.ui.rbPiezo.isChecked():
                x = self.hardware.mover.read_position_single(channel=1)
                y = self.hardware.mover.read_position_single(channel=2)
            elif self.ui.rbGalvo.isChecked():
                x, y = self.hardware.scanner.read_current_position()
            z = self.hardware.mover.read_position_single(channel=4)
            self.ui.txtX.setText(str(round(x, 3)))
            self.ui.txtY.setText(str(round(y, 3)))
            self.ui.txtZ.setText(str(round(z, 3)))
        except Exception as e:
            logger.logger.info(e)

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

        self.hardware.reset_mover()
        self.hardware.reset_scanner()
        self.hardware.reset_pulser()
        self.hardware.reset_counter()
        self.hardware.reset_ni()
        __status = max(self.hardware.mover_status, self.hardware.scanner_status, self.hardware.pulser_status,
                       self.hardware.counter_status, self.hardware.triggered_location_sensor_status,
                       self.hardware.timer_status, self.hardware.one_time_counter_status)
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
    # function for xy scan
    @QtCore.pyqtSlot()
    def set_full_range(self):
        if self.ui.rbPiezo.isChecked():
            self.ui.txtStartX.setText(str(self.XY_MIN_PIEZO))
            self.ui.txtEndX.setText(str(self.XY_MAX_PIEZO))
            self.ui.txtStepX.setText(str(round((self.XY_MAX_PIEZO - self.XY_MIN_PIEZO) / 100, 3)))
            self.ui.txtStartY.setText(str(self.XY_MIN_PIEZO))
            self.ui.txtEndY.setText(str(self.XY_MAX_PIEZO))
            self.ui.txtStepY.setText(str(round((self.XY_MAX_PIEZO - self.XY_MIN_PIEZO) / 100, 3)))
        elif self.ui.rbGalvo.isChecked():
            self.ui.txtStartX.setText(str(self.XY_MIN_GALVO))
            self.ui.txtEndX.setText(str(self.XY_MAX_GALVO))
            self.ui.txtStepX.setText(str(round((self.XY_MAX_GALVO - self.XY_MIN_GALVO) / 100, 3)))
            self.ui.txtStartY.setText(str(self.XY_MIN_GALVO))
            self.ui.txtEndY.setText(str(self.XY_MAX_GALVO))
            self.ui.txtStepY.setText(str(round((self.XY_MAX_GALVO - self.XY_MIN_GALVO) / 100, 3)))

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

        self.dThread.xArr = numpy.linspace(start=float(self.ui.txtStartX.text()),
                                           stop=float(self.ui.txtEndX.text()),
                                           num=round((float(self.ui.txtEndX.text()) - float(self.ui.txtStartX.text())) /
                                                     float(self.ui.txtStepX.text())),
                                           endpoint=True,
                                           dtype=float)
        self.dThread.yArr = numpy.linspace(start=float(self.ui.txtStartY.text()),
                                           stop=float(self.ui.txtEndY.text()),
                                           num=round((float(self.ui.txtEndY.text()) - float(self.ui.txtStartY.text())) /
                                                     float(self.ui.txtStepY.text())),
                                           endpoint=True,
                                           dtype=float)
        self.dThread.raw = None
        self.dThread.map = numpy.zeros((len(self.dThread.yArr), len(self.dThread.xArr)), dtype=int)
        self.dThread.update.disconnect()
        self.dThread.update.connect(self.update_image_data)

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

            self.sThread.start()
        elif self.ui.rbGalvo.isChecked():
            self.gsThread.parameters = (float(self.ui.txtStartX.text()),
                                        float(self.ui.txtEndX.text()),
                                        float(self.ui.txtStepX.text()),
                                        float(self.ui.txtStartY.text()),
                                        float(self.ui.txtEndY.text()),
                                        float(self.ui.txtStepY.text()),
                                        float(self.ui.txtZcom.text()),
                                        float(self.ui.cbFreq.currentText())
                                        )

            self.gsThread.start()

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
            self.gsThread.running = False

    # function for z scan
    @QtCore.pyqtSlot()
    def set_full_range_ZScan(self):
        if self.ui.rbPiezo.isChecked():
            self.ui.txtStartX.setText(str(self.XY_MIN_PIEZO))
            self.ui.txtEndX.setText(str(self.XY_MAX_PIEZO))
            self.ui.txtStepX.setText(str(round((self.XY_MAX_PIEZO - self.XY_MIN_PIEZO) / 100, 3)))
            self.ui.txtStartZ.setText(str(self.Z_MIN_PIEZO))
            self.ui.txtEndZ.setText(str(self.Z_MAX_PIEZO))
            self.ui.txtStepZ.setText(str(round((self.Z_MAX_PIEZO - self.Z_MIN_PIEZO) / 50, 3)))
        elif self.ui.rbGalvo.isChecked():
            self.ui.txtStartX.setText(str(self.XY_MIN_GALVO))
            self.ui.txtEndX.setText(str(self.XY_MAX_GALVO))
            self.ui.txtStepX.setText(str(round((self.XY_MAX_GALVO - self.XY_MIN_GALVO) / 100, 3)))
            self.ui.txtStartZ.setText(str(self.Z_MIN_PIEZO))
            self.ui.txtEndZ.setText(str(self.Z_MAX_PIEZO))
            self.ui.txtStepZ.setText(str(round((self.Z_MAX_PIEZO - self.Z_MIN_PIEZO) / 50, 3)))

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
        d = float(self.ui.txtRangeZ.text())
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

        self.dThread.xArr = numpy.linspace(start=float(self.ui.txtStartX.text()),
                                           stop=float(self.ui.txtEndX.text()),
                                           num=round((float(self.ui.txtEndX.text()) - float(self.ui.txtStartX.text())) /
                                                     float(self.ui.txtStepX.text())),
                                           endpoint=True,
                                           dtype=float)
        self.dThread.yArr = numpy.linspace(start=float(self.ui.txtStartZ.text()),
                                           stop=float(self.ui.txtEndZ.text()),
                                           num=round((float(self.ui.txtEndZ.text()) - float(self.ui.txtStartZ.text())) /
                                                     float(self.ui.txtStepZ.text())),
                                           endpoint=True,
                                           dtype=float)

        self.dThread.raw = None
        self.dThread.map = numpy.zeros((len(self.dThread.yArr), len(self.dThread.xArr)), dtype=int)
        self.dThread.update.disconnect()
        self.dThread.update.connect(self.update_image_data_ZScan)

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
            self.sThreadZ.start()
        elif self.ui.rbGalvo.isChecked():
            self.gsThreadZ.parameters = (float(self.ui.txtStartX.text()),
                                         float(self.ui.txtEndX.text()),
                                         float(self.ui.txtStepX.text()),
                                         float(self.ui.txtStartZ.text()),
                                         float(self.ui.txtEndZ.text()),
                                         float(self.ui.txtStepZ.text()),
                                         float(self.ui.txtYcom.text()),
                                         float(self.ui.cbFreq.currentText())
                                         )
            self.gsThreadZ.start()

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
            self.gsThreadZ.running = False

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
        if self.ui.rbPiezo.isChecked():
            self.ui.txtXcom.setText(str(round((self.XY_MAX_PIEZO + self.XY_MIN_PIEZO) / 2, 3)))
            self.ui.txtYcom.setText(str(round((self.XY_MAX_PIEZO + self.XY_MIN_PIEZO) / 2, 3)))
        elif self.ui.rbGalvo.isChecked():
            self.ui.txtXcom.setText(str(round((self.XY_MAX_GALVO + self.XY_MIN_GALVO) / 2, 3)))
            self.ui.txtYcom.setText(str(round((self.XY_MAX_GALVO + self.XY_MIN_GALVO) / 2, 3)))
        self.ui.txtZcom.setText(str(round((self.Z_MAX_PIEZO + self.Z_MIN_PIEZO) / 2, 3)))
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
            self.gmThread.command = self.cursorPosition
            self.gmThread.start()

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
    def change_count_rate(self, s):
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

        if self.ui.rbGalvo.isChecked():
            self.gmaxThread.step_xy = round(float(self.ui.txtStepXY.text()), 3)
            self.gmaxThread.step_z = round(float(self.ui.txtStep.text()), 3)
            self.gmaxThread.start()
        elif self.ui.rbPiezo.isChecked():
            self.maxThread.step_xy = round(float(self.ui.txtStepXY.text()), 3)
            self.maxThread.step_z = round(float(self.ui.txtStep.text()), 3)
            self.maxThread.start()

    # Plot Group
    @QtCore.pyqtSlot()
    def save_plot_to_cache(self):
        # save temp data to galvo file
        if self.ui.rbPiezo.isChecked():
            with open(self.scanning_cache["galvo_plot"].name, 'wb') as f:
                pickle.dump(self.map, f)
                pickle.dump(self.mapZ, f)
            with open(self.scanning_cache["galvo_raw"].name, 'wb') as f:
                if hasattr(self, "actualData"):
                    pickle.dump(self.actualData, f)
                else:
                    pickle.dump(0, f)  # set raw_data to 0 for later check when loading
                if hasattr(self, "actualData"):
                    pickle.dump(self.actualData_z, f)
                else:
                    pickle.dump(0, f)  # set raw_data to 0 for later check when loading
        # save temp data to piezo file
        elif self.ui.rbGalvo.isChecked():
            with open(self.scanning_cache["piezo_plot"].name, 'wb') as f:
                pickle.dump(self.map, f)
                pickle.dump(self.mapZ, f)
            with open(self.scanning_cache["piezo_raw"].name, 'wb') as f:
                if hasattr(self, "actualData"):
                    pickle.dump(self.actualData, f)
                else:
                    pickle.dump(0, f)  # set raw_data to 0 for later check when loading
                if hasattr(self, "actualData"):
                    pickle.dump(self.actualData_z, f)
                else:
                    pickle.dump(0, f)  # set raw_data to 0 for later check when loading

    @QtCore.pyqtSlot()
    def load_plots_from_cache(self):
        if self.ui.rbPiezo.isChecked():
            with open(self.scanning_cache["piezo_plot"].name, 'rb') as f:
                try:
                    self.map = pickle.load(f)
                    self.mapZ = pickle.load(f)
                except EOFError:
                    self.init_xy_dummy_data()
                    self.init_z_dummy_data()
                else:
                    with open(self.scanning_cache["piezo_raw"].name, 'rb') as f:
                        self.actualData = pickle.load(f)
                        self.actualData_z = pickle.load(f)
                    if self.actualData == 0:
                        del self.actualData
                    if self.actualData_z == 0:
                        del self.actualData_z
        elif self.ui.rbGalvo.isChecked():
            with open(self.scanning_cache["galvo_plot"].name, 'rb') as f:
                try:
                    self.map = pickle.load(f)
                    self.mapZ = pickle.load(f)
                except EOFError:
                    self.init_xy_dummy_data()
                    self.init_z_dummy_data()
                else:
                    with open(self.scanning_cache["galvo_raw"].name, 'rb') as f:
                        self.actualData = pickle.load(f)
                        self.actualData_z = pickle.load(f)
                    if self.actualData == 0:
                        del self.actualData
                    if self.actualData_z == 0:
                        del self.actualData_z

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
                                                  extent=[float(self.ui.txtStartX.text()),
                                                          float(self.ui.txtEndX.text()),
                                                          float(self.ui.txtStartZ.text()),
                                                          float(self.ui.txtEndZ.text())],
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
        current_path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_file = os.path.join(os.path.dirname(os.path.dirname(current_path)), config_path)
        self.config_confocal = load_config(config_path=CONFIG_file)
        self.update_ui_based_on_default()

    @QtCore.pyqtSlot()
    def save_defaults(self, config_path='config/config_confocal.yaml'):
        self.update_default_based_on_ui()
        current_path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_file = os.path.join(os.path.dirname(os.path.dirname(current_path)), config_path)
        save_config(config=self.config_confocal, config_path=CONFIG_file)

    def update_ui_based_on_default(self):
        if self.config_confocal['scanner'] == 'piezo':
            self.ui.rbPiezo.setChecked(True)
            self.ui.txtStartX.setText(str(self.config_confocal['piezo_scan']['x']['start']))
            self.ui.txtStartY.setText(str(self.config_confocal['piezo_scan']['y']['start']))
            self.ui.txtStartZ.setText(str(self.config_confocal['piezo_scan']['z']['start']))
            self.ui.txtEndX.setText(str(self.config_confocal['piezo_scan']['x']['end']))
            self.ui.txtEndY.setText(str(self.config_confocal['piezo_scan']['y']['end']))
            self.ui.txtEndZ.setText(str(self.config_confocal['piezo_scan']['z']['end']))
            self.ui.txtStepX.setText(str(self.config_confocal['piezo_scan']['x']['step']))
            self.ui.txtStepY.setText(str(self.config_confocal['piezo_scan']['y']['step']))
            self.ui.txtStepZ.setText(str(self.config_confocal['piezo_scan']['z']['step']))
            self.ui.txtRange.setText(str(self.config_confocal['piezo_scan']['range']))
            self.ui.txtXcom.setText(str(self.config_confocal['piezo_scan']['cursor']['x']))
            self.ui.txtYcom.setText(str(self.config_confocal['piezo_scan']['cursor']['y']))
            self.ui.txtZcom.setText(str(self.config_confocal['piezo_scan']['cursor']['z']))
            self.ui.txtStepXY.setText(str(self.config_confocal['move']['piezo_xy_step']))
            self.ui.cbFreq.setEnabled(False)
        elif self.config_confocal['scanner'] == 'galvo':
            self.ui.rbGalvo.setChecked(True)
            self.ui.txtStartX.setText(str(self.config_confocal['galvo_scan']['x']['start']))
            self.ui.txtStartY.setText(str(self.config_confocal['galvo_scan']['y']['start']))
            self.ui.txtStartZ.setText(str(self.config_confocal['galvo_scan']['z']['start']))
            self.ui.txtEndX.setText(str(self.config_confocal['galvo_scan']['x']['end']))
            self.ui.txtEndY.setText(str(self.config_confocal['galvo_scan']['y']['end']))
            self.ui.txtEndZ.setText(str(self.config_confocal['galvo_scan']['z']['end']))
            self.ui.txtStepX.setText(str(self.config_confocal['galvo_scan']['x']['step']))
            self.ui.txtStepY.setText(str(self.config_confocal['galvo_scan']['y']['step']))
            self.ui.txtStepZ.setText(str(self.config_confocal['galvo_scan']['z']['step']))
            self.ui.txtRange.setText(str(self.config_confocal['galvo_scan']['range']))
            self.ui.txtXcom.setText(str(self.config_confocal['galvo_scan']['cursor']['x']))
            self.ui.txtYcom.setText(str(self.config_confocal['galvo_scan']['cursor']['y']))
            self.ui.txtZcom.setText(str(self.config_confocal['galvo_scan']['cursor']['z']))
            self.ui.txtStepXY.setText(str(self.config_confocal['move']['galvo_xy_step']))
            self.ui.cbFreq.setEnabled(True)
            self.ui.cbFreq.setCurrentIndex(int(self.config_confocal['galvo_scan']['line_frequency_index']))
        self.ui.txtStep.setText(str(self.config_confocal['move']['z_step']))
        self.ui.txtRangeZ.setText(str(self.config_confocal['z_scan_range']))

    def update_default_based_on_ui(self):
        if self.config_confocal['scanner'] == 'piezo':
            self.config_confocal['piezo_scan']['x']['start'] = float(self.ui.txtStartX.text())
            self.config_confocal['piezo_scan']['y']['start'] = float(self.ui.txtStartY.text())
            self.config_confocal['piezo_scan']['z']['start'] = float(self.ui.txtStartZ.text())
            self.config_confocal['piezo_scan']['x']['end'] = float(self.ui.txtEndX.text())
            self.config_confocal['piezo_scan']['y']['end'] = float(self.ui.txtEndY.text())
            self.config_confocal['piezo_scan']['z']['end'] = float(self.ui.txtEndZ.text())
            self.config_confocal['piezo_scan']['x']['step'] = float(self.ui.txtStepX.text())
            self.config_confocal['piezo_scan']['y']['step'] = float(self.ui.txtStepY.text())
            self.config_confocal['piezo_scan']['z']['step'] = float(self.ui.txtStepZ.text())
            self.config_confocal['piezo_scan']['range'] = float(self.ui.txtRange.text())
            self.config_confocal['piezo_scan']['cursor']['x'] = float(self.ui.txtXcom.text())
            self.config_confocal['piezo_scan']['cursor']['y'] = float(self.ui.txtYcom.text())
            self.config_confocal['piezo_scan']['cursor']['z'] = float(self.ui.txtZcom.text())
            self.config_confocal['move']['piezo_xy_step'] = float(self.ui.txtStepXY.text())
        elif self.config_confocal['scanner'] == 'galvo':
            self.config_confocal['galvo_scan']['x']['start'] = float(self.ui.txtStartX.text())
            self.config_confocal['galvo_scan']['y']['start'] = float(self.ui.txtStartY.text())
            self.config_confocal['galvo_scan']['z']['start'] = float(self.ui.txtStartZ.text())
            self.config_confocal['galvo_scan']['x']['end'] = float(self.ui.txtEndX.text())
            self.config_confocal['galvo_scan']['y']['end'] = float(self.ui.txtEndY.text())
            self.config_confocal['galvo_scan']['z']['end'] = float(self.ui.txtEndZ.text())
            self.config_confocal['galvo_scan']['x']['step'] = float(self.ui.txtStepX.text())
            self.config_confocal['galvo_scan']['y']['step'] = float(self.ui.txtStepY.text())
            self.config_confocal['galvo_scan']['z']['step'] = float(self.ui.txtStepZ.text())
            self.config_confocal['galvo_scan']['range'] = float(self.ui.txtRange.text())
            self.config_confocal['galvo_scan']['cursor']['x'] = float(self.ui.txtXcom.text())
            self.config_confocal['galvo_scan']['cursor']['y'] = float(self.ui.txtYcom.text())
            self.config_confocal['galvo_scan']['cursor']['z'] = float(self.ui.txtZcom.text())
            self.config_confocal['move']['galvo_xy_step'] = float(self.ui.txtStepXY.text())
            self.config_confocal['galvo_scan']['line_frequency_index'] = int(self.ui.cbFreq.currentIndex())
            self.config_confocal['galvo_scan']['line_frequency_value'] = float(self.ui.cbFreq.currentText())
        self.config_confocal['move']['z_step'] = float(self.ui.txtStep.text())
        self.config_confocal['z_scan_range'] = float(self.ui.txtRangeZ.text())

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
        self.update_current_position()
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
        self.update_current_position()
        try:
            self.actualData_z = self.dThread.raw
        except:
            return

    # dThread
    # Run when signal 'update' emit
    @QtCore.pyqtSlot(numpy.ndarray)
    def update_image_data(self, map_array: numpy.ndarray):
        self.ui.statusbar.showMessage('updating...' + str(time.perf_counter()))
        print('updating...', time.perf_counter())
        self.map = map_array
        self.update_image()

    def update_image(self) -> None:
        """
        Update image basing on self.map data
        :return: None
        """
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
    def update_image_data_ZScan(self, map_array: numpy.ndarray):
        self.ui.statusbar.showMessage('updating...' + str(time.perf_counter()))
        print('updating...', time.perf_counter())
        self.mapZ = map_array

    def update_image_ZScan(self) -> None:
        """
        Update image basing on self.mapZ data
        :return: None
        """
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

    @QtCore.pyqtSlot()
    def scanner_changed(self):
        self.update_default_based_on_ui()
        if self.ui.rbGalvo.isChecked():
            self.config_confocal['scanner'] = 'galvo'
        elif self.ui.rbPiezo.isChecked():
            self.config_confocal['scanner'] = 'piezo'
        self.update_ui_based_on_default()  # update settings parameter based on scanning mode
        self.update_current_position()  # update current position of the scanner
        self.save_plot_to_cache()  # save demostrate plot and raw data to cache
        self.load_plots_from_cache()  # load saved plot and raw data from cache
        self.update_image()
        self.update_image_ZScan()

    # clean cache
    def periodic_clear_cache(self, days=1):
        del self.scanning_cache
        # define time tag
        now = time.time()
        # define expire  limit
        expiration_time = days * 86400
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path) and now - os.path.getmtime(file_path) > expiration_time:
                os.remove(file_path)  # 删除过期文件

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        quit_msg = "Save parameters as Defaults?"
        reply = QtWidgets.QMessageBox.question(self, 'Message', quit_msg, QtWidgets.QMessageBox.Save |
                                               QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
        if reply == QtWidgets.QMessageBox.Save:
            self.save_defaults()
            self.ExpConfocalClose.emit()
            self.periodic_clear_cache(days=self.CACHE_LIFE)
            event.accept()
        elif reply == QtWidgets.QMessageBox.Discard:
            self.ExpConfocalClose.emit()
            self.periodic_clear_cache(days=self.CACHE_LIFE)
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
