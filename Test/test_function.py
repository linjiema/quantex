import random

import numpy as np
import matplotlib.pyplot as plt

x = np.arange(-10, 10, 0.01)

x_real = (x + 10) * 5

y = 1/(1 + np.exp(-x))

y_real = y * 80

countsArr = []

for i in range(np.size(x_real)):
    temp = random.random() * 10
    countsArr.append(temp)

x_location = np.arange(0, 80, 0.8).tolist()
x_location.append(80)

selected_counts = []

for x_pos in x_location:
    x_pos_arr = np.array([x_pos] * np.size(x_real))
    diff_arr = list(np.abs(x_pos_arr-x_real))
    closeIndex = diff_arr.index(min(diff_arr))

    selected_counts.append(countsArr[closeIndex])


plt.plot(x_real, y_real)
plt.show()
plt.plot(x_location, selected_counts)
plt.show()

