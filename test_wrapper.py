'''
Confocal Microscope Program
Created on 2020-04-07
'''

import sys
import os.path
import time
import numpy
from GUI.GUI import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from matplotlib import cm
from collections import deque

from Threads import CountThread, MoveThread, ConfocalScanThread, MaxThread, DataThread
from Hardware import AllHardware


class mainGUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

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

        # Counts plot matplotlib widget
        fig = Figure()
        self.ui.mplPlot = FigureCanvas(fig)
        self.ui.mplPlot.setParent(self.ui.wMpl2)
        self.ui.mplPlot.axes = fig.add_subplot(111)
        self.ui.mplPlot.setGeometry(QtCore.QRect(QtCore.QPoint(0, 0), self.ui.wMpl2.size()))

        # Load defaults
        self.load_defaults()

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

        # Initialize Cursor Lines
        self.cursor = None
        self.curh = self.ui.mplMap.axes.axhline(color='red', linewidth=1, visible=False)
        self.curh.set_ydata((float(self.ui.txtYcom.text()), float(self.ui.txtYcom.text())))
        self.curv = self.ui.mplMap.axes.axvline(color='red', linewidth=1, visible=False)
        self.curv.set_xdata((float(self.ui.txtXcom.text()), float(self.ui.txtXcom.text())))

        # Initialize Dummy Counts Data
        self.countsX = deque(numpy.arange(10).tolist())
        self.countsY = deque(numpy.zeros(10, dtype=int).tolist())

        # Initialize counts plot
        self.countPlot, = self.ui.mplPlot.axes.plot(self.countsX, self.countsY)
        self.ui.mplPlot.axes.set_xlabel('time (s)')
        self.ui.mplPlot.figure.subplots_adjust(top=0.95, bottom=0.3, right=0.99)

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
        # Plot Group
        self.ui.pbSaveData.clicked.connect(self.save_data)
        self.ui.pbReplot.clicked.connect(self.replot_image)
        self.ui.vsMax.sliderMoved.connect(self.modify_image)
        self.ui.vsMin.sliderMoved.connect(self.modify_image)
        # Load and Save defaults
        self.ui.actionOpen_Defaults.triggered.connect(self.open_defaults)
        self.ui.actionSave_Defaults.triggered.connect(self.save_defaults)

    # Methods

    def load_defaults(self, fName='defaults.txt'):
        if fName == 'defaults.txt':
            f = open(os.path.join(os.path.dirname(__file__), fName), 'r')
        else:
            f = open(fName, 'r')
        d = {}
        for line in f.readlines():
            if line[-1] == '\n':
                line = line[:-1]
            [key, value] = line.split('=')
            d[key] = value
        f.close()
        dic = {'STARTX': self.ui.txtStartX,
               'STARTY': self.ui.txtStartY,
               'ENDX': self.ui.txtEndX,
               'ENDY': self.ui.txtEndY,
               'STEPX': self.ui.txtStepX,
               'STEPY': self.ui.txtStepY,
               'ZVAL': self.ui.txtZcom,
               'STEPZ': self.ui.txtStepZ,
               'CURSORX': self.ui.txtXcom,
               'CURSORY': self.ui.txtYcom,
               'RANGE': self.ui.txtRange
               }
        for key, value in d.items():
            dic.get(key).setText(value)

    @QtCore.pyqtSlot()
    def open_defaults(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        location, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose Defaults File', directory)
        self.load_defaults(location)

    @QtCore.pyqtSlot()
    def save_defaults(self, fName='defaults.txt'):
        pairList = []
        pairList.append(("STARTX", self.ui.txtStartX.text()))
        pairList.append(("STARTY", self.ui.txtStartY.text()))
        pairList.append(("ENDX", self.ui.txtEndX.text()))
        pairList.append(("ENDY", self.ui.txtEndY.text()))
        pairList.append(("STEPX", self.ui.txtStepX.text()))
        pairList.append(("STEPY", self.ui.txtStepY.text()))
        pairList.append(("ZVAL", self.ui.txtZcom.text()))
        pairList.append(("STEPZ", self.ui.txtStepZ.text()))
        pairList.append(("CURSORX", self.ui.txtXcom.text()))
        pairList.append(("CURSORY", self.ui.txtYcom.text()))
        pairList.append(("RANGE", self.ui.txtRange.text()))
        ofile = open(os.path.join(os.path.dirname(__file__), fName), 'w')
        for pair in pairList:
            ofile.write(pair[0] + "=" + pair[1] + "\n")
        ofile.close()

    @QtCore.pyqtSlot()
    def show_cursor(self):
        if self.cursor:
            self.cursor.disconnect_events()
            self.cursor = None
        self.curh.set_visible(True)
        self.curh.set_ydata((float(self.ui.txtYcom.text()), float(self.ui.txtYcom.text())))
        self.curv.set_visible(True)
        self.curv.set_xdata((float(self.ui.txtXcom.text()), float(self.ui.txtXcom.text())))
        self.ui.mplMap.draw()
        self.ui.pbShowCursor.setEnabled(False)
        self.ui.pbHideCursor.setEnabled(True)

    @QtCore.pyqtSlot()
    def hide_cursor(self):
        self.cur_vis = False
        self.curh.set_visible(False)
        self.curv.set_visible(False)
        self.ui.mplMap.draw()
        self.ui.pbShowCursor.setEnabled(True)
        self.ui.pbHideCursor.setEnabled(False)

    @QtCore.pyqtSlot()
    def new_cursor(self):
        self.hide_cursor()
        self.cursor = Cursor(self.ui.mplMap.axes, useblit=True, color='red', linewidth=1)
        self.cursor.connect_event('button_press_event', self.new_cursor_marked)
        self.ui.mplMap.draw()

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
    def init_hardware(self):
        self.ui.statusbar.showMessage('Initializing Hardware...')
        # Initialize...
        try:
            self.hardware = AllHardware()
            self.hardware.mover.connect()
            # Takes time...
            # Done!
            self.initPosition()

            # Initialize thread (Need to initialize hardware first!!)
            self.cThread = CountThread(self.hardware)
            self.cThread.counts.connect(self.update_counts)
            self.cThread.finished.connect(self.count_stopped)

            self.mThread = MoveThread(self.hardware)
            self.mThread.moved.connect(self.gone_to)

            self.sThread = ConfocalScanThread(self.hardware)
            self.sThread.update.connect(self.scan_data_back)
            self.sThread.finished.connect(self.scan_stopped)

            self.maxThread = MaxThread(self.hardware)
            self.maxThread.counts.connect(self.update_counts)
            self.maxThread.moved.connect(self.gone_to)

            self.dThread = DataThread()
            self.dThread.update.connect(self.update_image)
        except BaseException as e:
            print(e)
            self.ui.statusbar.showMessage('Hardware Initialization Failed.')
            return
        self.ui.pbCount.setEnabled(True)
        self.ui.cbCountFreq.setEnabled(True)
        self.ui.pbGoTo.setEnabled(True)
        self.ui.pbGoToMid.setEnabled(True)
        self.ui.pbLaserOn.setEnabled(True)
        self.ui.pbLaserOff.setEnabled(True)
        self.ui.pbMax.setEnabled(True)
        self.ui.pbKeepNV.setEnabled(True)
        self.ui.pbStart.setEnabled(True)
        self.ui.pbXleft.setEnabled(True)
        self.ui.pbXright.setEnabled(True)
        self.ui.pbYdown.setEnabled(True)
        self.ui.pbYup.setEnabled(True)
        self.ui.pbZdown.setEnabled(True)
        self.ui.pbZup.setEnabled(True)
        self.ui.pbInitHW.setEnabled(False)
        self.ui.pbCleanupHW.setEnabled(True)
        self.ui.statusbar.showMessage('Hardware Initialized Successfully.')

        self.stepMoveDic = {'x+': lambda: self.ui.txtXcom.setText(
            str(round(float(self.ui.txtXcom.text()) + float(self.ui.txtStepX.text()), 3))),
                            'x-': lambda: self.ui.txtXcom.setText(
                                str(round(float(self.ui.txtXcom.text()) - float(self.ui.txtStepX.text()), 3))),
                            'y+': lambda: self.ui.txtYcom.setText(
                                str(round(float(self.ui.txtYcom.text()) + float(self.ui.txtStepY.text()), 3))),
                            'y-': lambda: self.ui.txtYcom.setText(
                                str(round(float(self.ui.txtYcom.text()) - float(self.ui.txtStepY.text()), 3))),
                            'z+': lambda: self.ui.txtZcom.setText(
                                str(round(float(self.ui.txtZcom.text()) + float(self.ui.txtStepZ.text()), 3))),
                            'z-': lambda: self.ui.txtZcom.setText(
                                str(round(float(self.ui.txtZcom.text()) - float(self.ui.txtStepZ.text()), 3)))}

    def initPosition(self):
        x, y, z = self.hardware.mover.read_pos('1'), self.hardware.mover.read_pos('2'), self.hardware.mover.read_pos(
            '3')
        self.ui.txtX.setText(str(round(x, 3)))
        self.ui.txtY.setText(str(round(y, 3)))
        self.ui.txtZ.setText(str(round(z, 3)))
        self.ui.pbGetPos.setEnabled(True)

    @QtCore.pyqtSlot()
    def cleanup_hardware(self):
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
        self.ui.pbStop.setEnabled(False)
        self.ui.pbXleft.setEnabled(False)
        self.ui.pbXright.setEnabled(False)
        self.ui.pbYdown.setEnabled(False)
        self.ui.pbYup.setEnabled(False)
        self.ui.pbZdown.setEnabled(False)
        self.ui.pbZup.setEnabled(False)

        self.hardware.cleanup()
        if True:
            self.ui.statusbar.showMessage('Hardware Reset Successfully.')
            self.hardware = None
        else:
            self.ui.statusbar.showMessage('Hardware Reset Failed.')
        self.ui.pbInitHW.setEnabled(True)
        self.ui.pbCleanupHW.setEnabled(False)

    @QtCore.pyqtSlot()
    def laser_on(self):
        pass

    @QtCore.pyqtSlot()
    def laser_off(self):
        pass

    @QtCore.pyqtSlot()
    def set_full_range(self):
        self.ui.txtStartX.setText('0')
        self.ui.txtEndX.setText('200')
        self.ui.txtStepX.setText('2')
        self.ui.txtStartY.setText('0')
        self.ui.txtEndY.setText('200')
        self.ui.txtStepY.setText('2')

    @QtCore.pyqtSlot()
    def set_center_range(self):
        xval = round(float(self.ui.txtXcom.text()), 1)
        yval = round(float(self.ui.txtYcom.text()), 1)
        d = float(self.ui.txtRange.text())
        self.ui.txtStartX.setText(str(xval - d / 2))
        self.ui.txtStartY.setText(str(yval - d / 2))
        self.ui.txtEndX.setText(str(xval + d / 2))
        self.ui.txtEndY.setText(str(yval + d / 2))
        self.ui.txtStepX.setText(str(d / 100))
        self.ui.txtStepY.setText(str(d / 100))

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
        self.ui.pbFullRange.setEnabled(False)
        self.ui.pbSelectRange.setEnabled(False)
        self.ui.pbCount.setEnabled(False)
        self.ui.txtStartX.setEnabled(False)
        self.ui.txtEndX.setEnabled(False)
        self.ui.txtStepX.setEnabled(False)
        self.ui.txtStartY.setEnabled(False)
        self.ui.txtEndY.setEnabled(False)
        self.ui.txtStepY.setEnabled(False)

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
        self.sThread.start()

    @QtCore.pyqtSlot(float, list, list)
    def scan_data_back(self, y, posData, countsData):
        self.dThread.y = y
        self.dThread.xData = posData
        self.dThread.countsData = countsData
        self.dThread.start()

    @QtCore.pyqtSlot(numpy.ndarray)
    def update_image(self, map_array):
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

    @QtCore.pyqtSlot()
    def scan_stop(self):
        self.ui.statusbar.showMessage('Scan stopping...')
        self.ui.pbStop.setEnabled(False)
        # Stop the process
        self.sThread.running = False

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
        self.ui.pbStop.setEnabled(False)
        self.ui.pbFullRange.setEnabled(True)
        self.ui.pbSelectRange.setEnabled(True)
        self.ui.pbCount.setEnabled(True)
        self.ui.txtStartX.setEnabled(True)
        self.ui.txtEndX.setEnabled(True)
        self.ui.txtStepX.setEnabled(True)
        self.ui.txtStartY.setEnabled(True)
        self.ui.txtEndY.setEnabled(True)
        self.ui.txtStepY.setEnabled(True)

    @QtCore.pyqtSlot()
    def modify_image(self):
        val_max = self.ui.vsMax.value()
        val_min = self.ui.vsMin.value()
        vmax = self.map.max() * (10 ** ((val_max + 1) / 20)) / 1000
        vmin = min(self.map.mean(), vmax) * val_min / 100

        self.image.set_clim(vmin, vmax)
        self.ui.mplMap.draw()

    @QtCore.pyqtSlot()
    def replot_image(self):

        self.ui.mplMap.figure.clear()
        self.ui.mplMap.axes = self.ui.mplMap.figure.add_subplot(111)
        self.image = self.ui.mplMap.axes.imshow(self.map, cmap=cm.get_cmap(self.mapColor), vmin=0, vmax=self.map.max(),
                                                extent=[float(self.ui.txtStartX.text()), float(self.ui.txtEndX.text()),
                                                        float(self.ui.txtStartY.text()), float(self.ui.txtEndY.text())],
                                                interpolation='nearest',
                                                origin='lower')  # See https://matplotlib.org/gallery/images_contours_and_fields/interpolation_methods.html for interpolation
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
    def save_data(self):
        try:
            self.actualData = self.dThread.raw
        except:
            sys.stderr.write('No data to be saved!\n')
            return

        directory = QtWidgets.QFileDialog.getSaveFileName(self, 'Enter save file', "", "Text (*.txt)")
        directory = str(directory[0].replace('/', '\\'))
        if directory != '':
            f = open(directory, 'w')
            for each_datapoint in self.actualData:
                f.write(str(each_datapoint[0]) + '\t' + str(each_datapoint[1]) + '\t' + str(each_datapoint[2]) + '\n')
            f.close()
        else:
            sys.stderr.write('No file selected\n')

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

    @QtCore.pyqtSlot()
    def count_stopped(self):
        self.ui.statusbar.clearMessage()
        self.ui.pbMax.setEnabled(True)
        self.ui.pbKeepNV.setEnabled(True)
        self.ui.pbStart.setEnabled(True)
        self.ui.pbCount.setText('On')
        self.ui.pbCount.clicked.disconnect()
        self.ui.pbCount.clicked.connect(self.count_start)

    @QtCore.pyqtSlot(str)
    def change_rate(self, s):
        new_rate = eval(s)
        self.cThread.count_rate = new_rate
        self.cThread.count_rate_changed = True

    @property
    def cursorPosition(self):
        return [float(self.ui.txtXcom.text()), float(self.ui.txtYcom.text()), float(self.ui.txtZcom.text())]

    @QtCore.pyqtSlot()
    def mark_current_position(self):
        self.ui.txtXcom.setText(self.ui.txtX.text())
        self.ui.txtYcom.setText(self.ui.txtY.text())
        self.ui.txtZcom.setText(self.ui.txtZ.text())

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
        self.mThread.command = self.cursorPosition

        self.mThread.start()

    @QtCore.pyqtSlot()
    def go_to_mid(self):
        self.ui.txtXcom.setText('100')
        self.ui.txtYcom.setText('100')
        self.ui.txtZcom.setText('100')
        self.go_to()

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
        self.maxThread.start()

    @QtCore.pyqtSlot(QtCore.QEvent)
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Message', quit_msg, QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.cleanup_hardware()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myWindow = mainGUI()
    myWindow.show()
    sys.exit(app.exec_())
