import numpy as np
import matplotlib.pyplot as plt
import win32ui
from collections import deque

# Using win GUI to choose the file
dlg = win32ui.CreateFileDialog(1)
dlg.SetOFNInitialDir('C:/Users/Desktop')
dlg.DoModal()

# Get the file dir and name
filename = dlg.GetPathName()
path = dlg.GetPathName()
print('File name = ', filename)
print('Path name = ', path)

# Load the data
with open(path, 'r') as file_raw_data:
    raw_data = file_raw_data.readlines()
    x_arr = []
    y_arr = []
    count_arr = []
    for lines in raw_data:
        data_arr = lines.split()
        x_arr.append(round(float(data_arr[0]), 3))
        y_arr.append(round(float(data_arr[1]), 3))
        count_arr.append(float(data_arr[2]))

# Split the data based on Y value
diff_y = np.diff(y_arr)
index_nonzero = np.where(diff_y)
index_nonzero_deq = deque(index_nonzero)
index_nonzero_deq.appendleft(0)


for i in range(np.size(index_nonzero)):

#print(x_arr)
#print(np.size(y_arr_deq_origin))
#print('new = ', np.size(y_arr_deq_new))
print(diff_y)
print(index_nonzero)
print(np.size(index_nonzero))
#print('y_arr_deq_new = ', y_arr_deq_new)
#print(count_arr)
