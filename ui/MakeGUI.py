"""
This program uses pyuic to transform the "xxx.ui" file into "xxx.py" file.
"""
import subprocess
import os
from os import path

directory = path.dirname(path.abspath(__file__))

ui_dir = path.join(directory, "ui_files")
uipy_dir = path.join(directory, "uipy")


for root, dirs, files in os.walk(ui_dir):
    for file in files:
        if file.endswith(".ui"):
            ui_file_path = path.join(root, file)
            # Get the relative path of the .ui file from the ui_files directory
            relative_path = path.relpath(ui_file_path, ui_dir)
            # Construct the output file path in the uipy directory, replacing .ui with UI.py
            output_file_relative = path.splitext(relative_path)[0] + ".py"
            output_file_path = path.join(uipy_dir, output_file_relative)
            # Ensure the output directory exists
            output_dir = path.dirname(output_file_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            # Call pyuic5 to generate the .py file
            subprocess.call(["pyuic5", ui_file_path, "-o", output_file_path])
