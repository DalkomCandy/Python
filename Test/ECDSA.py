import numpy as np
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def animate():
    x_val = []
    y_val = []
    z_val = []
    for x in range(-200, 100, 1):
        k = x**3 + 109*x**2+224*x
        if k < 0:
            x_val.append(x)
            y_val.append(0)
            z_val.append(0)
        else:
            y = np.sqrt(k)
            z = -1 * np.sqrt(k)
            x_val.append(x)
            y_val.append(y)
            z_val.append(z)
            print(x, y, z)

    return x_val, y_val, z_val

x, y, z = animate()
plt.plot(x, y)
plt.plot(x, z)
plt.show()