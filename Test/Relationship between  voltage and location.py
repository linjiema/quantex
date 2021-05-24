import sys
import os.path
import time

import matplotlib.pyplot as plt
import numpy as np
from Hardware import AllHardware
import scipy.optimize

x_start = 0.0
x_end = 100.0
x_arr = list(np.arange(0.0, 100.0, 0.1))
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

    time.sleep(1)

    hardware.timer.start_timer()

    temp_location_arr = hardware.triggered_location_sensor.get_location_raw_data()
    hardware.timer.recycle_timer()

    print('Finish sample location', x_points)

    mean_temp = np.mean(temp_location_arr)
    std_temp = np.std(temp_location_arr)

    vol_mean.append(mean_temp)
    vol_std.append(std_temp)

print('location: ', x_arr)
print('Voltage: ', vol_mean)
print('Std: ', vol_std)

p0 = [np.max(x_arr)/np.max(vol_mean), 0]
val, cov = scipy.optimize.curve_fit(lambda x, a, b: a * x + b, vol_mean, x_arr, p0)
print('val = ', val)

write_list = []
for i in range(np.size(x_arr)):
    write_list.append((x_arr[i], vol_mean[i], vol_std[i]))
os.chdir(os.path.dirname(__file__) + '/Results')
f = open("location_voltage_table.txt", "w")
f.write('The fitted function is' + 'y = ' + str(val[0]) + 'x + ' + str(val[1]) + '\n')
f.write('location(um) \t voltage_mean(V) \t voltage_std(V) \n')
for points in write_list:
    f.write(str(points[0]) + '\t' + str(points[1]) + '\t' + str(points[2]) + '\n')
f.close()


plt.title('Relation of Position-Voltage')
plt.errorbar(x_arr, vol_mean, color='blue', marker='o', linestyle='none', linewidth=1, markersize=0.5, yerr=vol_std)
plt.xlabel('Location(um)')
plt.ylabel('Voltage value(V)')
plt.show()
