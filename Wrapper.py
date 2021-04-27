"""
This is the program that link the program with GUI
"""
import os, os.path, numpy, time
from PyQt5 import QtWidgets, QtCore
from matplotlib import cm
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from collections import deque

from GUI.GUI import Ui_MainWindow
from Threads import ConfocalScanThread
from Hardware import AllHardware