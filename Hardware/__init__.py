"""
This file used to list all the hardware we use.
"""

from Hardware.XMT_E70D4 import XMT

class AllHardware():
    def __init__(self):
        self.mover = XMT()

    def cleanup(self):
        pass