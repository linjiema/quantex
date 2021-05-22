import sys
import os.path
import time

import matplotlib.pyplot as plt
import numpy as np
from Hardware import AllHardware
import scipy.optimize

hardware = AllHardware()
hardware.mover.scan_devices()
hardware.mover.open_devices()

# Move all axis to 0.0 point
hardware.mover.move_position_all()

hardware.mover.scanning_setting(channel=1, start_point=0.0, end_point=100.0, line_rate=4)

hardware.triggered_location_sensor.init_task()
hardware.timer.init_task()

hardware.timer.start_timer()
hardware.mover.scanning_single_line(channel=1, start_point=0.0, end_point=100.0, line_rate=4)
hardware.timer.recycle_timer()

pos_arr = hardware.triggered_location_sensor.get_location_data()

x_arr = range(np.size(pos_arr))

print('pos_arr', pos_arr)
plt.plot(x_arr, pos_arr)
plt.title('Time_location Relationship')
plt.xlabel('Time(ms)')
plt.ylabel('Location(um)')
plt.show()

