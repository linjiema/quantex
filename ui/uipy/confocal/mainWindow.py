# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\pbblab\PycharmProjects\afm-confocal\ui\ui_files\confocal\mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Confocal(object):
    def setupUi(self, Confocal):
        Confocal.setObjectName("Confocal")
        Confocal.resize(1117, 772)
        self.centralwidget = QtWidgets.QWidget(Confocal)
        self.centralwidget.setObjectName("centralwidget")
        self.gbHardware = QtWidgets.QGroupBox(self.centralwidget)
        self.gbHardware.setGeometry(QtCore.QRect(560, 300, 171, 51))
        self.gbHardware.setObjectName("gbHardware")
        self.pbInitHW = QtWidgets.QPushButton(self.gbHardware)
        self.pbInitHW.setGeometry(QtCore.QRect(10, 20, 71, 23))
        self.pbInitHW.setObjectName("pbInitHW")
        self.pbCleanupHW = QtWidgets.QPushButton(self.gbHardware)
        self.pbCleanupHW.setEnabled(False)
        self.pbCleanupHW.setGeometry(QtCore.QRect(90, 20, 71, 23))
        self.pbCleanupHW.setObjectName("pbCleanupHW")
        self.gbCounts = QtWidgets.QGroupBox(self.centralwidget)
        self.gbCounts.setGeometry(QtCore.QRect(580, 410, 521, 301))
        self.gbCounts.setObjectName("gbCounts")
        self.pbCount = QtWidgets.QPushButton(self.gbCounts)
        self.pbCount.setEnabled(False)
        self.pbCount.setGeometry(QtCore.QRect(260, 40, 61, 23))
        self.pbCount.setObjectName("pbCount")
        self.pbMax = QtWidgets.QPushButton(self.gbCounts)
        self.pbMax.setEnabled(False)
        self.pbMax.setGeometry(QtCore.QRect(330, 40, 61, 23))
        self.pbMax.setObjectName("pbMax")
        self.cbCountFreq = QtWidgets.QComboBox(self.gbCounts)
        self.cbCountFreq.setEnabled(False)
        self.cbCountFreq.setGeometry(QtCore.QRect(400, 40, 73, 22))
        self.cbCountFreq.setObjectName("cbCountFreq")
        self.cbCountFreq.addItem("")
        self.cbCountFreq.addItem("")
        self.cbCountFreq.addItem("")
        self.cbCountFreq.addItem("")
        self.label_15 = QtWidgets.QLabel(self.gbCounts)
        self.label_15.setGeometry(QtCore.QRect(480, 40, 31, 21))
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.lcdNumber = QtWidgets.QLCDNumber(self.gbCounts)
        self.lcdNumber.setGeometry(QtCore.QRect(10, 20, 241, 61))
        self.lcdNumber.setDigitCount(8)
        self.lcdNumber.setObjectName("lcdNumber")
        self.wMplCounts = QtWidgets.QWidget(self.gbCounts)
        self.wMplCounts.setGeometry(QtCore.QRect(10, 90, 501, 191))
        self.wMplCounts.setObjectName("wMplCounts")
        self.gbCursorControl = QtWidgets.QGroupBox(self.centralwidget)
        self.gbCursorControl.setGeometry(QtCore.QRect(10, 600, 281, 51))
        self.gbCursorControl.setObjectName("gbCursorControl")
        self.pbNewCursor = QtWidgets.QPushButton(self.gbCursorControl)
        self.pbNewCursor.setEnabled(True)
        self.pbNewCursor.setGeometry(QtCore.QRect(10, 20, 81, 23))
        self.pbNewCursor.setObjectName("pbNewCursor")
        self.pbShowCursor = QtWidgets.QPushButton(self.gbCursorControl)
        self.pbShowCursor.setEnabled(True)
        self.pbShowCursor.setGeometry(QtCore.QRect(100, 20, 81, 23))
        self.pbShowCursor.setObjectName("pbShowCursor")
        self.pbHideCursor = QtWidgets.QPushButton(self.gbCursorControl)
        self.pbHideCursor.setEnabled(False)
        self.pbHideCursor.setGeometry(QtCore.QRect(190, 20, 81, 23))
        self.pbHideCursor.setObjectName("pbHideCursor")
        self.gbLaser = QtWidgets.QGroupBox(self.centralwidget)
        self.gbLaser.setGeometry(QtCore.QRect(560, 360, 171, 51))
        self.gbLaser.setObjectName("gbLaser")
        self.pbLaserOn = QtWidgets.QPushButton(self.gbLaser)
        self.pbLaserOn.setEnabled(False)
        self.pbLaserOn.setGeometry(QtCore.QRect(10, 20, 71, 23))
        self.pbLaserOn.setObjectName("pbLaserOn")
        self.pbLaserOff = QtWidgets.QPushButton(self.gbLaser)
        self.pbLaserOff.setEnabled(False)
        self.pbLaserOff.setGeometry(QtCore.QRect(90, 20, 71, 23))
        self.pbLaserOff.setObjectName("pbLaserOff")
        self.gbMove = QtWidgets.QGroupBox(self.centralwidget)
        self.gbMove.setGeometry(QtCore.QRect(740, 300, 361, 111))
        self.gbMove.setObjectName("gbMove")
        self.gbMoveXY = QtWidgets.QGroupBox(self.gbMove)
        self.gbMoveXY.setGeometry(QtCore.QRect(10, 20, 161, 81))
        self.gbMoveXY.setObjectName("gbMoveXY")
        self.pbYup = QtWidgets.QPushButton(self.gbMoveXY)
        self.pbYup.setEnabled(False)
        self.pbYup.setGeometry(QtCore.QRect(60, 10, 41, 23))
        self.pbYup.setObjectName("pbYup")
        self.pbYdown = QtWidgets.QPushButton(self.gbMoveXY)
        self.pbYdown.setEnabled(False)
        self.pbYdown.setGeometry(QtCore.QRect(60, 50, 41, 23))
        self.pbYdown.setObjectName("pbYdown")
        self.pbXright = QtWidgets.QPushButton(self.gbMoveXY)
        self.pbXright.setEnabled(False)
        self.pbXright.setGeometry(QtCore.QRect(110, 30, 41, 23))
        self.pbXright.setObjectName("pbXright")
        self.pbXleft = QtWidgets.QPushButton(self.gbMoveXY)
        self.pbXleft.setEnabled(False)
        self.pbXleft.setGeometry(QtCore.QRect(10, 30, 41, 23))
        self.pbXleft.setObjectName("pbXleft")
        self.gbMoveZ = QtWidgets.QGroupBox(self.gbMove)
        self.gbMoveZ.setGeometry(QtCore.QRect(180, 20, 61, 81))
        self.gbMoveZ.setObjectName("gbMoveZ")
        self.pbZup = QtWidgets.QPushButton(self.gbMoveZ)
        self.pbZup.setEnabled(False)
        self.pbZup.setGeometry(QtCore.QRect(10, 20, 41, 23))
        self.pbZup.setObjectName("pbZup")
        self.pbZdown = QtWidgets.QPushButton(self.gbMoveZ)
        self.pbZdown.setEnabled(False)
        self.pbZdown.setGeometry(QtCore.QRect(10, 50, 41, 23))
        self.pbZdown.setObjectName("pbZdown")
        self.pbKeepNV = QtWidgets.QPushButton(self.gbMove)
        self.pbKeepNV.setEnabled(False)
        self.pbKeepNV.setGeometry(QtCore.QRect(260, 70, 81, 31))
        self.pbKeepNV.setObjectName("pbKeepNV")
        self.txtStep = QtWidgets.QLineEdit(self.gbMove)
        self.txtStep.setGeometry(QtCore.QRect(300, 45, 51, 21))
        self.txtStep.setObjectName("txtStep")
        self.label_9 = QtWidgets.QLabel(self.gbMove)
        self.label_9.setGeometry(QtCore.QRect(250, 45, 41, 21))
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.label_22 = QtWidgets.QLabel(self.gbMove)
        self.label_22.setGeometry(QtCore.QRect(250, 15, 41, 21))
        self.label_22.setAlignment(QtCore.Qt.AlignCenter)
        self.label_22.setObjectName("label_22")
        self.txtStepXY = QtWidgets.QLineEdit(self.gbMove)
        self.txtStepXY.setGeometry(QtCore.QRect(300, 15, 51, 21))
        self.txtStepXY.setObjectName("txtStepXY")
        self.gbXYScan = QtWidgets.QGroupBox(self.centralwidget)
        self.gbXYScan.setGeometry(QtCore.QRect(10, 0, 541, 411))
        self.gbXYScan.setObjectName("gbXYScan")
        self.pbSaveData = QtWidgets.QPushButton(self.gbXYScan)
        self.pbSaveData.setGeometry(QtCore.QRect(370, 370, 71, 31))
        self.pbSaveData.setObjectName("pbSaveData")
        self.wMpl = QtWidgets.QWidget(self.gbXYScan)
        self.wMpl.setGeometry(QtCore.QRect(7, 19, 431, 341))
        self.wMpl.setObjectName("wMpl")
        self.label_17 = QtWidgets.QLabel(self.gbXYScan)
        self.label_17.setGeometry(QtCore.QRect(440, 20, 61, 20))
        self.label_17.setAlignment(QtCore.Qt.AlignCenter)
        self.label_17.setObjectName("label_17")
        self.pbReplot = QtWidgets.QPushButton(self.gbXYScan)
        self.pbReplot.setEnabled(True)
        self.pbReplot.setGeometry(QtCore.QRect(450, 370, 81, 31))
        self.pbReplot.setObjectName("pbReplot")
        self.wToolbar = QtWidgets.QWidget(self.gbXYScan)
        self.wToolbar.setGeometry(QtCore.QRect(10, 370, 351, 31))
        self.wToolbar.setObjectName("wToolbar")
        self.vsMax = QtWidgets.QSlider(self.gbXYScan)
        self.vsMax.setGeometry(QtCore.QRect(458, 50, 21, 311))
        self.vsMax.setMinimum(0)
        self.vsMax.setMaximum(59)
        self.vsMax.setProperty("value", 59)
        self.vsMax.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.vsMax.setObjectName("vsMax")
        self.label_18 = QtWidgets.QLabel(self.gbXYScan)
        self.label_18.setGeometry(QtCore.QRect(500, 20, 31, 20))
        self.label_18.setAlignment(QtCore.Qt.AlignCenter)
        self.label_18.setObjectName("label_18")
        self.vsMin = QtWidgets.QSlider(self.gbXYScan)
        self.vsMin.setGeometry(QtCore.QRect(508, 50, 21, 311))
        self.vsMin.setProperty("value", 0)
        self.vsMin.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.vsMin.setObjectName("vsMin")
        self.gbZScan = QtWidgets.QGroupBox(self.centralwidget)
        self.gbZScan.setGeometry(QtCore.QRect(560, 0, 541, 301))
        self.gbZScan.setObjectName("gbZScan")
        self.wMpl_ZScan = QtWidgets.QWidget(self.gbZScan)
        self.wMpl_ZScan.setGeometry(QtCore.QRect(10, 20, 431, 231))
        self.wMpl_ZScan.setObjectName("wMpl_ZScan")
        self.pbReplot_ZScan = QtWidgets.QPushButton(self.gbZScan)
        self.pbReplot_ZScan.setEnabled(True)
        self.pbReplot_ZScan.setGeometry(QtCore.QRect(450, 260, 81, 31))
        self.pbReplot_ZScan.setObjectName("pbReplot_ZScan")
        self.wToolbar_ZScan = QtWidgets.QWidget(self.gbZScan)
        self.wToolbar_ZScan.setGeometry(QtCore.QRect(12, 260, 351, 31))
        self.wToolbar_ZScan.setObjectName("wToolbar_ZScan")
        self.pbSaveData_ZScan = QtWidgets.QPushButton(self.gbZScan)
        self.pbSaveData_ZScan.setGeometry(QtCore.QRect(370, 260, 71, 31))
        self.pbSaveData_ZScan.setObjectName("pbSaveData_ZScan")
        self.vsMax_ZScan = QtWidgets.QSlider(self.gbZScan)
        self.vsMax_ZScan.setGeometry(QtCore.QRect(460, 50, 21, 201))
        self.vsMax_ZScan.setMinimum(0)
        self.vsMax_ZScan.setMaximum(59)
        self.vsMax_ZScan.setProperty("value", 59)
        self.vsMax_ZScan.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.vsMax_ZScan.setObjectName("vsMax_ZScan")
        self.vsMin_ZScan = QtWidgets.QSlider(self.gbZScan)
        self.vsMin_ZScan.setGeometry(QtCore.QRect(510, 50, 21, 201))
        self.vsMin_ZScan.setProperty("value", 0)
        self.vsMin_ZScan.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.vsMin_ZScan.setObjectName("vsMin_ZScan")
        self.label_19 = QtWidgets.QLabel(self.gbZScan)
        self.label_19.setGeometry(QtCore.QRect(440, 20, 61, 20))
        self.label_19.setAlignment(QtCore.Qt.AlignCenter)
        self.label_19.setObjectName("label_19")
        self.label_20 = QtWidgets.QLabel(self.gbZScan)
        self.label_20.setGeometry(QtCore.QRect(500, 20, 31, 20))
        self.label_20.setAlignment(QtCore.Qt.AlignCenter)
        self.label_20.setObjectName("label_20")
        self.gbScan = QtWidgets.QGroupBox(self.centralwidget)
        self.gbScan.setGeometry(QtCore.QRect(170, 410, 401, 191))
        self.gbScan.setObjectName("gbScan")
        self.gbX = QtWidgets.QGroupBox(self.gbScan)
        self.gbX.setGeometry(QtCore.QRect(10, 70, 121, 111))
        self.gbX.setObjectName("gbX")
        self.txtStepX = QtWidgets.QLineEdit(self.gbX)
        self.txtStepX.setGeometry(QtCore.QRect(40, 80, 71, 21))
        self.txtStepX.setObjectName("txtStepX")
        self.label = QtWidgets.QLabel(self.gbX)
        self.label.setGeometry(QtCore.QRect(0, 21, 46, 20))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.txtStartX = QtWidgets.QLineEdit(self.gbX)
        self.txtStartX.setGeometry(QtCore.QRect(40, 20, 71, 21))
        self.txtStartX.setObjectName("txtStartX")
        self.label_4 = QtWidgets.QLabel(self.gbX)
        self.label_4.setGeometry(QtCore.QRect(0, 81, 46, 20))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_3 = QtWidgets.QLabel(self.gbX)
        self.label_3.setGeometry(QtCore.QRect(0, 51, 46, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.txtEndX = QtWidgets.QLineEdit(self.gbX)
        self.txtEndX.setGeometry(QtCore.QRect(40, 50, 71, 21))
        self.txtEndX.setObjectName("txtEndX")
        self.gbY = QtWidgets.QGroupBox(self.gbScan)
        self.gbY.setGeometry(QtCore.QRect(140, 70, 121, 111))
        self.gbY.setObjectName("gbY")
        self.txtStepY = QtWidgets.QLineEdit(self.gbY)
        self.txtStepY.setGeometry(QtCore.QRect(40, 80, 71, 21))
        self.txtStepY.setObjectName("txtStepY")
        self.label_5 = QtWidgets.QLabel(self.gbY)
        self.label_5.setGeometry(QtCore.QRect(0, 21, 46, 20))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.txtStartY = QtWidgets.QLineEdit(self.gbY)
        self.txtStartY.setGeometry(QtCore.QRect(40, 20, 71, 21))
        self.txtStartY.setObjectName("txtStartY")
        self.label_6 = QtWidgets.QLabel(self.gbY)
        self.label_6.setGeometry(QtCore.QRect(0, 81, 46, 20))
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.gbY)
        self.label_7.setGeometry(QtCore.QRect(0, 51, 46, 20))
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.txtEndY = QtWidgets.QLineEdit(self.gbY)
        self.txtEndY.setGeometry(QtCore.QRect(40, 50, 71, 21))
        self.txtEndY.setObjectName("txtEndY")
        self.gbZ_2 = QtWidgets.QGroupBox(self.gbScan)
        self.gbZ_2.setGeometry(QtCore.QRect(270, 70, 121, 111))
        self.gbZ_2.setObjectName("gbZ_2")
        self.txtStepZ = QtWidgets.QLineEdit(self.gbZ_2)
        self.txtStepZ.setGeometry(QtCore.QRect(40, 80, 71, 21))
        self.txtStepZ.setObjectName("txtStepZ")
        self.label_24 = QtWidgets.QLabel(self.gbZ_2)
        self.label_24.setGeometry(QtCore.QRect(0, 21, 46, 20))
        self.label_24.setAlignment(QtCore.Qt.AlignCenter)
        self.label_24.setObjectName("label_24")
        self.txtStartZ = QtWidgets.QLineEdit(self.gbZ_2)
        self.txtStartZ.setGeometry(QtCore.QRect(40, 20, 71, 21))
        self.txtStartZ.setObjectName("txtStartZ")
        self.label_25 = QtWidgets.QLabel(self.gbZ_2)
        self.label_25.setGeometry(QtCore.QRect(0, 81, 46, 20))
        self.label_25.setAlignment(QtCore.Qt.AlignCenter)
        self.label_25.setObjectName("label_25")
        self.label_26 = QtWidgets.QLabel(self.gbZ_2)
        self.label_26.setGeometry(QtCore.QRect(0, 51, 46, 20))
        self.label_26.setAlignment(QtCore.Qt.AlignCenter)
        self.label_26.setObjectName("label_26")
        self.txtEndZ = QtWidgets.QLineEdit(self.gbZ_2)
        self.txtEndZ.setGeometry(QtCore.QRect(40, 50, 71, 21))
        self.txtEndZ.setObjectName("txtEndZ")
        self.gbSpeed = QtWidgets.QGroupBox(self.gbScan)
        self.gbSpeed.setGeometry(QtCore.QRect(160, 20, 231, 51))
        self.gbSpeed.setObjectName("gbSpeed")
        self.label_16 = QtWidgets.QLabel(self.gbSpeed)
        self.label_16.setGeometry(QtCore.QRect(10, 20, 131, 21))
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.cbFreq = QtWidgets.QComboBox(self.gbSpeed)
        self.cbFreq.setGeometry(QtCore.QRect(140, 20, 73, 22))
        self.cbFreq.setObjectName("cbFreq")
        self.cbFreq.addItem("")
        self.cbFreq.addItem("")
        self.cbFreq.addItem("")
        self.cbFreq.addItem("")
        self.cbFreq.addItem("")
        self.cbFreq.addItem("")
        self.cbFreq.addItem("")
        self.cbFreq.addItem("")
        self.gbXYScanner = QtWidgets.QGroupBox(self.gbScan)
        self.gbXYScanner.setGeometry(QtCore.QRect(10, 20, 141, 51))
        self.gbXYScanner.setObjectName("gbXYScanner")
        self.rbGalvo = QtWidgets.QRadioButton(self.gbXYScanner)
        self.rbGalvo.setGeometry(QtCore.QRect(80, 20, 61, 21))
        self.rbGalvo.setObjectName("rbGalvo")
        self.rbPiezo = QtWidgets.QRadioButton(self.gbXYScanner)
        self.rbPiezo.setGeometry(QtCore.QRect(10, 20, 61, 21))
        self.rbPiezo.setObjectName("rbPiezo")
        self.tabScanControl = QtWidgets.QTabWidget(self.centralwidget)
        self.tabScanControl.setGeometry(QtCore.QRect(10, 410, 151, 191))
        self.tabScanControl.setObjectName("tabScanControl")
        self.tabXYScan = QtWidgets.QWidget()
        self.tabXYScan.setObjectName("tabXYScan")
        self.pbStart = QtWidgets.QPushButton(self.tabXYScan)
        self.pbStart.setEnabled(False)
        self.pbStart.setGeometry(QtCore.QRect(0, 130, 71, 25))
        self.pbStart.setObjectName("pbStart")
        self.label_2 = QtWidgets.QLabel(self.tabXYScan)
        self.label_2.setGeometry(QtCore.QRect(10, 100, 53, 21))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.pbStop = QtWidgets.QPushButton(self.tabXYScan)
        self.pbStop.setEnabled(False)
        self.pbStop.setGeometry(QtCore.QRect(70, 130, 71, 25))
        self.pbStop.setObjectName("pbStop")
        self.pbSelectRange = QtWidgets.QPushButton(self.tabXYScan)
        self.pbSelectRange.setEnabled(True)
        self.pbSelectRange.setGeometry(QtCore.QRect(20, 40, 101, 25))
        self.pbSelectRange.setObjectName("pbSelectRange")
        self.pbFullRange = QtWidgets.QPushButton(self.tabXYScan)
        self.pbFullRange.setGeometry(QtCore.QRect(20, 10, 101, 25))
        self.pbFullRange.setObjectName("pbFullRange")
        self.pbCenter = QtWidgets.QPushButton(self.tabXYScan)
        self.pbCenter.setGeometry(QtCore.QRect(20, 70, 101, 25))
        self.pbCenter.setObjectName("pbCenter")
        self.txtRange = QtWidgets.QLineEdit(self.tabXYScan)
        self.txtRange.setGeometry(QtCore.QRect(60, 100, 71, 22))
        self.txtRange.setObjectName("txtRange")
        self.tabScanControl.addTab(self.tabXYScan, "")
        self.tabZScan = QtWidgets.QWidget()
        self.tabZScan.setObjectName("tabZScan")
        self.pbCenterZ = QtWidgets.QPushButton(self.tabZScan)
        self.pbCenterZ.setGeometry(QtCore.QRect(20, 70, 101, 25))
        self.pbCenterZ.setObjectName("pbCenterZ")
        self.pbStartZ = QtWidgets.QPushButton(self.tabZScan)
        self.pbStartZ.setEnabled(False)
        self.pbStartZ.setGeometry(QtCore.QRect(0, 130, 71, 25))
        self.pbStartZ.setObjectName("pbStartZ")
        self.pbSelectRangeZ = QtWidgets.QPushButton(self.tabZScan)
        self.pbSelectRangeZ.setEnabled(True)
        self.pbSelectRangeZ.setGeometry(QtCore.QRect(20, 40, 101, 25))
        self.pbSelectRangeZ.setObjectName("pbSelectRangeZ")
        self.pbFullRangeZ = QtWidgets.QPushButton(self.tabZScan)
        self.pbFullRangeZ.setGeometry(QtCore.QRect(20, 10, 101, 25))
        self.pbFullRangeZ.setObjectName("pbFullRangeZ")
        self.txtRangeZ = QtWidgets.QLineEdit(self.tabZScan)
        self.txtRangeZ.setGeometry(QtCore.QRect(60, 100, 71, 22))
        self.txtRangeZ.setObjectName("txtRangeZ")
        self.label_21 = QtWidgets.QLabel(self.tabZScan)
        self.label_21.setGeometry(QtCore.QRect(10, 100, 53, 21))
        self.label_21.setAlignment(QtCore.Qt.AlignCenter)
        self.label_21.setObjectName("label_21")
        self.pbStopZ = QtWidgets.QPushButton(self.tabZScan)
        self.pbStopZ.setEnabled(False)
        self.pbStopZ.setGeometry(QtCore.QRect(70, 130, 71, 25))
        self.pbStopZ.setObjectName("pbStopZ")
        self.tabScanControl.addTab(self.tabZScan, "")
        self.gbActual = QtWidgets.QGroupBox(self.centralwidget)
        self.gbActual.setGeometry(QtCore.QRect(10, 660, 251, 51))
        self.gbActual.setObjectName("gbActual")
        self.label_11 = QtWidgets.QLabel(self.gbActual)
        self.label_11.setGeometry(QtCore.QRect(0, 20, 21, 21))
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.txtX = QtWidgets.QLineEdit(self.gbActual)
        self.txtX.setEnabled(False)
        self.txtX.setGeometry(QtCore.QRect(20, 20, 61, 21))
        self.txtX.setObjectName("txtX")
        self.txtY = QtWidgets.QLineEdit(self.gbActual)
        self.txtY.setEnabled(False)
        self.txtY.setGeometry(QtCore.QRect(100, 20, 61, 21))
        self.txtY.setObjectName("txtY")
        self.label_12 = QtWidgets.QLabel(self.gbActual)
        self.label_12.setGeometry(QtCore.QRect(80, 20, 21, 21))
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.label_14 = QtWidgets.QLabel(self.gbActual)
        self.label_14.setGeometry(QtCore.QRect(160, 20, 21, 21))
        self.label_14.setAlignment(QtCore.Qt.AlignCenter)
        self.label_14.setObjectName("label_14")
        self.txtZ = QtWidgets.QLineEdit(self.gbActual)
        self.txtZ.setEnabled(False)
        self.txtZ.setGeometry(QtCore.QRect(180, 20, 61, 21))
        self.txtZ.setObjectName("txtZ")
        self.gbCursor = QtWidgets.QGroupBox(self.centralwidget)
        self.gbCursor.setGeometry(QtCore.QRect(320, 660, 251, 51))
        self.gbCursor.setObjectName("gbCursor")
        self.label_10 = QtWidgets.QLabel(self.gbCursor)
        self.label_10.setGeometry(QtCore.QRect(0, 20, 21, 21))
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.txtXcom = QtWidgets.QLineEdit(self.gbCursor)
        self.txtXcom.setGeometry(QtCore.QRect(20, 20, 61, 21))
        self.txtXcom.setObjectName("txtXcom")
        self.label_13 = QtWidgets.QLabel(self.gbCursor)
        self.label_13.setGeometry(QtCore.QRect(80, 20, 21, 21))
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.txtYcom = QtWidgets.QLineEdit(self.gbCursor)
        self.txtYcom.setGeometry(QtCore.QRect(100, 20, 61, 21))
        self.txtYcom.setObjectName("txtYcom")
        self.txtZcom = QtWidgets.QLineEdit(self.gbCursor)
        self.txtZcom.setGeometry(QtCore.QRect(180, 20, 61, 21))
        self.txtZcom.setObjectName("txtZcom")
        self.label_8 = QtWidgets.QLabel(self.gbCursor)
        self.label_8.setGeometry(QtCore.QRect(160, 20, 21, 21))
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.pbGetPos = QtWidgets.QPushButton(self.centralwidget)
        self.pbGetPos.setEnabled(False)
        self.pbGetPos.setGeometry(QtCore.QRect(270, 670, 41, 31))
        self.pbGetPos.setObjectName("pbGetPos")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(300, 600, 261, 51))
        self.groupBox.setObjectName("groupBox")
        self.pbGoToMid = QtWidgets.QPushButton(self.groupBox)
        self.pbGoToMid.setEnabled(False)
        self.pbGoToMid.setGeometry(QtCore.QRect(150, 20, 81, 23))
        self.pbGoToMid.setObjectName("pbGoToMid")
        self.pbGoTo = QtWidgets.QPushButton(self.groupBox)
        self.pbGoTo.setEnabled(False)
        self.pbGoTo.setGeometry(QtCore.QRect(30, 20, 81, 23))
        self.pbGoTo.setObjectName("pbGoTo")
        Confocal.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Confocal)
        self.statusbar.setObjectName("statusbar")
        Confocal.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(Confocal)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1117, 22))
        self.menuBar.setObjectName("menuBar")
        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        Confocal.setMenuBar(self.menuBar)
        self.actionOpen = QtWidgets.QAction(Confocal)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave_As = QtWidgets.QAction(Confocal)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionSave_Defaults = QtWidgets.QAction(Confocal)
        self.actionSave_Defaults.setObjectName("actionSave_Defaults")
        self.actionOpen_Defaults = QtWidgets.QAction(Confocal)
        self.actionOpen_Defaults.setObjectName("actionOpen_Defaults")
        self.menuFile.addAction(self.actionOpen_Defaults)
        self.menuFile.addAction(self.actionSave_Defaults)
        self.menuBar.addAction(self.menuFile.menuAction())

        self.retranslateUi(Confocal)
        self.tabScanControl.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Confocal)
        Confocal.setTabOrder(self.txtStartX, self.txtEndX)
        Confocal.setTabOrder(self.txtEndX, self.txtStepX)
        Confocal.setTabOrder(self.txtStepX, self.txtStartY)
        Confocal.setTabOrder(self.txtStartY, self.txtEndY)
        Confocal.setTabOrder(self.txtEndY, self.txtStepY)
        Confocal.setTabOrder(self.txtStepY, self.txtZcom)
        Confocal.setTabOrder(self.txtZcom, self.txtStep)
        Confocal.setTabOrder(self.txtStep, self.pbZup)
        Confocal.setTabOrder(self.pbZup, self.pbZdown)
        Confocal.setTabOrder(self.pbZdown, self.pbStart)
        Confocal.setTabOrder(self.pbStart, self.pbStop)
        Confocal.setTabOrder(self.pbStop, self.txtXcom)
        Confocal.setTabOrder(self.txtXcom, self.pbXleft)
        Confocal.setTabOrder(self.pbXleft, self.pbXright)
        Confocal.setTabOrder(self.pbXright, self.txtYcom)
        Confocal.setTabOrder(self.txtYcom, self.pbYup)
        Confocal.setTabOrder(self.pbYup, self.pbYdown)
        Confocal.setTabOrder(self.pbYdown, self.txtX)
        Confocal.setTabOrder(self.txtX, self.txtY)
        Confocal.setTabOrder(self.txtY, self.txtZ)
        Confocal.setTabOrder(self.txtZ, self.pbGoTo)
        Confocal.setTabOrder(self.pbGoTo, self.pbCount)
        Confocal.setTabOrder(self.pbCount, self.pbMax)

    def retranslateUi(self, Confocal):
        _translate = QtCore.QCoreApplication.translate
        Confocal.setWindowTitle(_translate("Confocal", "Confocal Imaging"))
        self.gbHardware.setTitle(_translate("Confocal", "Hardware"))
        self.pbInitHW.setText(_translate("Confocal", "Initialize"))
        self.pbCleanupHW.setText(_translate("Confocal", "Reset"))
        self.gbCounts.setTitle(_translate("Confocal", "Counts"))
        self.pbCount.setText(_translate("Confocal", "On"))
        self.pbMax.setText(_translate("Confocal", "Max"))
        self.cbCountFreq.setItemText(0, _translate("Confocal", "1"))
        self.cbCountFreq.setItemText(1, _translate("Confocal", "2"))
        self.cbCountFreq.setItemText(2, _translate("Confocal", "5"))
        self.cbCountFreq.setItemText(3, _translate("Confocal", "10"))
        self.label_15.setText(_translate("Confocal", "Hz"))
        self.gbCursorControl.setTitle(_translate("Confocal", "Cursor Control"))
        self.pbNewCursor.setText(_translate("Confocal", "New Cursor"))
        self.pbShowCursor.setText(_translate("Confocal", "Show Cursor"))
        self.pbHideCursor.setText(_translate("Confocal", "Hide Cursor"))
        self.gbLaser.setTitle(_translate("Confocal", "Laser"))
        self.pbLaserOn.setText(_translate("Confocal", "On"))
        self.pbLaserOff.setText(_translate("Confocal", "Off"))
        self.gbMove.setTitle(_translate("Confocal", "Move"))
        self.gbMoveXY.setTitle(_translate("Confocal", "X-Y"))
        self.pbYup.setText(_translate("Confocal", "˄"))
        self.pbYdown.setText(_translate("Confocal", "˅"))
        self.pbXright.setText(_translate("Confocal", ">"))
        self.pbXleft.setText(_translate("Confocal", "<"))
        self.gbMoveZ.setTitle(_translate("Confocal", "Z"))
        self.pbZup.setText(_translate("Confocal", "˄"))
        self.pbZdown.setText(_translate("Confocal", "˅"))
        self.pbKeepNV.setText(_translate("Confocal", "KeepNV"))
        self.label_9.setText(_translate("Confocal", "Z Step"))
        self.label_22.setText(_translate("Confocal", "XY Step"))
        self.gbXYScan.setTitle(_translate("Confocal", "XY Scan"))
        self.pbSaveData.setText(_translate("Confocal", "Save Data"))
        self.label_17.setText(_translate("Confocal", "High(log)"))
        self.pbReplot.setText(_translate("Confocal", "Reset Plot"))
        self.label_18.setText(_translate("Confocal", "Low"))
        self.gbZScan.setTitle(_translate("Confocal", "Z Scan"))
        self.pbReplot_ZScan.setText(_translate("Confocal", "Reset Plot"))
        self.pbSaveData_ZScan.setText(_translate("Confocal", "Save Data"))
        self.label_19.setText(_translate("Confocal", "High(log)"))
        self.label_20.setText(_translate("Confocal", "Low"))
        self.gbScan.setTitle(_translate("Confocal", "Scan Parameters"))
        self.gbX.setTitle(_translate("Confocal", "X"))
        self.label.setText(_translate("Confocal", "Start"))
        self.label_4.setText(_translate("Confocal", "Step"))
        self.label_3.setText(_translate("Confocal", "End"))
        self.gbY.setTitle(_translate("Confocal", "Y"))
        self.label_5.setText(_translate("Confocal", "Start"))
        self.label_6.setText(_translate("Confocal", "Step"))
        self.label_7.setText(_translate("Confocal", "End"))
        self.gbZ_2.setTitle(_translate("Confocal", "Z"))
        self.label_24.setText(_translate("Confocal", "Start"))
        self.label_25.setText(_translate("Confocal", "Step"))
        self.label_26.setText(_translate("Confocal", "End"))
        self.gbSpeed.setTitle(_translate("Confocal", "Speed"))
        self.label_16.setText(_translate("Confocal", "Step Frequency (Hz)"))
        self.cbFreq.setItemText(0, _translate("Confocal", "1"))
        self.cbFreq.setItemText(1, _translate("Confocal", "2"))
        self.cbFreq.setItemText(2, _translate("Confocal", "5"))
        self.cbFreq.setItemText(3, _translate("Confocal", "10"))
        self.cbFreq.setItemText(4, _translate("Confocal", "20"))
        self.cbFreq.setItemText(5, _translate("Confocal", "50"))
        self.cbFreq.setItemText(6, _translate("Confocal", "100"))
        self.cbFreq.setItemText(7, _translate("Confocal", "200"))
        self.gbXYScanner.setTitle(_translate("Confocal", "XY Scanner"))
        self.rbGalvo.setText(_translate("Confocal", "Galvo"))
        self.rbPiezo.setText(_translate("Confocal", "Piezo"))
        self.pbStart.setText(_translate("Confocal", "Start"))
        self.label_2.setText(_translate("Confocal", "Range"))
        self.pbStop.setText(_translate("Confocal", "Stop"))
        self.pbSelectRange.setText(_translate("Confocal", "Select Range"))
        self.pbFullRange.setText(_translate("Confocal", "Full Range"))
        self.pbCenter.setText(_translate("Confocal", "Center Cursor"))
        self.txtRange.setText(_translate("Confocal", "10"))
        self.tabScanControl.setTabText(self.tabScanControl.indexOf(self.tabXYScan), _translate("Confocal", "XY Scan"))
        self.pbCenterZ.setText(_translate("Confocal", "Center Cursor"))
        self.pbStartZ.setText(_translate("Confocal", "Start"))
        self.pbSelectRangeZ.setText(_translate("Confocal", "Select Range"))
        self.pbFullRangeZ.setText(_translate("Confocal", "Full Range"))
        self.txtRangeZ.setText(_translate("Confocal", "10"))
        self.label_21.setText(_translate("Confocal", "Range"))
        self.pbStopZ.setText(_translate("Confocal", "Stop"))
        self.tabScanControl.setTabText(self.tabScanControl.indexOf(self.tabZScan), _translate("Confocal", "Z Scan"))
        self.gbActual.setTitle(_translate("Confocal", "Actual"))
        self.label_11.setText(_translate("Confocal", "X"))
        self.label_12.setText(_translate("Confocal", "Y"))
        self.label_14.setText(_translate("Confocal", "Z"))
        self.gbCursor.setTitle(_translate("Confocal", "Cursor"))
        self.label_10.setText(_translate("Confocal", "X"))
        self.label_13.setText(_translate("Confocal", "Y"))
        self.label_8.setText(_translate("Confocal", "Z"))
        self.pbGetPos.setText(_translate("Confocal", "-->"))
        self.groupBox.setTitle(_translate("Confocal", "Position Control"))
        self.pbGoToMid.setText(_translate("Confocal", "Go to Mid"))
        self.pbGoTo.setText(_translate("Confocal", "Go!"))
        self.menuFile.setTitle(_translate("Confocal", "File"))
        self.actionOpen.setText(_translate("Confocal", "Open"))
        self.actionSave_As.setText(_translate("Confocal", "Save As"))
        self.actionSave_Defaults.setText(_translate("Confocal", "Save Defaults"))
        self.actionOpen_Defaults.setText(_translate("Confocal", "Open Defaults"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Confocal = QtWidgets.QMainWindow()
    ui = Ui_Confocal()
    ui.setupUi(Confocal)
    Confocal.show()
    sys.exit(app.exec_())
