import numpy as np
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use('fivethirtyeight')
x_val = []
y_val = []
z_val = []

def animate(index = -100):
    index += 1
    x = index
    x_val.append(x)
    y_val.append(np.sqrt(x**3 + 109*x**2+224*x))
    z_val.append(-1*np.sqrt(x**3 + 109*x**2+224*x))
    plt.cla()
    plt.plot(x_val, y_val)
    plt.plot(x_val, z_val)

ani = FuncAnimation(plt.gcf(), animate)
plt.tight_layout()
plt.show()