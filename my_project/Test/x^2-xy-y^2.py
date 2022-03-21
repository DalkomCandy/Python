import matplotlib.pyplot as plt
import numpy as np

x = -2
x_val = []
y_val = []
z_val = []
while x < 2:
    if (1-(3/4)*x**2) < 0:
        pass
    else:
        y = np.sqrt(1-(3/4)*(x**2)) + (1/2)*x
        z = -1 * np.sqrt(1-(3/4)*(x**2)) + (1/2)*x
        x_val.append(x)
        y_val.append(y)
        z_val.append(z)

    x += 0.00001

plt.plot(x_val, y_val)
plt.plot(x_val, z_val)
plt.show()