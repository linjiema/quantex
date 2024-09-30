# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\eee\PycharmProjects\afm-confocal\ui\ui_files\mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(742, 716)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gbDataProcessing = QtWidgets.QGroupBox(self.centralwidget)
        self.gbDataProcessing.setObjectName("gbDataProcessing")
        self.gridLayout_12 = QtWidgets.QGridLayout(self.gbDataProcessing)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.pbDP_confocal = QtWidgets.QPushButton(self.gbDataProcessing)
        self.pbDP_confocal.setObjectName("pbDP_confocal")
        self.gridLayout_12.addWidget(self.pbDP_confocal, 0, 0, 1, 1)
        self.pbDP_ESR = QtWidgets.QPushButton(self.gbDataProcessing)
        self.pbDP_ESR.setObjectName("pbDP_ESR")
        self.gridLayout_12.addWidget(self.pbDP_ESR, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.gbDataProcessing, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 1, 1, 1, 1)
        self.gbExperiment = QtWidgets.QGroupBox(self.centralwidget)
        self.gbExperiment.setObjectName("gbExperiment")
        self.gridLayout_11 = QtWidgets.QGridLayout(self.gbExperiment)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.pbExpConfocal = QtWidgets.QPushButton(self.gbExperiment)
        self.pbExpConfocal.setObjectName("pbExpConfocal")
        self.gridLayout_11.addWidget(self.pbExpConfocal, 0, 0, 1, 1)
        self.pbExpESR = QtWidgets.QPushButton(self.gbExperiment)
        self.pbExpESR.setObjectName("pbExpESR")
        self.gridLayout_11.addWidget(self.pbExpESR, 1, 0, 1, 1)
        self.pbExpRotation = QtWidgets.QPushButton(self.gbExperiment)
        self.pbExpRotation.setObjectName("pbExpRotation")
        self.gridLayout_11.addWidget(self.pbExpRotation, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.gbExperiment, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 3, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 742, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.Device_Manager = QtWidgets.QDockWidget(MainWindow)
        self.Device_Manager.setFocusPolicy(QtCore.Qt.TabFocus)
        self.Device_Manager.setObjectName("Device_Manager")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gbPiezo = QtWidgets.QGroupBox(self.dockWidgetContents_2)
        self.gbPiezo.setObjectName("gbPiezo")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gbPiezo)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pbPiezoInit = QtWidgets.QPushButton(self.gbPiezo)
        self.pbPiezoInit.setObjectName("pbPiezoInit")
        self.gridLayout_3.addWidget(self.pbPiezoInit, 0, 3, 1, 1)
        self.rbPiezoConnect = QtWidgets.QRadioButton(self.gbPiezo)
        self.rbPiezoConnect.setEnabled(False)
        self.rbPiezoConnect.setCheckable(True)
        self.rbPiezoConnect.setObjectName("rbPiezoConnect")
        self.gridLayout_3.addWidget(self.rbPiezoConnect, 0, 0, 1, 1)
        self.rbPiezoDisconnect = QtWidgets.QRadioButton(self.gbPiezo)
        self.rbPiezoDisconnect.setEnabled(False)
        self.rbPiezoDisconnect.setCheckable(True)
        self.rbPiezoDisconnect.setChecked(True)
        self.rbPiezoDisconnect.setObjectName("rbPiezoDisconnect")
        self.gridLayout_3.addWidget(self.rbPiezoDisconnect, 0, 1, 1, 1)
        self.pbPiezoReset = QtWidgets.QPushButton(self.gbPiezo)
        self.pbPiezoReset.setEnabled(False)
        self.pbPiezoReset.setCheckable(False)
        self.pbPiezoReset.setChecked(False)
        self.pbPiezoReset.setObjectName("pbPiezoReset")
        self.gridLayout_3.addWidget(self.pbPiezoReset, 0, 4, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem2, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.gbPiezo, 0, 1, 1, 1)
        self.gbPulseGenerator = QtWidgets.QGroupBox(self.dockWidgetContents_2)
        self.gbPulseGenerator.setObjectName("gbPulseGenerator")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.gbPulseGenerator)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.pbPulseGenInit = QtWidgets.QPushButton(self.gbPulseGenerator)
        self.pbPulseGenInit.setObjectName("pbPulseGenInit")
        self.gridLayout_6.addWidget(self.pbPulseGenInit, 0, 3, 1, 1)
        self.rbPulseGenConnect = QtWidgets.QRadioButton(self.gbPulseGenerator)
        self.rbPulseGenConnect.setEnabled(False)
        self.rbPulseGenConnect.setCheckable(True)
        self.rbPulseGenConnect.setObjectName("rbPulseGenConnect")
        self.gridLayout_6.addWidget(self.rbPulseGenConnect, 0, 0, 1, 1)
        self.pbPulseGenReset = QtWidgets.QPushButton(self.gbPulseGenerator)
        self.pbPulseGenReset.setEnabled(False)
        self.pbPulseGenReset.setCheckable(False)
        self.pbPulseGenReset.setChecked(False)
        self.pbPulseGenReset.setObjectName("pbPulseGenReset")
        self.gridLayout_6.addWidget(self.pbPulseGenReset, 0, 4, 1, 1)
        self.rbPulseGenDisconnect = QtWidgets.QRadioButton(self.gbPulseGenerator)
        self.rbPulseGenDisconnect.setEnabled(False)
        self.rbPulseGenDisconnect.setCheckable(True)
        self.rbPulseGenDisconnect.setChecked(True)
        self.rbPulseGenDisconnect.setObjectName("rbPulseGenDisconnect")
        self.gridLayout_6.addWidget(self.rbPulseGenDisconnect, 0, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem3, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.gbPulseGenerator, 3, 1, 1, 1)
        self.gbTimetagger = QtWidgets.QGroupBox(self.dockWidgetContents_2)
        self.gbTimetagger.setObjectName("gbTimetagger")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.gbTimetagger)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.pbTaggerInit = QtWidgets.QPushButton(self.gbTimetagger)
        self.pbTaggerInit.setObjectName("pbTaggerInit")
        self.gridLayout_7.addWidget(self.pbTaggerInit, 0, 3, 1, 1)
        self.pbTaggerReset = QtWidgets.QPushButton(self.gbTimetagger)
        self.pbTaggerReset.setEnabled(False)
        self.pbTaggerReset.setCheckable(False)
        self.pbTaggerReset.setChecked(False)
        self.pbTaggerReset.setObjectName("pbTaggerReset")
        self.gridLayout_7.addWidget(self.pbTaggerReset, 0, 4, 1, 1)
        self.rbTaggerDisconnect = QtWidgets.QRadioButton(self.gbTimetagger)
        self.rbTaggerDisconnect.setEnabled(False)
        self.rbTaggerDisconnect.setCheckable(True)
        self.rbTaggerDisconnect.setChecked(True)
        self.rbTaggerDisconnect.setObjectName("rbTaggerDisconnect")
        self.gridLayout_7.addWidget(self.rbTaggerDisconnect, 0, 1, 1, 1)
        self.rbTaggerConnect = QtWidgets.QRadioButton(self.gbTimetagger)
        self.rbTaggerConnect.setEnabled(False)
        self.rbTaggerConnect.setCheckable(True)
        self.rbTaggerConnect.setObjectName("rbTaggerConnect")
        self.gridLayout_7.addWidget(self.rbTaggerConnect, 0, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem4, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.gbTimetagger, 4, 1, 1, 1)
        self.gbMW = QtWidgets.QGroupBox(self.dockWidgetContents_2)
        self.gbMW.setObjectName("gbMW")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.gbMW)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.rbMWConnect = QtWidgets.QRadioButton(self.gbMW)
        self.rbMWConnect.setEnabled(False)
        self.rbMWConnect.setCheckable(True)
        self.rbMWConnect.setObjectName("rbMWConnect")
        self.gridLayout_9.addWidget(self.rbMWConnect, 0, 0, 1, 1)
        self.pbMWInit = QtWidgets.QPushButton(self.gbMW)
        self.pbMWInit.setObjectName("pbMWInit")
        self.gridLayout_9.addWidget(self.pbMWInit, 0, 3, 1, 1)
        self.rbMWDisconnect = QtWidgets.QRadioButton(self.gbMW)
        self.rbMWDisconnect.setEnabled(False)
        self.rbMWDisconnect.setCheckable(True)
        self.rbMWDisconnect.setChecked(True)
        self.rbMWDisconnect.setObjectName("rbMWDisconnect")
        self.gridLayout_9.addWidget(self.rbMWDisconnect, 0, 1, 1, 1)
        self.pbMWReset = QtWidgets.QPushButton(self.gbMW)
        self.pbMWReset.setEnabled(False)
        self.pbMWReset.setCheckable(False)
        self.pbMWReset.setChecked(False)
        self.pbMWReset.setObjectName("pbMWReset")
        self.gridLayout_9.addWidget(self.pbMWReset, 0, 4, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem5, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.gbMW, 6, 1, 1, 1)
        self.gbRotationStage = QtWidgets.QGroupBox(self.dockWidgetContents_2)
        self.gbRotationStage.setObjectName("gbRotationStage")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.gbRotationStage)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.rbRotatorDisconnect = QtWidgets.QRadioButton(self.gbRotationStage)
        self.rbRotatorDisconnect.setEnabled(False)
        self.rbRotatorDisconnect.setCheckable(True)
        self.rbRotatorDisconnect.setChecked(True)
        self.rbRotatorDisconnect.setObjectName("rbRotatorDisconnect")
        self.gridLayout_10.addWidget(self.rbRotatorDisconnect, 0, 1, 1, 1)
        self.rbRotaotrConnect = QtWidgets.QRadioButton(self.gbRotationStage)
        self.rbRotaotrConnect.setEnabled(False)
        self.rbRotaotrConnect.setCheckable(True)
        self.rbRotaotrConnect.setObjectName("rbRotaotrConnect")
        self.gridLayout_10.addWidget(self.rbRotaotrConnect, 0, 0, 1, 1)
        self.pbRotatorReset = QtWidgets.QPushButton(self.gbRotationStage)
        self.pbRotatorReset.setEnabled(False)
        self.pbRotatorReset.setCheckable(False)
        self.pbRotatorReset.setChecked(False)
        self.pbRotatorReset.setObjectName("pbRotatorReset")
        self.gridLayout_10.addWidget(self.pbRotatorReset, 0, 4, 1, 1)
        self.pbRotatorInit = QtWidgets.QPushButton(self.gbRotationStage)
        self.pbRotatorInit.setObjectName("pbRotatorInit")
        self.gridLayout_10.addWidget(self.pbRotatorInit, 0, 3, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_10.addItem(spacerItem6, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.gbRotationStage, 9, 1, 1, 1)
        self.gbNIdaq = QtWidgets.QGroupBox(self.dockWidgetContents_2)
        self.gbNIdaq.setObjectName("gbNIdaq")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.gbNIdaq)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.rbDaqDisconnect = QtWidgets.QRadioButton(self.gbNIdaq)
        self.rbDaqDisconnect.setEnabled(False)
        self.rbDaqDisconnect.setCheckable(True)
        self.rbDaqDisconnect.setChecked(True)
        self.rbDaqDisconnect.setObjectName("rbDaqDisconnect")
        self.gridLayout_8.addWidget(self.rbDaqDisconnect, 0, 1, 1, 1)
        self.pbDaqReset = QtWidgets.QPushButton(self.gbNIdaq)
        self.pbDaqReset.setEnabled(False)
        self.pbDaqReset.setCheckable(False)
        self.pbDaqReset.setChecked(False)
        self.pbDaqReset.setObjectName("pbDaqReset")
        self.gridLayout_8.addWidget(self.pbDaqReset, 0, 4, 1, 1)
        self.pbDaqInit = QtWidgets.QPushButton(self.gbNIdaq)
        self.pbDaqInit.setObjectName("pbDaqInit")
        self.gridLayout_8.addWidget(self.pbDaqInit, 0, 3, 1, 1)
        self.rbDaqConnect = QtWidgets.QRadioButton(self.gbNIdaq)
        self.rbDaqConnect.setEnabled(False)
        self.rbDaqConnect.setCheckable(True)
        self.rbDaqConnect.setObjectName("rbDaqConnect")
        self.gridLayout_8.addWidget(self.rbDaqConnect, 0, 0, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_8.addItem(spacerItem7, 0, 2, 1, 1)
        self.gridLayout_4.addWidget(self.gbNIdaq, 5, 1, 1, 1)
        self.gbGalvo = QtWidgets.QGroupBox(self.dockWidgetContents_2)
        self.gbGalvo.setObjectName("gbGalvo")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.gbGalvo)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pbGalvoReset = QtWidgets.QPushButton(self.gbGalvo)
        self.pbGalvoReset.setEnabled(False)
        self.pbGalvoReset.setCheckable(False)
        self.pbGalvoReset.setChecked(False)
        self.pbGalvoReset.setObjectName("pbGalvoReset")
        self.gridLayout_5.addWidget(self.pbGalvoReset, 1, 4, 1, 1)
        self.pbGalvoInit = QtWidgets.QPushButton(self.gbGalvo)
        self.pbGalvoInit.setObjectName("pbGalvoInit")
        self.gridLayout_5.addWidget(self.pbGalvoInit, 1, 3, 1, 1)
        self.rbGalvoConnect = QtWidgets.QRadioButton(self.gbGalvo)
        self.rbGalvoConnect.setEnabled(False)
        self.rbGalvoConnect.setCheckable(True)
        self.rbGalvoConnect.setObjectName("rbGalvoConnect")
        self.gridLayout_5.addWidget(self.rbGalvoConnect, 1, 0, 1, 1)
        self.rbGalvoDisconnect = QtWidgets.QRadioButton(self.gbGalvo)
        self.rbGalvoDisconnect.setEnabled(False)
        self.rbGalvoDisconnect.setCheckable(True)
        self.rbGalvoDisconnect.setChecked(True)
        self.rbGalvoDisconnect.setObjectName("rbGalvoDisconnect")
        self.gridLayout_5.addWidget(self.rbGalvoDisconnect, 1, 1, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem8, 1, 2, 1, 1)
        self.gridLayout_4.addWidget(self.gbGalvo, 2, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem9)
        self.pbInitAll = QtWidgets.QPushButton(self.dockWidgetContents_2)
        self.pbInitAll.setObjectName("pbInitAll")
        self.horizontalLayout.addWidget(self.pbInitAll)
        self.pbResetAll = QtWidgets.QPushButton(self.dockWidgetContents_2)
        self.pbResetAll.setEnabled(False)
        self.pbResetAll.setObjectName("pbResetAll")
        self.horizontalLayout.addWidget(self.pbResetAll)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem10)
        self.gridLayout_4.addLayout(self.horizontalLayout, 11, 1, 1, 1)
        spacerItem11 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem11, 10, 1, 1, 1)
        spacerItem12 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem12, 13, 1, 1, 1)
        self.Device_Manager.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.Device_Manager)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.gbDataProcessing.setTitle(_translate("MainWindow", "Data Processing"))
        self.pbDP_confocal.setText(_translate("MainWindow", "Confocal Image"))
        self.pbDP_ESR.setText(_translate("MainWindow", "ESR"))
        self.gbExperiment.setTitle(_translate("MainWindow", "Experiment Interface"))
        self.pbExpConfocal.setText(_translate("MainWindow", "Confocal"))
        self.pbExpESR.setText(_translate("MainWindow", "ESR"))
        self.pbExpRotation.setText(_translate("MainWindow", "Rotation"))
        self.Device_Manager.setWindowTitle(_translate("MainWindow", "Device Manager"))
        self.gbPiezo.setTitle(_translate("MainWindow", "Piezo Stage"))
        self.pbPiezoInit.setText(_translate("MainWindow", "Init"))
        self.rbPiezoConnect.setText(_translate("MainWindow", "Connected"))
        self.rbPiezoDisconnect.setText(_translate("MainWindow", "Disconnected"))
        self.pbPiezoReset.setText(_translate("MainWindow", "Reset"))
        self.gbPulseGenerator.setTitle(_translate("MainWindow", "Pulse Generator"))
        self.pbPulseGenInit.setText(_translate("MainWindow", "Init"))
        self.rbPulseGenConnect.setText(_translate("MainWindow", "Connected"))
        self.pbPulseGenReset.setText(_translate("MainWindow", "Reset"))
        self.rbPulseGenDisconnect.setText(_translate("MainWindow", "Disconnected"))
        self.gbTimetagger.setTitle(_translate("MainWindow", "Timetagger20"))
        self.pbTaggerInit.setText(_translate("MainWindow", "Init"))
        self.pbTaggerReset.setText(_translate("MainWindow", "Reset"))
        self.rbTaggerDisconnect.setText(_translate("MainWindow", "Disconnected"))
        self.rbTaggerConnect.setText(_translate("MainWindow", "Connected"))
        self.gbMW.setTitle(_translate("MainWindow", "Microwave Source ---- SynthNVPro"))
        self.rbMWConnect.setText(_translate("MainWindow", "Connected"))
        self.pbMWInit.setText(_translate("MainWindow", "Init"))
        self.rbMWDisconnect.setText(_translate("MainWindow", "Disconnected"))
        self.pbMWReset.setText(_translate("MainWindow", "Reset"))
        self.gbRotationStage.setTitle(_translate("MainWindow", "Rotation Stage ---- EM_CV5_1"))
        self.rbRotatorDisconnect.setText(_translate("MainWindow", "Disconnected"))
        self.rbRotaotrConnect.setText(_translate("MainWindow", "Connected"))
        self.pbRotatorReset.setText(_translate("MainWindow", "Reset"))
        self.pbRotatorInit.setText(_translate("MainWindow", "Init"))
        self.gbNIdaq.setTitle(_translate("MainWindow", "NI DAQ"))
        self.rbDaqDisconnect.setText(_translate("MainWindow", "Disconnected"))
        self.pbDaqReset.setText(_translate("MainWindow", "Reset"))
        self.pbDaqInit.setText(_translate("MainWindow", "Init"))
        self.rbDaqConnect.setText(_translate("MainWindow", "Connected"))
        self.gbGalvo.setTitle(_translate("MainWindow", "Galvo Mirror"))
        self.pbGalvoReset.setText(_translate("MainWindow", "Reset"))
        self.pbGalvoInit.setText(_translate("MainWindow", "Init"))
        self.rbGalvoConnect.setText(_translate("MainWindow", "Connected"))
        self.rbGalvoDisconnect.setText(_translate("MainWindow", "Disconnected"))
        self.pbInitAll.setText(_translate("MainWindow", "Init All Device"))
        self.pbResetAll.setText(_translate("MainWindow", "Reset All Device"))