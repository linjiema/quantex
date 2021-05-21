import sys
import os.path
import time

import matplotlib.pyplot as plt
import numpy as np
from Hardware import AllHardware
import scipy.optimize

x_start = 0.0
x_end = 100.0
x_arr = list(np.arange(0.0, 100.0, 1.0))
x_arr.append(100.0)


vol_mean = []
vol_std = []

hardware = AllHardware()
hardware.mover.scan_devices()
hardware.mover.open_devices()

for x_points in x_arr:
    hardware.mover.move_position_single(channel=1, location=x_points)

    hardware.triggered_location_sensor.init_task()
    hardware.timer.init_task()

    time.sleep(0.1)

    hardware.timer.start_timer()

    temp_location_arr = hardware.triggered_location_sensor.get_location_raw_data()
    print('Finish sample location', x_points)

    mean_temp = np.mean(temp_location_arr)
    std_temp = np.std(temp_location_arr)

    vol_mean.append(mean_temp)
    vol_std.append(std_temp)

print('location: ', x_arr)
print('Voltage: ', vol_mean)
print('Std: ', vol_std)

def func(x,a,b):
    return a*x + b
p0=[np.max(x_arr)/np.max(vol_mean), 0]
val, cov = scipy.optimize.curve_fit(func,vol_mean,x_arr,p0)
print(val)

plt.title('Relation of Position-Voltage')
plt.errorbar(x_arr, vol_mean, yerr=vol_std)
plt.show()
#AllHardware.mover.move_position_single(channel=1, location=x_start)
