import random

import numpy as np
import matplotlib.pyplot as plt
from collections import deque

x = np.array([1,2,3,4,5,6,7,8,9,0])
y = x[np.where((x < 7) & (x > 5))]
print(y)

