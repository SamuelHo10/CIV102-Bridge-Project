import numpy as np
from calculate import x
# import matplotlib.pyplot as plt
import sympy.plotting as plt 
import sympy as sy

### Add functions to generate graphs here ###

def plot_piecewise(f):
    # x = sy.Symbol("x", real=True)
    # x_array = np.linspace(-5, 5, 1000)
    # f_array = sy.lambdify(x, f)(x_array)
    print(f)
    plt.plot( f, (x, 0,16))


def line_graph(x_axis, y_axis, x_axis_label="x", y_axis_label="y", invert_y=False, save_path="graph.png"):
    plt.plot(x_axis, y_axis)
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    if invert_y:
        ax = plt.gca()
        ax.invert_yaxis()
    plt.savefig(save_path)
    plt.show()
