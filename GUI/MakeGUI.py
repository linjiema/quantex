"""
This program uses pyuic to transform the "GUI.ui" file into "GUI_RAW" file.
"""
import subprocess
from os import path

directory = path.dirname(path.abspath(__file__))
subprocess.call(["pyuic5", path.join(directory, "GUI.ui"),
                 ">",
                 path.join(directory, "GUI_RAW.py")],
                shell=True)
